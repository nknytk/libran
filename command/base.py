# coding: utf-8

import traceback
from time import time, sleep


class Command:

    def __init__(self, controller):
        """ arg1: libran.Controllerインスタンス """
        self.controller = controller

    def exec(self, *sentence_candidates):
        self.controller.is_in_command = True
        try:
            self.command(sentence_candidates)
        except UserInturruptException:
            self.controller.message_out.talk('キャンセルします')
        except:
            self.controller.message_out.talk('エラーが発生しました')
            print(traceback.format_exc())
        finally:
            self.controller.is_in_command = False

    def command(self, *sentence_candidates):
        """
        arg1: ユーザー入力メッセージのタプル(確度が高い順)
        子クラスで具体的な処理を実装してください
        """
        pass

    def cancel(self):
        self.controller.should_cancel = False
        raise UserInturruptException()

    def fetch_input(self, message=None, timeout=20):
        """ ユーザー入力を取得する """
        if message:
            self.controller.message_out.talk(message)
        self.controller.is_waiting_for_input = True

        answer = self.controller.answer
        wait_until = time() + timeout
        while True:
            if time() >= wait_until:
                self.controller.is_waiting_for_input = False
                raise InputTimeoutException()

            if self.controller.answer:
                answer = self.controller.answer
                self.controller.answer = None
                self.controller.is_waiting_for_input = False
                return answer

            sleep(0.1)

    def ask_with_retry(self, ask_message, timeout=20, max_try=3):
        i = 0
        while True:
            try:
                i += 1
                answer = self.fetch_input(timeout)
                return answer
            except InputTimeoutException:
                self.controller.message_out.talk('すみません、聞き取れませんでした。')
                if i >= max_try:
                    self.controller.message_out.talk('管理者に問い合わせてください')
                    raise InputTimeoutException()
                else:
                    self.controller.message_out.talk('もう一度お願いします。')

    def talk(self, message):
        self.controller.message_out.talk(message)

    def push_message(self, message):
        self.controller.message_out.push(message)



class InputTimeoutException(Exception):
    pass


class UserInturruptException(Exception):
    pass
