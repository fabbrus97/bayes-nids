import sklearn
import argparse
import pandas as pd
import os
import threading
import json
import random

LIMIT = 500000
QUEUEDONE = False

def producer():
    global counter
    global input_row_df
    global input_row_attack_df
    global QUEUEDONE
    
    while True:
        file = None
        file_attack = None
        mutex.acquire()
        
        counter += 1
        hasWork = False
        if len(input_path_queue) > 0 and len(input_row_df.index) <= LIMIT:
            file = input_path_queue.pop()
            hasWork = True
        if len(input_path_attack_queue) > 0 and len(input_row_attack_df.index) <= LIMIT:
            file_attack = input_path_attack_queue.pop()
            hasWork = True
        mutex.release()

        if not hasWork:
            mutex.acquire()
            QUEUEDONE = True
            mutex.release()
            
            consumerSem.release()
            break
            
        if file is not None:
            # print("Opening normal file", file)
            df_normal = pd.read_csv(os.path.join(args.input_path, file))
            samplemutex.acquire()
            input_row_df = pd.concat([input_row_df, df_normal])
            samplemutex.release()
        if file_attack is not None:
            # print("Opening attack file", file_attack)
            df_attack = pd.read_csv(os.path.join(args.input_path, file_attack))
            samplemutex.acquire()
            input_row_attack_df = pd.concat([input_row_attack_df, df_attack])
            samplemutex.release()
        
        
        consumerSem.release()
            
        samplemutex.acquire()
        print("input_row_df values:", len(input_row_df.index), "input_row_attack_df values:", len(input_row_attack_df.index), "normal files to pop:", len(input_path_queue), "attack files to pop:", len(input_path_attack_queue))
        samplemutex.release()

        samplemutex.acquire()
        l1 = len(input_row_df.index)
        l2 = len(input_row_attack_df.index)
        samplemutex.release()
        while l1 > LIMIT and l2 > LIMIT:
            
            consumerSem.release()
            producerSem.acquire()

            samplemutex.acquire()
            l1 = len(input_row_df.index)
            l2 = len(input_row_attack_df.index)
            samplemutex.release()
            

def get_sample(fraction, normal):
    global input_row_df
    global input_row_attack_df
    while True:
        
        mutex.acquire()
        if QUEUEDONE:
            mutex.release()
            return pd.DataFrame()
        mutex.release()

        samplemutex.acquire()
        l1 = len(input_row_df.index)
        l2 = len(input_row_attack_df.index)

        if l1 < 20000 or l2 < 20000:
            # print("Not enough data")
            samplemutex.release()
            consumerSem.acquire()
            continue
        
        if normal:
            data = input_row_df.sample(n=int(10000*fraction))
            input_row_df.drop(data.index, inplace=True)
        else:
            data = input_row_attack_df.sample(n=int(10000*fraction))
            input_row_attack_df.drop(data.index, inplace=True)
        producerSem.release() #notify the producer we have freed some space in the buffer
        samplemutex.release()
        return data

    # samplemutex.acquire()
    # data = input_row_df.sample(n=int(10000*fraction))
    # input_row_df.drop(data.index, inplace=True)
    # samplemutex.release()
    # producerSem.release() #notify the producer we have freed some space in the buffer
    

def process_csv():
    global sparse_features
    global counter
    global QUEUEDONE

    while True:
        mutex.acquire()
        if QUEUEDONE:
            mutex.release()
            break
        n = counter
        mutex.release()
        
        test_normal_sample = get_sample(args.fraction, True)
        test_attack_sample = get_sample(args.fraction, True)
        train_normal_sample = get_sample(1-args.fraction, False)
        train_attack_sample = get_sample(1-args.fraction, False)

        if test_normal_sample.empty or test_attack_sample.empty \
            or train_normal_sample.empty or test_attack_sample.empty:
            continue
    
        test = pd.concat([test_normal_sample, test_attack_sample])
        train = pd.concat([train_normal_sample, train_attack_sample])

        df = pd.DataFrame()
        df = pd.concat([train, test])

        indexmax = {}
        for key in sparse_features.keys():
            indexmax[key] = max(df[key])
        
        
        for key in sparse_features.keys():
            if indexmax[key] > sparse_features[key]:
                sparse_features[key] = indexmax[key]
        

        train.to_csv(os.path.join(args.output_path, f"train.{n}.csv"), index=False)
        test.to_csv(os.path.join(args.output_path, f"test.{n}.csv"), index=False)
        # train = train.sample(frac=1).reset_index(drop=True) #shuffle in place
        # test = test.sample(frac=1).reset_index(drop=True) #shuffle in place


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="split_data.py",
        description="Split data into training and testing dataset."
    )
    parser.add_argument("--input_path", required=True)
    parser.add_argument("--output_path", required=True)
    parser.add_argument("--fraction", required=True, type=float) #fraction that will go in the test e.g. 0.3 = 70% train, 30% test

    args = parser.parse_args()

    input_path_queue = []
    input_path_attack_queue = []
    input_row_df = pd.DataFrame()
    input_row_attack_df = pd.DataFrame()
    counter = 0
    sparse_features = {
        "SrcAddr": 0,
        "DstAddr": 0,
        "Sport": 0,
        "Dport": 0,
        "Proto": 0,
        "State": 0,
        "proto_state_and": 0
    }


    mutex = threading.Lock()
    
    producerSem = threading.Semaphore(0)
    consumerSem = threading.Semaphore(0)
    samplemutex = threading.Lock()
    for file in os.listdir(args.input_path):
        if file.endswith(".csv"):
            if file.find("attack") >= 0:
                input_path_attack_queue.append(file)
            else:
                input_path_queue.append(file)

    random.shuffle(input_path_queue)
    random.shuffle(input_path_attack_queue)


    threads = [threading.Thread(target=process_csv), threading.Thread(target=producer)]
    
    for i in range(2):
        threads[i].start()
    
    for i in range(2):
        threads[i].join()
        
    
    json.dump(sparse_features, open(os.path.join("dataset", "sparse_features_max_index.json"), "w"), indent="  ")
