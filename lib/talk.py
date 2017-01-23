# coding: utf-8

import os
import random
import shlex
from datetime import datetime
from threading import Thread
from time import sleep
try:
    from subprocess import run
    run_subproc = run
except:
    from subprocess import call
    run_subproc = call

TMPDIR = '/tmp/'
HTS_VOICE = {
  'man': '/usr/share/hts-voice/nitech-jp-atr503-m001/nitech_jp_atr503_m001.htsvoice',
  'woman': '/usr/share/hts-voice/mei/mei_normal.htsvoice'
}


class Jtalk:
    def __init__(self, config):
        self.htsvoice = config.get('htsvoice', '/usr/share/hts-voice/nitech-jp-atr503-m001/nitech_jp_atr503_m001.htsvoice')
        self.tmpdir = config.get('tmp_dir', '/tmp')
        self.dict = config.get('dict', '/var/lib/mecab/dic/open-jtalk/naist-jdic')
        self.interval = config.get('interval', 0.1)
        self.txt_queue = []
        self.should_run = True
        self.talk_thread = None

        self.run()

    def run(self):
        self.talk_thread = Thread(target=self.talk_if_message)
        self.talk_thread.start()

    def talk_if_message(self):
        while self.should_run:
            try:
                txt = self.txt_queue.pop()
                self.talk(txt)
            except IndexError as e:
                sleep(self.interval)

    def stop(self):
        self.should_run = False
        if self.talk_thread is not None:
            self.talk_thread.join()
        self.clear()

    def talk(self, txt):
        talk_id = 'jtalk_{}_{}'.format(datetime.now().strftime('%Y%m%d_%H%M%S'), random.randint(0, 100000))
        talk_txt = os.path.join(self.tmpdir, talk_id + '.txt')
        talk_wav = os.path.join(self.tmpdir, talk_id + '.wav')

        with open(talk_txt, mode='w') as fp:
            fp.write(txt)

        jtalk_command = 'open_jtalk -m {} -x {} -ow {} {}'.format(self.htsvoice, self.dict, talk_wav, talk_txt)
        run_subproc(shlex.split(jtalk_command))
        run_subproc(shlex.split('aplay --quiet ' + talk_wav))

        os.remove(talk_wav)
        os.remove(talk_txt)

    def push(self, txt, block=True):
        self.txt_queue.insert(0, txt)
        if not block:
            return

        while True:
            if self.txt_queue:
                sleep(self.interval)
            else:
                break

    def clear(self):
        self.txt_queue = []


if __name__ == '__main__':
    import sys
    talk(' '.join(sys.argv[1:]))
