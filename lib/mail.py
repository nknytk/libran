# coding: utf-8

import os
import smtplib
import mimetypes
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.audio import MIMEAudio
from email.mime.image import MIMEImage
from email.mime.text import MIMEText
from email.utils import formatdate
from time import sleep, time


class Mail:
    def __init__(self, config):
        self.config = config

    def notify(self, title, message, attachment_paths=[], level='INFO'):
        m = self.create_mail(title, message, attachment_paths)
        self.send(m)

    def create_mail(self, title, message, attachment_paths=[]):
        """ メールを作成する """
        mailcontent = MIMEMultipart()
        mailcontent['From'] = self.config['mail_from']
        mailcontent['To'] = self.config['mail_to']
        mailcontent['Subject'] = title
        mailcontent['Date'] = formatdate()
        if message:
            msg = MIMEText(message, 'plain', 'utf-8')
        mailcontent.attach(msg)
        self.attach_files(mailcontent, attachment_paths)
        return mailcontent

    def attach_files(self, mailcontent, attachment_paths):
        """ メールにファイルを添付する """
        for fname in attachment_paths:
            with open(fname, 'rb') as f:
                content = f.read()
            fname = fname.split('/')[-1]

            conttype, ignored = mimetypes.guess_type(fname)
            if conttype is None:
                conttype = 'application/octet-stream'
            maintype, subtype = conttype.split('/')

            if maintype == 'image':
                attachment = MIMEImage(content, subtype, filename=fname)
            elif maintype == 'text':
                attachment = MIMEText(content, subtype, 'utf-8')
            elif maintype == 'audio':
                attachment = MIMEAudio(content, subtype, filename=fname)
            else:
                attachment = MIMEApplication(content, subtype, filename=fname)

            attachment.add_header('Content-Disposition', 'attachment', filename=fname)
            mailcontent.attach(attachment)

    def send(self, mailcontent):
        mailer = smtplib.SMTP(self.config['smtp_server'], self.config.get('smtp_port', 587))
        try:
            mailer.ehlo()
            mailer.starttls()
            mailer.ehlo()
            mailer.login(self.config['mail_from'], self.config['password'])
            mailer.sendmail(
                self.config['mail_from'],
                self.config['mail_to'].split(','),
                mailcontent.as_string()
            )
        finally:
            mailer.close()
            print('mail sent at ' + str(time()))


if __name__ == '__main__':
    import sys
    import json
    with open(sys.argv[1]) as fp:
        config = json.load(fp)
    m = Mail(config['notification'])
    m.notify(title='テストメール', message='ちゃんと届いた?')
