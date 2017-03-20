# coding: utf-8

import os
import sys
from datetime import datetime
from time import sleep
sys.path.append(os.path.dirname(__file__))
from base import Command


class EquipmentRentalBase(Command):

    def rental_info(self):
        max_try = 3
        for i in range(max_try):
            if self.controller.should_cancel:
                self.cancel()

            img = self.controller.camera.capture()
            img_gray_blured = self.controller.image_processor.blur(self.controller.image_processor.gray(img))
            face_rect = self.controller.image_processor.face_rect(img_gray_blured)
            if face_rect is None:
                self.talk('顔を特定できません。カメラの位置を調整してください。')
                continue

            face_img = self.controller.image_processor.clip(img, face_rect)
            user_id = self.controller.image_processor.who_is(face_img)

            book_rect = self.controller.image_processor.book_rect(img_gray_blured, face_rect)
            if book_rect is None:
                if i < max_try - 1:
                    self.talk('本を特定できません。本の位置を調整してください')
                    continue
                else:
                    self.push_message('本を特定できませんでした。')

            book_img = self.controller.image_processor.clip(img, book_rect)
            orig_img = img.copy()
            self.controller.image_processor.add_rect(img, face_rect, (255, 0, 0))  # 顔を青で囲う
            if book_rect is not None:
                self.controller.image_processor.add_rect(img, book_rect, (0, 0, 255))  # 本を赤で囲う
            name = self.controller.storage.get_name('user', user_id)
            info = {
                'user_id': user_id,
                'user_name': name,
                'img': img,
                'orig_img': orig_img,
                'book_img': book_img
            }
            return info

        return {}


class Register(EquipmentRentalBase):

    def command(self, *words):
        if self.controller.image_processor.face_classifier is None:
            self.talk('ユーザーが登録されていないため、受け付けできません')
            return

        while True:
            self.talk('本を登録するユーザーと、本の写真を撮ります。本を持ってカメラの前に立ってください。')
            while True:
                sleep(5)
                is_ready = self.ask_with_retry('準備はよろしいですか?')
                if self.controller.message_processor.is_cancel(is_ready):
                    self.cancel()
                if self.controller.message_processor.is_yes(is_ready):
                    break

            info = self.rental_info()
            if 'book_img' not in info:
                return

            while True:
                book_name = self.ask_with_retry('本の名前を教えてください')[0]
                if self.controller.message_processor.is_cancel(book_name):
                    self.cancel()
                confirm = self.ask_with_retry('本の名前は、{}でよろしいですか?'.format(book_name))
                if self.controller.message_processor.is_yes(confirm):
                    break
                else:
                    self.talk('失礼しました')

            resized_book = self.controller.image_processor.reisze(info['book_img'], (100, 100))
            dataset = self.controller.storage.new_dir('book')
            dataset.save_img('orig.jpg', info['orig_img'])
            dataset.save_img('clipped_book.jpg', resized_book)
            dataset.save_text('name.txt', book_name)
            dataset.save_text('user.txt', info['user_name'])
            dataset.commit()

            self.talk('{}の登録受付が完了しました。'.format(book_name))
            to_continue = self.ask_with_retry('他の本も登録しますか?')
            if not self.controller.message_processor.is_yes(to_continue):
                break

        to_study_now = self.ask_with_retry('今すぐ本の学習を行いますか?')
        if self.controller.message_processor.is_yes(to_study_now):
            self._train()
        else:
            self.talk('登録手続きを完了します。お疲れ様でした。')

    def _train(self):
        self.push_message('今からしばらく勉強します')
        self.controller.image_processor.train_book()
        self.push_message('勉強が終わりました')


class BookStudy(Register):
    def command(self, *words):
        self._train()


class Borrow(EquipmentRentalBase):

    def command(self, *words):
        if self.controller.image_processor.face_classifier is None:
            self.talk('ユーザーが登録されていないため、受け付けできません')
            return

        self.talk('貸し出しを受付けます。本を持ってカメラの前に立ってください。')
        sleep(2)
        info = self.rental_info()
        if not info:
            self.talk('処理に失敗しました')
            return

        book_id = self.controller.image_processor.which_book(info['book_img'])
        book_name = self.controller.storage.get_name('book', book_id)

        data_dir = self.controller.storage.new_dir('rental', book_id)
        data_dir.save_img('rental.jpg', info['img'])
        data_dir.save_text('user.txt', str(info['user_id']))
        data_dir.save_text('time.txt', datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))
        data_dir.commit()

        self.push_message('{}さんへの{}の貸し出しを受け付けました'.format(info['user_name'], book_name))
        rental_text = '{}さんが{}を借りました'.format(info['user_name'], book_name)
        self.controller.notifier.notify('貸し出し', rental_text, data_dir.files())


class Return(EquipmentRentalBase):

    def command(self, *words):
        if self.controller.image_processor.face_classifier is None:
            self.talk('ユーザーが登録されていないため、受け付けできません')
            return

        self.talk('返却を受付けます。本を持ってカメラの前に立ってください。')
        sleep(2)
        info = self.rental_info()
        if not info:
            self.talk('処理に失敗しました')
            return

        book_id = self.controller.image_processor.which_book(info['book_img'])
        book_name = self.controller.storage.book_name(book_id)

        data_dir = self.controller.storage.new_dir('rental', book_id)
        rental_user = data_dir.read_text('user.txt')
        if rental_user is None:
            self.talk('その本は元々借りられていないので、返却手続きの必要はありません')
            return

        if int(rental_user) == info['user_name']:
            msg = '{}さんが{}を返却しました'.format(info['user_name'], book_name)
        else:
            rental_user_name = self.controller.storage.get_name('user', int(rental_user))
            msg = '{}さんが{}の代理で{}を返却しました'.format(info['user_name'], rental_user_name, book_name)

        data_dir.save_text('time.txt', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        data_dir.save_img('rental.jpg', info['img'])
        data_dir.commit()

        self.push_message('{}さんからの{}の返却を受け付けました'.format(info['user_name'], book_name))
        self.controller.notifier.notify('貸し出し', msg, data_dir.files())
