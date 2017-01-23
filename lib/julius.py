# coding: utf-8

import shlex
from subprocess import Popen, PIPE
from threading import Thread
from time import sleep


class Julius:
    def __init__(self, config):
        self.config = config
        julius_env = {
            'AUDIODEV': '/dev/dsp1',
            'ALSADEV': 'plughw:{},{}'.format(config['card'], config['device'])
        }
        command = '{} -C {} -C {}'.format(config['julius_bin'], config['main_conf'], config['gmm_conf'])
        self.julius_proc = Popen(shlex.split(command), stdout=PIPE, env=julius_env, universal_newlines=True, bufsize=1)
        self.output = []
        self.reader_thread = Thread(target=self.write_output)
        self.reader_thread.start()

    def write_output(self):
        lines = []
        while True:
            line = self.julius_proc.stdout.readline().strip()
            if line:
                self.output.insert(0, line)
            else:
                if self.julius_proc.poll() is not None:
                    print('finish_ouput')
                    break

    def readline(self):
        if self.output:
            return self.output.pop()

    def stop(self):
        self.julius_proc.terminate()
        self.reader_thread.join()

    def listen(self):
        pass1_best = ''
        sentence1 = ''

        while True:
            line = self.readline()
            if not line:
                sleep(self.config.get('interval', 0.2))
                if self.julius_proc.poll() is not None:
                    return None, None
                else:
                    continue
            if line.startswith('pass1_best:'):
                pass1_best = line.split(':', 1)[1]
                pass1_best = pass1_best.replace(' ', '').rstrip('。、')
            elif line.startswith('sentence1:'):
                sentence1 = line.split(':', 1)[1]
                sentence1 = sentence1.replace(' ', '').rstrip('。、')
            else:
                continue

            if sentence1:
                return pass1_best, sentence1
