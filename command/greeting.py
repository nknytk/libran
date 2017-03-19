# coding: utf-8

import os
import sys
from datetime import datetime
sys.path.append(os.path.dirname(__file__))
from base import Command


class Greet(Command):

    greeting_pairs = [
        ('おはよう', 'おはようございます'),
        ('こんにちは', 'こんにちは'),
        ('こんばんは', 'こんばんは'),
        ('ただいま', 'おかえりなさい'),
        ('おやすみ', 'おやすみなさい')
    ]

    def command(self, *txts):
        txt = txts[0]  # 最も確度が高い発話だけを使う

        for key, greeting in self.greeting_pairs:
            if txt.find(key) != -1:
                self.talk(greeting)
                return

        self.talk(self._timely_greeting())

    def _timely_greeting(self):
        current_hour = datetime.now().hour
        if current_hour <= 3:
            greeting = 'こんばんは'
        elif current_hour <= 11: 
            greeting = 'おはようございます'
        elif current_hour <= 17: 
            greeting = 'こんにちは'
        else:
            greeting = 'こんばんは'
        return greeting
