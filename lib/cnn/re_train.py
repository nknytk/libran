# coding: utf-8

import json
import os
import sys
import pickle
import cv2
import chainer
from chainer.training import extensions

sys.path.append(os.path.dirname(__file__))
import face_models
import util


#def load_face_classifier(model_class, re_trained_file, n_base_units, data_path):
def load_face_classifier(re_trained_file):
    """ ファイルに保存された再学習済みの顔分類モデルを読み込む """
    if not os.path.exists(re_trained_file):
        return None

    with open(re_trained_file, mode='rb') as fp:
        model = pickle.load(fp)
    model.train = False
    return model


def train_face(model_class, pre_trained_file, n_base_units, data_path, re_trained_file):
    """ ユーザーの顔写真と事前学習済みモデルから、顔分類モデルを作成してファイルに保存 """
    if isinstance(model_class, str):
        model_class = getattr(face_models, model_class)
    n_classes = len(os.listdir(data_path))
    model = face_models.FaceClassifier100x100_Relearn(
        n_classes=n_classes,
        n_base_units=n_base_units,
        learned_model_file=pre_trained_file,
        orig_model_class=model_class,
        orig_n_classes=120
    )
    optimizer = chainer.optimizers.Adam()
    optimizer.setup(model)

    train_dataset = util.create_dataset(data_path, lambda filename: filename.endswith('_face.jpg'))
    train_iter = chainer.iterators.SerialIterator(train_dataset, 1)
    updater = chainer.training.StandardUpdater(train_iter, optimizer, device=-1)
    trainer = chainer.training.Trainer(updater, (20, 'epoch'), out='work/face_train')

    trainer.extend(extensions.dump_graph('main/loss'))
    trainer.extend(extensions.LogReport())
    trainer.extend(extensions.ProgressBar(update_interval=10))
    trainer.extend(extensions.PrintReport(['epoch', 'main/loss', 'main/accuracy']))

    trainer.run()

    with open(re_trained_file, mode='wb') as fp:
        pickle.dump(model, fp)

    model.train = False
    return model
