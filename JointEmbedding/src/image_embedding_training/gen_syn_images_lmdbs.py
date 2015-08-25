#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import lmdb
import shutil
import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(BASE_DIR))
from global_variables import *

train_val_split = [int(line.strip()) for line in open(g_syn_images_train_val_split, 'r')]

env = lmdb.open(g_pool5_lmdb, readonly=True)
if os.path.exists(g_pool5_lmdb_train):
    shutil.rmtree(g_pool5_lmdb_train)
env_train = lmdb.open(g_pool5_lmdb_train, map_size=int(1e12))
if os.path.exists(g_pool5_lmdb_val):
    shutil.rmtree(g_pool5_lmdb_val)
env_val = lmdb.open(g_pool5_lmdb_val, map_size=int(1e12))

idx = 0
cache_train = dict()
cache_val = dict()
txn_commit_count = 512

report_step = 10000;
with env.begin() as txn:
    cursor = txn.cursor()
    for key, value in cursor:
        if train_val_split[idx]:
            cache_train[key] = value
            if (len(cache_train) == txn_commit_count or idx == len(train_val_split)-1):
                with env_train.begin(write=True) as txn_train:
                    for k, v in cache_train.iteritems():
                        txn_train.put(k, v)
                cache_train.clear()
        else:
            cache_val[key] = value
            if (len(cache_val) == txn_commit_count or idx == len(train_val_split)-1):
                with env_val.begin(write=True) as txn_val:
                    for k, v in cache_val.iteritems():
                        txn_val.put(k, v)
                cache_val.clear()
        if(idx%report_step == 0):
            print datetime.datetime.now().time(), '-', idx, 'of', len(train_val_split), 'processed!'
        idx = idx + 1
        

env.close()
env_train.close()
env_val.close()