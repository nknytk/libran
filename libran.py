# coding: utf-8

import imp
import json
import os
import sys
import traceback
from time import sleep, time
from threading import Thread

this_dir = os.path.abspath(os.path.dirname(__file__))


class Libran:
    def __init__(self, config_file=None):
        if config_file is None:
            config_file = os.path.join(this_dir, 'config.json')
        with open(config_file) as fp:
            self.config = json.load(fp)

        self.message_in = self.get_instance(self.config['message_in'])
        self.message_out = self.get_instance(self.config['message_out'])
        self.camera = self.get_instance(self.config['camera'])
        self.image_processor = self.get_instance(self.config['image_processor'])
        self.message_processor = self.get_instance(self.config['message_processor'])
        self.notifier = self.get_instance(self.config['notification'])
        self.storage = self.get_instance(self.config['storage'])

        self.answer = None
        self.command_to_exec = 'idle'
        self.command_thread = Thread(target=self.exec)
        self.command_thread.start()
        self.should_cancel = False

    def get_instance(self, config):
        mod_name, cls_name = config['class'].split('.')
        src = os.path.join(this_dir, 'lib', mod_name + '.py')
        mod = imp.load_source(mod_name, src)
        cls = getattr(mod, cls_name)
        return cls(config)

    def exec(self):
        while True:
            if self.command_to_exec == 'idle':
                sleep(0.1)
                continue
            if self.command_to_exec == 'stop':
                break

            if self.command_to_exec == 'user_registoration':
                self.register_user()
            elif self.command_to_exec == 'book_registoration':
                self.register_book()
            elif self.command_to_exec == 'borrow_book':
                self.borrow_book()
            elif self.command_to_exec == 'return_book':
                self.return_book()
            elif self.command_to_exec == 'photo':
                self.take_photo()
            elif self.command_to_exec == 'train':
                self.train()
            elif self.command_to_exec == 'kill':
                self.stop()

            self.command_to_exec = 'idle'

    def register_user(self):
        self.message_out.talk('新規ユーザーを登録します。')

        datasets_to_commit = []
        while True:

            new_dataset = self.storage.new_dir('user')
            name = None
            response = self.ask('お名前を教えてください。')
            while name is None:
                if response is None:
                    response = self.ask('すみません、お名前をよく聞き取れませんでした。もう一度教えてください。')
                    continue

                words, msg = response
                command = self.message_processor.map_to_command(msg, words)
                if command == 'cancel' or self.should_cancel:
                    self.prepare_cancel('ユーザー登録を中断します')
                    return

                name = self.message_processor.remove_prefix(msg, ('私は', '僕は', '俺は'))
                name = self.message_processor.remove_suffix(msg, ('です', 'だよ'))

                confirm_name = self.ask_yes_no('お名前は、{}さんですね?'.format(name))
                if confirm_name == 'yes':
                    new_dataset.save_text('name.txt', name)
                elif confirm_name == 'no':
                    name = None
                    response = None
                elif confirm_name == 'cancel':
                    self.prepare_cancel('ユーザー登録を中断します')
                    return

            self.message_out.talk('9枚の写真を撮ります。ご協力ください。')

            operations = [
                ('front1', 'まず、カメラを向いてください'),
                ('smile', '笑ってください'),
                ('anger', '怒ってください'),
                ('cry', '泣いてください'),
                ('down', '少しだけ下を向いてください'),
                ('up', '少しだけ上を向いてください'),
                ('left', '少しだけ左を向いてください'),
                ('right', '少しだけ右を向いてください'),
                ('front2', '最後に、もう一度カメラを向いてください'),
            ]

            for tag, msg in operations:
                if self.should_cancel:
                    self.prepare_cancel('ユーザー登録を中断します')
                    return

                self.message_out.talk(msg)
                sleep(1)
                remaining_retry = 2
                img = None
                face_rect = None
                while True:
                    print(tag, remaining_retry)
                    img = self.camera.capture()
                    img_gray_blured = self.image_processor.blur(self.image_processor.gray(img))
                    face_rect = self.image_processor.face_rect(img_gray_blured)

                    if face_rect is not None:
                        break

                    if remaining_retry == 0:
                        self.message_out.talk('顔を認識できませんでした。管理者に問い合わせてください')
                        new_dataset.save_img(tag + '.jpg', img)
                        return
                    else:
                        remaining_retry -= 1

                new_dataset.save_img(tag + '.jpg', img)
                new_dataset.save_img(tag + '_face.jpg', self.image_processor.clip(img, face_rect, resize_to=(100, 100)))

            datasets_to_commit.append(new_dataset)

            self.message_out.talk(name + 'さんの登録を受け付けました。')
            to_continue = self.ask_yes_no('他のユーザーも登録しますか?')
            if to_continue == 'yes':
                continue
            elif to_continue == 'no':
                break
            elif to_continue == 'cancel':
                self.prepare_cancel('ユーザー登録を中断します')

        for dataset in datasets_to_commit:
            dataset.commit()
        self.message_out.push('登録を受け付けました。ご協力、ありがとうございました')

        self.train()

    def train(self):
        self.message_out.push('今からしばらく勉強します')
        self.image_processor.train_face()
        self.message_out.push('勉強が終わりました')

    def register_book(self):
        self.message_out.talk('本を登録します。未実装です')

    def borrow_book(self):
        if self.image_processor.face_classifier is None:
            self.message_out.talk('ユーザーが登録されていないため、受け付けできません')
            return

        self.message_out.talk('貸し出しを受付けます。本を持ってカメラの前に立ってください。')
        sleep(2)
        info = self.rental_info()
        if not info:
            return

        data_dir = self.storage.new_dir('rental')
        data_dir.save_img(str(info['user_id']) + '.jpg', info['img'])
        data_dir.commit()
        self.message_out.push(info['user_name'] + 'さんへの本の貸し出しを受け付けました')
        self.notifier.notify('貸し出し', info['user_name'] + 'さんが本を借りました', data_dir.files())

    def return_book(self):
        if self.image_processor.face_classifier is None:
            self.message_out.talk('ユーザーが登録されていないため、受け付けできません')
            return
        self.message_out.talk('返却を受付けます。本を持ってカメラの前に立ってください。')

    def rental_info(self):
        max_try = 3
        for i in range(max_try):
            img = self.camera.capture()
            img_gray_blured = self.image_processor.blur(self.image_processor.gray(img))
            face_rect = self.image_processor.face_rect(img_gray_blured)
            if face_rect is None:
                self.message_out.talk('顔を特定できません。カメラの位置を調整してください。')
                continue

            face_img = self.image_processor.clip(img, face_rect)
            user_id = self.image_processor.who_is(face_img)

            book_rect = self.image_processor.book_rect(img_gray_blured, face_rect)
            if book_rect is None:
                if i < max_try - 1:
                    self.message_out.talk('本を特定できません。本の位置を調整してください')
                    continue
                else:
                    self.message_out.push('本を特定できませんでした。')

            self.image_processor.add_rect(img, face_rect, (255, 0, 0))  # 顔を青で囲う
            if book_rect is not None:
                self.image_processor.add_rect(img, book_rect, (0, 0, 255))  # 本を赤で囲う
            with open(os.path.join(this_dir, 'data/user', str(user_id), 'name.txt')) as fp:
                name = fp.read()
            return {'user_id': user_id, 'user_name': name, 'img': img}

        self.message_out.talk('処理に失敗しました')
        return {}

    def take_photo(self):
        dataset = self.storage.new_dir('user')

        n_img = 0
        while True:
            self.message_out.talk('写真を撮ります。はい、チーズ')
            img = self.camera.capture()
            dataset.save_img('image_{}.jpg'.format(n_img), img)
            n_img += 1

            to_continue = self.ask_yes_no('もう一枚撮りますか?')
            if to_continue != 'yes':
                break

        self.notifier.notify('写真', '先ほどの写真です', dataset.files())
        self.message_out.push('写真を送りました。確認してください。')
        dataset.clean()

    def ask(self, question, answer_limit=20):
        interrupted_command = self.command_to_exec
        self.command_to_exec = 'ask'
        self.answer = None
        self.message_out.talk(question)

        wait_answer_until = time() + answer_limit
        while time() < wait_answer_until:
            if self.answer:
                break
            sleep(0.1)

        self.command_to_exec = interrupted_command
        return self.answer

    def ask_yes_no(self, question):
        response = self.ask(question)
        while True:
            if response is None:
                response = self.ask('すみません、よく聞き取れませんでした。' + question)
                continue
            command = self.message_processor.map_to_command(*response)
            if command in ('yes', 'no', 'cancel'):
                return command
            else:
                response = self.ask('すみません、よく聞き取れませんでした。' + question)

    def prepare_cancel(self, message):
        self.message_out.clear()
        self.message_out.talk(message)
        self.should_cancel = False

    def start(self):
        self.message_out.talk('おはようございます。何かあったら声をかけてください')
        while self.command_to_exec != 'stop':
            words, msg = self.message_in.listen()
            if not msg:
                sleep(0.1)
                continue

            if self.command_to_exec == 'ask':
                self.answer = (words, msg)
                print(words, msg, self.message_processor.map_to_command(msg, words), self.command_to_exec)
                continue

            print(words, msg, self.message_processor.map_to_command(msg, words), self.command_to_exec)
            command = self.message_processor.map_to_command(msg, words)
            if not command:
                sleep(0.1)
                continue

            if self.command_to_exec == 'idle':
                self.command_to_exec = command

            else:
                if command == 'cancel':
                     self.should_cancel = True
                     continue

    def stop(self):
        really_stop = self.ask('終了しますか?')
        if really_stop is None:
            self.message_out.push('やめておきますね')
            return

        words, msg = really_stop
        command = self.message_processor.map_to_command(msg, words)
        if command == 'yes':
            pass
        elif command == 'no':
            self.message_out.push('このまま働きます。何かあれば呼んでください')
            return
        else:
            self.message_out.talk('すみません、聞き取れませんでした。ひとまずこのまま働きますね')
            return

        self.message_out.talk('終了します')
        self.command_to_exec = 'stop'
        self.message_in.stop()
        self.message_out.talk('おやすみなさい')
        self.message_out.stop()

    def cleanup(self):
        self.command_thread.join()


if __name__ == '__main__':
    libran = Libran()
    try:
        libran.start()
    except Exception as e:
        sys.stderr.write(traceback.format_exc())
        libran.cleanup()
        raise e
    libran.cleanup()
