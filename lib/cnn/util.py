# coding: utf-8

import os
import chainer


def create_dataset(root_dir, data_condition):
    data_pairs = []
    for label_dir in os.listdir(root_dir):
        label = int(label_dir)
        files = [f for f in os.listdir(os.path.join(root_dir, label_dir)) if data_condition(f)]
        data_pairs += [(os.path.join(label_dir, f), label) for f in files]
    return chainer.datasets.image_dataset.LabeledImageDataset(pairs=data_pairs, root=root_dir)
