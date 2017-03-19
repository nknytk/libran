# coding: utf-8

import os
import re
import sys

base_dir = os.path.join(os.path.dirname(__file__), '..')
sys.path.append(base_dir)
from command import user, rental, photo, exit


class RegexCommandRouter:

    def __init__(self, controller):
        self.command_routes = [
            (re.compile('^.*((ユーザー|ユーザ|人|利用者)(|の|を)(登録|追加)|(新規|新しい)(ユーザー|ユーザ|人|利用者)).*$'),
             user.Register(controller)),
            (re.compile('^.*((本|備品)(|の|を)(登録|追加|買った|買ってきた)|新しい(本|備品)).*$'),
             rental.Register(controller)),
            (re.compile('^.*(貸して|貸し出し|借りる|借ります|借りたい|レンタル|持ってく).*$'),
             rental.Borrow(controller)),
            (re.compile('^.*(返す|戻す|返却).*$'),
             rental.Return(controller)),
            (re.compile('^.*(写真|撮影|写メ|しゃめ|インスタ|いんすた).*$'),
             photo.TakeAndSendPhoto(controller)),
            (re.compile('^.*(勉強|学習).*$'), user.FaceStudy(controller))
        ]

    def routes(self, *texts):
        for text in texts:
            for pattern, command in self.command_routes:
                if pattern.match(text):
                    return command
