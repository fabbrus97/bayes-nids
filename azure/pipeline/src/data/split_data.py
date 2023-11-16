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
    global input_row_df
    global input_row_attack_df
    global QUEUEDONE

    while True:
        file = None
        file_attack = None
        mutex.acquire()
        
        hasWork = False
        if len(input_path_queue) > 0 and len(input_row_df.index) <= LIMIT:
            file = input_path_queue.pop()
            hasWork = True
        if len(input_path_attack_queue) > 0 and len(input_row_attack_df.index) <= LIMIT:
            file_attack = input_path_attack_queue.pop()
            hasWork = True
        if not hasWork and (len(input_row_df) > 500 and len(input_row_attack_df) > 500):
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
            df_normal = pd.read_csv(os.path.join(args.input_path_normal, file))
            samplemutex.acquire()
            input_row_df = pd.concat([input_row_df, df_normal], ignore_index=True)
            samplemutex.release()
        if file_attack is not None:
            # print("Opening attack file", file_attack)
            df_attack = pd.read_csv(os.path.join(args.input_path_attack, file_attack))
            samplemutex.acquire()
            input_row_attack_df = pd.concat([input_row_attack_df, df_attack], ignore_index=True)
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
            

def get_sample(lines2get, normal):
    global input_row_df
    global input_row_attack_df
    # lines2get = 10000
    while True:
        mutex.acquire()
        if QUEUEDONE:
            mutex.release()
            return 0, pd.DataFrame()
        mutex.release()

        samplemutex.acquire()
        l1 = len(input_row_df.index)
        l2 = len(input_row_attack_df.index)

        if (normal and l1 < lines2get) or (not normal and l2 < lines2get):
            # print("Not enough data")
            samplemutex.release()
            # print("not enough data: requested", lines2get, "available normal:", l1, "av. attack:", l2, "- halving x =>", int(lines2get*0.5), "?")
            if (not normal and len(input_path_attack_queue) == 0) or (normal and len(input_path_queue) == 0): #NOTE this is optimistic
                #because if there are not enough samlpes in the queue, but there are some files left to open, we can wait to read these files
                #but this assumes that the files are big enough to reach the target "lines2get", which is not always the case (e.g. the new files can contains 1 line
                # instead of 10000)
                lines2get = int(lines2get*0.5)
            consumerSem.acquire()
            continue
        
        
        if normal:
            data = input_row_df.sample(n=lines2get, axis=0)
            input_row_df.drop(data.index, inplace=True)
        else:
            data = input_row_attack_df.sample(n=lines2get, axis=0)
            input_row_attack_df.drop(data.index, inplace=True)
        producerSem.release() #notify the producer we have freed some space in the buffer
        samplemutex.release()
        # if normal:
        #     print("DEBUG requiring", x, "rows and getting", len(data.index))
        return lines2get, data

    # samplemutex.acquire()
    # data = input_row_df.sample(n=int(10000*fraction))
    # input_row_df.drop(data.index, inplace=True)
    # samplemutex.release()
    # producerSem.release() #notify the producer we have freed some space in the buffer
    

def process_csv():
    global sparse_features
    global QUEUEDONE
    n = 0

    DEBUG_lines_wrote = 0
    DEBUG_lines_wrote_attack = 0

    while True:
        mutex.acquire()
        if QUEUEDONE:
            mutex.release()
            break
        mutex.release()
        
        n_sample, normal_data = get_sample(30000, True)
        test_normal_sample = normal_data.sample(frac = args.fraction, axis=0)
        train_normal_sample = normal_data.drop(index = test_normal_sample.index)
        
        n_sample_a, attack_data = get_sample(n_sample, False)
        test_attack_sample = attack_data.sample(frac = args.fraction, axis=0, replace=False)
        attack_data.drop(test_attack_sample.index, inplace=True)
        train_attack_sample = attack_data


        if test_normal_sample.empty or test_attack_sample.empty \
            or train_normal_sample.empty or test_attack_sample.empty:
            print("one of the dataset is empty, discarding...")
            continue
    
        test = pd.concat([test_normal_sample, test_attack_sample])
        train = pd.concat([train_normal_sample, train_attack_sample])

        df = pd.DataFrame()
        df = pd.concat([train, test])

        local_indexmax = {}
        local_indexmin = {}
        for key in sparse_features.keys():
            local_indexmax[key] = max(df[key])
            local_indexmin[key] = min(df[key])
        
        for key in sparse_features.keys():
            if local_indexmax[key] > sparse_features[key]["max"]:
                sparse_features[key]["max"] = local_indexmax[key]
            if local_indexmin[key] < sparse_features[key]["min"]:
                # print("Found index", local_indexmin[key], "lesser than", sparse_features[key]["min"], "for sparse feature", key)
                sparse_features[key]["min"] = local_indexmin[key]
            
        DEBUG_lines_wrote += len(test_normal_sample.index)
        DEBUG_lines_wrote += len(train_normal_sample.index)
        DEBUG_lines_wrote_attack += len(test_attack_sample.index)
        DEBUG_lines_wrote_attack += len(train_attack_sample.index)
        
        
        
        train.to_csv(os.path.join(args.output_path, f"train.{n}.csv"), index=False)
        test.to_csv(os.path.join(args.output_path, f"test.{n}.csv"), index=False)
        n += 1
        print("wrote to csv", DEBUG_lines_wrote, "samples of t traffic")
        print("wrote to csv", DEBUG_lines_wrote_attack, "samples of attack traffic")
        


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="split_data.py",
        description="Split data into training and testing dataset."
    )
    parser.add_argument("--input_path_normal", required=True)
    parser.add_argument("--input_path_attack", required=True)
    parser.add_argument("--output_path", required=True)
    parser.add_argument("--fraction", required=True, type=float) #fraction that will go in the test e.g. 0.3 = 70% train, 30% test

    args = parser.parse_args()

    input_path_queue = []
    input_path_attack_queue = []
    input_row_df = pd.DataFrame()
    input_row_attack_df = pd.DataFrame()
    sparse_features = {
        "SrcAddr": {"max": 0, "min": 65000},
        "DstAddr": {"max": 0, "min": 65000},
        "Sport": {"max": 0, "min": 65000},
        "Dport": {"max": 0, "min": 65000},
        "Proto": {"max": 0, "min": 65000},
        "State": {"max": 0, "min": 65000},
        "proto_state_and": {"max": 0, "min": 65000}
    }


    mutex = threading.Lock()
    
    producerSem = threading.Semaphore(0)
    consumerSem = threading.Semaphore(0)
    samplemutex = threading.Lock()
    for file in os.listdir(args.input_path_normal):
        if file.endswith(".csv"):
            input_path_queue.append(file)
    for file in os.listdir(args.input_path_attack):
        if file.endswith(".csv"):
                input_path_attack_queue.append(file)

    random.shuffle(input_path_queue)
    random.shuffle(input_path_attack_queue)


    threads = [threading.Thread(target=process_csv), threading.Thread(target=producer)]
    
    for i in range(2):
        threads[i].start()
    
    for i in range(2):
        threads[i].join()
        
    
    json.dump(sparse_features, open(os.path.join(args.output_path, "sparse_features_max_index.json"), "w"), indent="  ")
