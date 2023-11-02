import sklearn
import argparse
import pandas as pd
import os
import threading

def process_csv():
    global counter
    while True:
        file = None
        file_attack = None
        mutex.acquire()
        n = counter
        counter += 1
        hasWork = False
        if len(input_path_queue) > 0:
            file = input_path_queue.pop()
            hasWork = True
        if len(input_path_attack_queue) > 0:
            file_attack = input_path_attack_queue.pop()
            hasWork = True
        mutex.release()

        if not hasWork:
            break
    
        df = pd.DataFrame()
    
        if file is not None:
            df_normal = pd.read_csv(os.path.join(args.input_path, file))
            pd.concat(df, df_normal)
        if file_attack is not None:
            df_attack = pd.read_csv(os.path.join(args.input_path, file_attack))
            df = pd.concat([df, df_attack])
    
        test  = df.sample(frac=args.fraction)
        train = df.drop(test.index)
    
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
    parser.add_argument("--nthreads", required=False, type=int, default=1)

    args = parser.parse_args()

    input_path_queue = []
    input_path_attack_queue = []
    counter = 0

    mutex = threading.Lock()
    for file in os.listdir(args.input_path):
        if file.endswith(".csv"):
            if file.find("attack"):
                input_path_attack_queue.append(file)
            else:
                input_path_queue.append(file)

    threads = [threading.Thread(target=process_csv) for i in range(args.nthreads)]
    
    for i in range(args.nthreads):
        threads[i].start()
    
    for i in range(args.nthreads):
        threads[i].join()
    
