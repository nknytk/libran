# coding: utf-8

import json
import os
import sys
import cv2
import chainer
from chainer.training import extensions

sys.path.append(os.path.dirname(__file__))
import face_models
import util


def load_book_classifier(model_class, n_base_units, data_path, npz_file):
    if not os.path.exists(npz_file):
        return None
    if isinstance(model_class, str):
        model_class = getattr(face_models, model_class)
    n_classes = len(os.listdir(data_path))
    model = model_class(n_classes, n_base_units)
    chainer.serializers.load_npz(npz_file, model)
    model.train = False
    return model


def train_book(model_class, n_base_units, data_path, out_file, epoch=30, batch_size=1):
    n_classes = len(os.listdir(data_path))
    if isinstance(model_class, str):
        model_class = getattr(face_models, model_class)
    model = model_class(n_classes, n_base_units)

    optimizer = chainer.optimizers.Adam()
    optimizer.setup(model)

    train_dataset = util.create_dataset(data_path, lambda filename: filename.endswith('_book.jpg'))
    train_iter = chainer.iterators.SerialIterator(train_dataset, batch_size)
    updater = chainer.training.StandardUpdater(train_iter, optimizer, device=-1)
    trainer = chainer.training.Trainer(updater, (epoch, 'epoch'), out='out')

    trainer.extend(extensions.dump_graph('main/loss'))
    trainer.extend(extensions.LogReport())
    trainer.extend(extensions.ProgressBar(update_interval=10))
    trainer.extend(extensions.PrintReport(['epoch', 'main/loss', 'main/accuracy']))

    trainer.run()

    model.train = False
    chainer.serializers.save_npz(out_file, model)
    return model
