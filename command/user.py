# coding: utf-8

import os
import sys

this_dir = sys.path.append(os.path.dirname(__file__))
from base import Command

class Register(Command):

    def command(self, *words):
        self.talk('新規ユーザーを登録します。')

        datasets_to_commit = []
        while True:

            # 名前の特定と確認
            name = self._ask_name()
            response = self.ask_with_retry('お名前は、{}さんですね?'.format(name))
            if self.controller.message_processor.is_cancel(response):
                self.cancel()
            if not self.controller.messsage_processor.is_yes(response) == 'yes':
                self.talk('失礼しました。')
                continue

            # ユーザーデータの作成。この時点では一時データ
            new_dataset = self.controller.storage.new_dir('user')
            new_dataset.save_text('name.txt', name)

            # 顔写真をデータに追加
            self._take_photos(new_dataset)

            datasets_to_commit.append(new_dataset)
            self.talk(name + 'さんの登録を受け付けました。')

            to_continue = self.ask_with_retry('他のユーザーも登録しますか?')
            if self.controller.message_processor.is_yes(to_continue):
                continue
            else:
                break

        # これまで取得してきたデータを永続化
        for dataset in datasets_to_commit:
            dataset.commit()
        self.message_out.push('登録を受け付けました。ご協力、ありがとうございました')

        shoud_study_now = self.ask_with_retry('すぐに勉強したほうが良いですか？')
        if self.controller.message_processor.is_yes(shoud_study_now):
            self._train(words)

    def _ask_name(self):
        """ 名前を訊く """
        response = self.ask_with_retry('お名前を教えてください。')
        if self.controller.message_processor.is_cancel(response):
            self.cancel()
        name = self.message_processor.remove_prefix(response, ('私は', '僕は', '俺は'))
        name = self.message_processor.remove_suffix(response, ('です', 'だよ'))
        return name

    def _take_photos(self, dataset):
        """ 角度を変えた９枚の顔写真を撮り、datasetに追加する """

        self.talk('9枚の写真を撮ります。ご協力ください。')

        operations = [
            ('front1', 'まず、カメラを向いてください'),
            ('smile', '笑ってください'),
            ('anger', '怒ってください'),
            ('cry', '泣いてください'),
            ('down', '少しだけ下を向いてください'),
            ('up', '少しだけ上を向いてください'),
            ('left', '少しだけ左を向いてください'),
            ('right', '少しだけ右を向いてください'),
            ('front2', '最後に、もう一度カメラを向いてください')
        ]

        for tag, msg in operations:
            if self.should_cancel:
                self.talk('ユーザー登録を中断します')
                self.cancel()

            self.talk(msg)
            sleep(1)
            remaining_retry = 2
            while True:
                img = self.controller.camera.capture()
                img_gray_blured = self.controller.image_processor.blur(self.image_processor.gray(img))
                face_rect = self.controller.image_processor.face_rect(img_gray_blured)

                if face_rect is not None:
                    break

                if remaining_retry == 0:
                    dataset.save_img(tag + '.jpg', img)
                    break
                else:
                    remaining_retry -= 1

            face_img = self.controller.image_processor.clip(img, face_rect, resize_to(100, 100))
            dataset.save_img(tag + '.jpg', img)
            dataset.save_img(tag + '_face.jpg', face_img)

    def _train(self):
        self.push_message('今からしばらく勉強します')
        self.image_processor.train_face()
        self.push_message('勉強が終わりました')


class FaceStudy(Register):
    def command(self, *messages):
        self._train()
