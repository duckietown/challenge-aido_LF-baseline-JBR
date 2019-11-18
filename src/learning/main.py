#!/usr/bin/env python

import argparse
import os
import shutil
import time

import sklearn.model_selection
import numpy as np
import logging

from src.learning.cnn_models import CNNResidualNetwork, CNN160Model, CNN96Model
from src.learning.cnn_training_functions import load_real_data, load_sim_data, Trainer
from src.utils.config import CFG

os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
os.environ["CUDA_VISIBLE_DEVICES"] = "0"
logger = logging.getLogger()


def read_data(data_dir, real_filename, sim_filename):
    real_file_data_path = os.path.join(os.getcwd(), data_dir, real_filename)
    sim_file_data_path = os.path.join(os.getcwd(), data_dir, sim_filename)

    logger.info('Reading the real dataset')
    XR, YR = load_real_data(real_file_data_path)
    logger.info('Reading the sim dataset')
    XS, YS = load_sim_data(sim_file_data_path)

    K = 100000
    XR = XR[:K]
    YR = YR[:K]
    XS = XS[:K]
    YS = YS[:K]

    XR_train, XR_test, YR_train, YR_test = sklearn.model_selection.train_test_split(
        XR, YR, train_size=0.7, random_state=CFG.seed)
    logger.info(f'Real dataset split is {len(XR_train)} in train, {len(XR_test)} in test')

    XS_train, XS_test, YS_train, YS_test = sklearn.model_selection.train_test_split(
        XS, YS, train_size=0.7, random_state=CFG.seed)
    logger.info(f'Real dataset split is {len(XS_train)} in train, {len(XS_test)} in test')

    X_train = np.vstack([XR_train, XS_train])
    X_test = np.vstack([XR_test, XS_test])
    Y_train = np.vstack([YR_train, YS_train])
    Y_test = np.vstack([YR_test, YS_test])
    logger.info(f'Overall split is {len(X_train)} in train, {len(X_test)} in test')
    return X_train, X_test, Y_train, Y_test


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument('model_name', type=str, help='The name of the trained model')
    args = parser.parse_args()
    return args


def main() -> None:
    args = parse_args()

    model_dir = os.path.join('learned_models', args.model_name)
    if os.path.exists(model_dir):
        shutil.rmtree(model_dir)
    os.makedirs(model_dir)

    filename = os.path.join(model_dir, 'log.txt')
    logger.setLevel(logging.INFO)
    logger.addHandler(logging.StreamHandler())
    logger.addHandler(logging.FileHandler(filename))

    train_images, test_images, train_velocities, test_velocities = read_data(
        'data', 'LF_dataset_real.h5', 'LF_dataset_sim.h5')

    logger.info('Starting training for {} model.'.format(args.model_name))
    start_time = time.time()

    # create and train the model
    if CFG.model == 'CNNResidualNetwork':
        model = CNNResidualNetwork(CFG.regularizer)
    elif CFG.model == 'CNN160Model':
        model = CNN160Model(CFG.regularizer)
    elif CFG.model == 'CNN96Model':
        model = CNN96Model(CFG.regularizer)
    else:
        raise ValueError(f'Unknown model from the config: {format(CFG.model)}')

    trainer = Trainer(CFG.batch_size, CFG.epochs, CFG.lr)
    trainer.train(model, model_dir, train_velocities, train_images, test_velocities, test_images)

    # calculate total training time in minutes
    training_time = (time.time() - start_time) / 60

    logger.info('Finished training of {} in {:.1f} minutes.'.format(args.model_name, training_time))


if __name__ == '__main__':
    main()
