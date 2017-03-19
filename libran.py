# coding: utf-8

import imp
import json
import os
import sys
import traceback
from time import sleep, time
from threading import Thread

this_dir = os.path.abspath(os.path.dirname(__file__))
from routing.regex import RegexCommandRouter


class Libran:
    def __init__(self, config_file=None):
        if config_file is None:
            config_file = os.path.join(this_dir, 'config.json')
        with open(config_file) as fp:
            self.config = json.load(fp)

        self.router = RegexCommandRouter(self)
        self.message_in = self.get_instance(self.config['message_in'])
        self.message_out = self.get_instance(self.config['message_out'])
        self.camera = self.get_instance(self.config['camera'])
        self.image_processor = self.get_instance(self.config['image_processor'])
        self.message_processor = self.get_instance(self.config['message_processor'])
        self.notifier = self.get_instance(self.config['notification'])
        self.storage = self.get_instance(self.config['storage'])

        self.should_work = True
        self.answer = None
        self.should_cancel = False
        self.is_waiting_for_input = False
        self.command_to_exec = None
        self.command_thread = Thread(target=self.exec_command)
        self.command_thread.start()
        self.run()

    def get_instance(self, config):
        mod_name, cls_name = config['class'].split('.')
        src = os.path.join(this_dir, 'lib', mod_name + '.py')
        mod = imp.load_source(mod_name, src)
        cls = getattr(mod, cls_name)
        return cls(config)

    def run(self):
        self.message_out.talk('おはようございます。何かあったら声をかけてください')

        while self.should_work == True:
            sentence_candidates = self.message_in.listen()
            if not sentence_candidates:
                sleep(0.1)
                continue

            print(sentence_candidates, self.is_waiting_for_input)
            if self.is_waiting_for_input:
                self.answer = sentence_candidates
                continue

            if self.command_to_exec is not None:
                if self.message_processor.is_cancel(sentence_candidates):
                    self.should_cancel = True
                continue

            command = self.router.routes(*sentence_candidates)
            if command:
                self.command_to_exec = (command, sentence_candidates)

        self.message_out.talk('おやすみなさい')

    def exec_command(self):
        while self.should_work == True:
            if self.command_to_exec is None:
                sleep(0.1)
                continue
            command, args = self.command_to_exec
            command.exec(*args)
            self.command_to_exec = None

    def cleanup(self):
        self.message_in.stop()
        self.camera.stop()
        self.command_thead.join()


if __name__ == '__main__':
    libran = Libran()
    try:
        libran.run()
    except Exception as e:
        sys.stderr.write(traceback.format_exc())
        raise e
    finally:
        libran.cleanup()
