# coding: utf-8

import os
import sys
import cv2

sys.path.append(os.path.dirname(__file__))
from cnn import face_models, re_train, pre_train

DEFAULT_DATA_DIR = os.path.join(os.path.dirname(__file__), '../data')


class ImageProcessor:
    def __init__(self, config):
        self.config = config
        self.face_extractor = cv2.CascadeClassifier(config['cascade_path'])
        self.face_classifier = re_train.load_face_classifier(
            config.get('face_classifier_file', os.path.join(DEFAULT_DATA_DIR, 'face_model.pickle'))
        )
        self.book_classifier = pre_train.load_book_classifier(
            model_class=config.get('book_classifier_class', 'FaceClassifier100x100A'),
            n_base_units=config.get('book_classifier_n_base_units', 8),
            data_path=config.get('book_data', os.path.join(DEFAULT_DATA_DIR, 'book')),
            npz_file=config.get('book_classifier_file', os.path.join(DEFAULT_DATA_DIR, 'book_model.npz'))
        )
        self.black = (0, 0, 0)
        self.white = (255, 255, 255)

    def gray(self, img):
        return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    def blur(self, img):
        return cv2.GaussianBlur(img, (5, 5), 0)

    def face_rect(self, img_gray):
        """
        顔と判定されたエリアのうち、最も中央に近いものを顔として返す
        """
        frs = self.face_extractor.detectMultiScale(img_gray, scaleFactor=1.1, minNeighbors=1, minSize=(30, 30))
        img_center = (img_gray.shape[0] / 2, img_gray.shape[1] / 2)
        face_rect = None
        min_distance = None
        for rect in frs:
            rect_center = (rect[0] + rect[2] / 2, rect[1] + rect[3] / 2)
            dst = self.distance(img_center, rect_center)
            if min_distance is None or dst < min_distance:
                min_distance = dst
                face_rect = rect

        return face_rect

    def book_rect(self, img_gray, face_rect):
        """
        以下の条件を満たす輪郭を本の候補として扱う。
          1. 外接四角形の面積が顔の0.5倍から2.5倍までの間 (作者の顔:180x150, 文庫本:148x106, 雑誌:281x210)
          2. 外接四角形の高さ <= 顔の高さ * 1.6 && 外接四角形の幅 <= 顔の幅 * 1.6
          3. 0.4 < 外接四角形の縦/横 <= 1.2
          4. 下端が顔の上端より下である
          5. 外接四角形が顔と重なっていない
          6. 近似した時に点の数が4以上

        2値化の閾値を変えて輪郭抽出を行い、候補を探す。
        候補のうち、中心点が顔の中心点と最も近いものを本と判定する。
        """

        face_area = face_rect[2] * face_rect[3]
        min_book_area = face_area * 0.5
        max_book_area = face_area * 2.5
        max_book_width = face_rect[2] * 1.6
        max_book_height = face_rect[3] * 1.6
        face_top = face_rect[1]

        book_rects = []
        for th in range(31, 160, 16):
            ret, bin_img = cv2.threshold(img_gray, th, 255, 0)
            #cv2.imwrite('aaa_{}.jpg'.format(th), bin_img)
            edge, contours, hierarchy = cv2.findContours(bin_img, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
            for cnt in contours:
                rect = cv2.boundingRect(cnt)
                # 条件1
                if not (min_book_area <= rect[2] * rect[3] <= max_book_area):
                    continue
                # 条件2
                if not (rect[2] <= max_book_width and rect[3] <= max_book_height):
                    continue
                # 条件3
                if not (0.4 <= rect[2] / rect[3] <= 1.2):
                    continue
                # 条件4
                if rect[1] + rect[3] < face_top:
                    continue
                # 条件5
                if self.intersect(rect, face_rect):
                    continue
                # 条件6
                epsilon = 0.02 * cv2.arcLength(cnt, True)
                approx = cv2.approxPolyDP(cnt, epsilon, True)
                if not (4 <= len(approx) <= 10):
                    continue

                book_rects.append((th, rect))

        min_distance = None
        face_center = (face_rect[0] + face_rect[2] / 2, face_rect[1] + face_rect[3] / 2)
        book_rect = None
        for th, rect in book_rects:
            rect_center = (rect[0] + rect[2] / 2, rect[1] + rect[3] / 2)
            dst = self.distance(face_center, rect_center)
            if min_distance is None or dst < min_distance:
                book_rect = rect
                min_distance = dst

        return book_rect


    def add_rect(self, img, rect, color=None):
        if color is None:
            color = self.black
        cv2.rectangle(img, (rect[0], rect[1]), (rect[0] + rect[2], rect[1] + rect[3]), color, thickness=2)

    def intersect(self, rect1, rect2):
        """ 2つの四角形が 交接する = 共有する領域を持つ かどうかを判定する """

        #左側にある四角形の右辺が右側の四角形の左辺より左にあったら、交接していない
        if rect1[0] < rect2[0]:
            left_rect, right_rect = rect1, rect2
        else:
            left_rect, right_rect = rect2, rect1
        if left_rect[0] + left_rect[2] < right_rect[0]:
            return False

        # 上側にある四角形の下辺が下側の四角形の上辺より上にあったら、交接していない
        if rect1[1] < rect2[1]:
            upper_rect, lower_rect = rect1, rect2
        else:
            upper_rect, lower_rect = rect2, rect1
        if upper_rect[1] + upper_rect[3] < lower_rect[1]:
            return False

        return True

    def distance(self, p1, p2):
        """ 2点間の距離を返す """
        return ((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)**(1/2)

    def clip(self, img, rect, resize_to=None):
        """ 四角形で切り抜いた画像を返す """
        clipped_img = img[rect[1]: rect[1] + rect[3], rect[0]: rect[0] + rect[2]]
        if resize_to:
            clipped_img = cv2.resize(clipped_img, resize_to)
        return clipped_img

    def resize(self, img, resize_to=(100, 100)):
        return cv2.resize(img, resize_to)

    def train_face(self):
        """ 顔分類モデルを学習させる"""
        config = self.config
        self.face_classifier = re_train.train_face(
            model_class=config.get('face_classifier_class', 'FaceClassifier100x100A'),
            pre_trained_file=config.get('face_classifier_pre_trained_file',
                                        os.path.join(DEFAULT_DATA_DIR, '../pre_trained_models/A_16.npz')),
            n_base_units=config.get('face_classifier_n_base_units', 16),
            data_path=config.get('face_data', os.path.join(DEFAULT_DATA_DIR, 'user')),
            re_trained_file=config.get('face_classifier_file', os.path.join(DEFAULT_DATA_DIR, 'face_model.pickle'))
        )

    def train_book(self):
        config = self.config
        self.book_classifier = pre_train.train_book(
            model_class=config.get('book_classifier_class', 'FaceClassifier100x100A'),
            n_base_units=config.get('book_classifier_n_base_units', 8),
            data_path=config.get('book_data', os.path.join(DEFAULT_DATA_DIR, 'book')),
            out_file=config.get('book_classifier_file', os.path.join(DEFAULT_DATA_DIR, 'book_model.npz'))
        )

    def who_is(self, face_img):
        return self.face_classifier.classify(face_img)

    def which_book(self, book_img):
        return self.book_classifier.classify(book_img)


class ObjectNotFound(Exception):
    def __init__(self, object_name):
        self.missing_object = object_name

    def __str__(self):
        return 'Could not find {} from image'.format(self.missing_object)


if __name__ == '__main__':
    import json
    from time import time, sleep
    from datetime import datetime
    from camera import Camera


    with open(sys.argv[1]) as fp:
        conf = json.load(fp)
    ih = ImageProcessor(conf['image_processor'])
    ch = Camera(conf['camera'])

    while True:
        sys.stdout.write('Input image file path: ')
        fn = input()

        t1 = time()
        if fn.strip():
            try:
                img = cv2.imread(fn)
            except:
                break
        else:
            img = ch.capture()

        t2 = time()
        gimg = ih.gray(img)

        t3 = time()
        face = ih.face_rect(gimg)
        t4 = time()
        if face is None:
            print('Failed to detect face.')
            print('imread:{}, gray:{}, face:{}'.format(t2 - t1, t3 - t2, t4 - t3))
            continue
        cv2.imwrite('f.jpg', ih.clip(img, face))

        book = ih.book_rect(gimg, face)
        t5 = time()

        if book is None:
            print('Failed to detect book.')
        else:
            ih.add_rect(img, face)
            ih.add_rect(img, book)
            cv2.imwrite('k.jpg', img)
            print('k.jpg')

        print('imread:{}, gray:{}, face:{}, book:{}'.format(t2 - t1, t3 - t2, t4 - t3, t5 - t4))
