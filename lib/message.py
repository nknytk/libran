# coding: utf-8

import re
from MeCab import Tagger
import romkan


class MessageProcessor:

    keywords = [
        ('cancel', [
            '終わり', '終わる', '終了', '中断', 'ストップ',
            'やめる', 'やめて', 'キャンセル'
        ]),
        ('user_registoration', [
            'ユーザー登録', 'ユーザーの登録', 'ユーザーを登録',
            'ユーザー追加', 'ユーザーの追加', 'ユーザーを追加',
            'ユーザ登録', 'ユーザの登録', 'ユーザを登録',
            'ユーザ追加', 'ユーザの追加', 'ユーザを追加',
            '人の登録', '人を登録', '人の追加', '人を追加',
            '新規ユーザー', '新しいユーザー', '新しい人'
            '新規ユーザ', '新しいユーザ',
        ]),
        ('book_registoration', [
            '本の登録', '本を登録', '本の追加', '本を追加',
            '新しい本', '本買った', '本買ってきた'
        ]),
        ('borrow_book', ['貸して', '貸し出し', '借りる', '借ります', '借りたい', 'レンタル', '持ってく']),
        ('return_book', ['返す', '戻す', '返却']),
        ('kill', ['おやすみ']),
        ('no', ['いえ', 'ダメ', '嫌', 'やだ', '違う', '違います', 'もういい', 'しません', 'やりません']),
        ('yes', ['はい', 'うん', 'そう', 'いいよ', 'オッケー', 'お願い']),
        ('train', ['勉強', '学習']),
        ('photo', ['写真', 'しゃめ'])
    ]

    def __init__(self, config):
        self.config = config
        self.tagger = Tagger('-Oyomi')
        self.classifier = []
        for command, kwds in self.keywords:
            katakanas = [self.katakana(kwd) for kwd in kwds]
            self.classifier.append((command, re.compile('^.*({}).*$'.format('|'.join(katakanas)))))

    def map_to_command(self, *txts):
        for txt in txts:
            kana = self.katakana(txt)
            for command, ptn in self.classifier:
                if ptn.match(kana):
                    return command

    def katakana(self, txt):
        return romkan.to_katakana(self.tagger.parse(txt).strip())

    def remove_prefix(self, txt, prefixes):
        for prefix in prefixes:
            if txt.startswith(prefix):
                txt = txt[len(prefix):]
        return txt

    def remove_suffix(self, txt, suffixes):
        for suffix in suffixes:
            if txt.endswith(suffix):
                txt = txt[:-len(suffix)]
        return txt
