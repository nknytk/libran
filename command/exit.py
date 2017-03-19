# coding: utf-8

import os
import sys
sys.path.append(os.path.dirname(__file__))
from base import Command


class Exit(Command):

    def command(self, *words):
        really_stop = self.fetch_input('終了しますか?')
        if self.controller.message_processor.is_yes(really_stop):
            self.talk('終了します')
            self.controller.message_in.stop()
            self.talk('おやすみなさい')
            self.controller.message_out.stop()
            self.controller.cleanup()

        elif self.controller.message_processor.is_no(really_stop):
            self.push_message('このまま働きます。何かあれば呼んでください')

        else:
            self.talk('すみません、聞き取れませんでした。ひとまずこのまま働きますね')
