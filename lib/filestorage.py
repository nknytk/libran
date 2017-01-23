# coding: utf-8

import os
import shutil
from datetime import datetime
import cv2


class FileManager:
    def __init__(self, config):
        libran_home = os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))
        data_dir = config.get('data_dir', os.path.join(libran_home, 'data'))
        work_dir = config.get('work_dir', os.path.join(libran_home, 'work'))
        self.data_dirs = {
            'work': work_dir,
            'user': os.path.join(data_dir, 'user'),
            'book': os.path.join(data_dir, 'book'),
            'rental': os.path.join(data_dir, 'rental'),
        }
        for d in self.data_dirs.values():
            if not os.path.exists(d):
                os.makedirs(d)

    def new_dir(self, data_type):
        exisiting_ids = [int(id) for id in os.listdir(self.data_dirs[data_type]) if not id.startswith('.')]
        new_id = max(exisiting_ids) + 1 if exisiting_ids else 0
        dpath = os.path.join(self.data_dirs[data_type], str(new_id))
        return WorkingDirectory(dpath, self.data_dirs['work'])


class WorkingDirectory:
    def __init__(self, final_path, work_dir):
         self.final_path = final_path
         self.tmpdir = os.path.join(work_dir, datetime.now().strftime('%Y%m%d_%H%M%S'))
         os.makedirs(self.tmpdir)

    def save_text(self, filename, contents):
        with open(os.path.join(self.tmpdir, filename), mode='w') as fp:
            fp.write(contents)

    def save_img(self, filename, img):
        cv2.imwrite(os.path.join(self.tmpdir, filename), img)

    def commit(self):
        if os.path.exists(self.final_path):
            shutil.rmtree(self.final_path)
        os.rename(self.tmpdir, self.final_path)

    def files(self):
        if os.path.exists(self.tmpdir):
            files = [os.path.join(self.tmpdir, f) for f in os.listdir(self.tmpdir)]
        elif os.path.exists(self.final_path):
            files = [os.path.join(self.final_path, f) for f in os.listdir(self.final_path)]
        else:
            files = []
        return files

    def clean(self):
        if os.path.exists(self.tmpdir):
            shutil.rmtree(self.tmpdir)
