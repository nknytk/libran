# coding: utf-8

import os
import sys
from time import sleep
sys.path.append(os.path.dirname(__file__))
from base import Command


class EquipmentRentalBase(Command):

    def rental_info(self):
        max_try = 3
        for i in range(max_try):
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

            self.controller.image_processor.add_rect(img, face_rect, (255, 0, 0))  # 顔を青で囲う
            if book_rect is not None:
                self.controller.image_processor.add_rect(img, book_rect, (0, 0, 255))  # 本を赤で囲う
            name = self.controller.storage.user_name(user_id)
            return {'user_id': user_id, 'user_name': name, 'img': img}

        return {}


class Register(EquipmentRentalBase):

    def command(self, *words):
        self.talk('未実装です')


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

        data_dir = self.controller.storage.new_dir('rental')
        data_dir.save_img(str(info['user_id']) + '.jpg', info['img'])
        data_dir.commit()
        self.push_message(info['user_name'] + 'さんへの本の貸し出しを受け付けました')
        self.controller.notifier.notify('貸し出し', info['user_name'] + 'さんが本を借りました', data_dir.files())


class Return(EquipmentRentalBase):
    def command(self, *words):
        pass
