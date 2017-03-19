# coding: utf-8

import os
import sys
import traceback
sys.path.append(os.path.dirname(__file__))
from base import Command


class TakeAndSendPhoto(Command):

    def command(self, *words):
        dataset = self.controller.storage.new_dir('user')

        n_img = 0
        while True:
            self.talk('写真を撮ります。はい、チーズ')
            img = self.controller.camera.capture()
            dataset.save_img('image_{}.jpg'.format(n_img), img)
            n_img += 1

            try:
                to_continue = self.fetch_input('もう一枚撮りますか?')
                if not self.controller.message_processor.is_yes(to_continue):
                    break
            except:
                print(traceback.format_exc())
                break

        self.controller.notifier.notify('写真', '先ほどの写真です', dataset.files())
        self.push_message('写真を送りました。確認してください。')
        dataset.clean()

