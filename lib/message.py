# coding: utf-8

import re
from MeCab import Tagger
import romkan


class MessageProcessor:

    pattern_yes = re.compile('^.*(はい|うん|いいよ|オッケー|お願い|そうして).*$')
    pattern_no = re.compile('^.*(いえ|ダメ|嫌|やだ|違う|違います|もういい|しません|やりません|しない|やらない|そうじゃない).*$')
    pattern_cancel = re.compile('^.*(キャンセル|ストップ|終了|終わり|終わる|中断|やめる|やめて).*$')

    def __init__(self, config):
        self.config = config

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

    def is_yes(self, txts):
        return self._check_match(txts, self.pattern_yes)

    def is_no(self, txts):
        return self._check_match(txts, self.pattern_no)

    def is_cancel(self, txts):
        return self._check_match(txts, self.pattern_cancel)

    def _check_match(self, txts, pattern):
        if isinstance(txts, str):
            txts = (txts,)
        for txt in txts:
            if pattern.match(txt):
                return True
        return False
