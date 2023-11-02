import argparse
import pandas as pd
import os
import threading
import itertools

# ROW_PER_FILE = 15000

def convert_port(data):
    port = 0
    try:
        port = int(data)
    except:
        pass
    return port

def fake_one_hot_encoding():
    """
    due to the huge amount of values to encode, this is actually a "factorization" (as in pd.factorize), 
    but the bayes model will use a weight not for the e.g. "SrcAddr" attribute, but instead will use a weight
    for every address (SrcAddr192.168.1.1, SrcAddr10.0.0.1, ...) as in an one hot encoding setting.
    """
    output_path = args.output_path
    
    while True:
        filename = None
        mutex.acquire()
        hasWork = False
        if len(input_path_queue) > 0:
            filename = input_path_queue.pop()
            hasWork = True
            print(len(input_path_queue), "files missing, now working on", filename)
        mutex.release()

        if not hasWork:
            break
        
        max_proto = len(variables2encode["Proto"].keys())
        # max_state = max(variables2encode["State"])
        df = pd.read_csv(os.path.join(output_path, filename))
        for key in variables2encode.keys():
            print("substituting values with index for key", key)
            df[key] = df[key].apply(lambda x: variables2encode[key][x]) #substitute each value with an index 0..n
            print("key", key, "done")

            # vals2process = len(variables2encode[key])
            # counter = 0
            # for val in variables2encode[key]: 
            #     print("processing  val", val, "key", key, counter, "/", vals2process, "file:", filename)
            #     counter += 1
            #     newcol = [int(x == val) for x in df[key]] #df[key].str.contains(val)
                
            #     df = pd.concat([df, pd.DataFrame(columns=[f"{key}{val}"],
            #                 data = newcol)],   # [],
            #                 axis=1)                  
            # df.drop(labels=[key], axis=1)
        df.insert(len(df.columns) - 1, "proto_state_and", list(df[["Proto", "State"]].itertuples(index=False, name=None)))
        df["proto_state_and"] = df["proto_state_and"].apply(lambda x: 
                                max_proto*x[0] + x[1]) #substitute each value with an index 0..n

        df.to_csv(os.path.join(output_path, filename), index=False)


def load_with_pandas():
    global counter

    label = args.traffic_type
    input_path = args.input_path
    output_path = args.output_path

    while True:
        filename = None
        mutex.acquire()
        n = counter
        counter += 1
        hasWork = False
        if len(input_path_queue) > 0:
            filename = input_path_queue.pop()
            hasWork = True
            # print(len(input_path_queue), "files missing, now working on", filename)
        mutex.release()

        if not hasWork:
            break

        zfilename = filename.replace("-argus", "-zeek")
        zeek_df = pd.pandas.read_csv(os.path.join(input_path, zfilename), names=["uid","ts","is_sm_ips_ports","ct_state_ttl","ct_flw_http_mthd",
                    "is_ftp_login","ct_ftp_login","ct_srv_src","ct_srv_dst",
                    "ct_dst_ltm","ct_src_ltm","ct_src_dport_ltm","ct_dst_sport_ltm",
                    "ct_dst_src_ltm"], dtype={"ts": 'float64'})
        # print(zeek_df.head())


        zeek_df_grp = zeek_df.groupby('uid', group_keys=True, sort=False).max()
        zeek_df_grp.drop_duplicates(subset="ts", keep="last", inplace=True)
        # print(zeek_df_grp)

        argus_df = pd.pandas.read_csv(os.path.join(input_path, filename), header=0,
                converters = {'Sport': convert_port, 'Dport': convert_port},
                dtype={'StartTime':'float64','LastTime':'float64'})
        # print(argus_df)

        df = argus_df.join(zeek_df_grp.set_index("ts"), how="inner", on="StartTime") #.sort_values("LastTime") #.drop("ts", axis=1)
        # df = argus_df.merge(zeek_df_grp, how="inner", left_on="StartTime", right_on="ts").sort_values("LastTime").drop("ts", axis=1)

        #    DATA TRANSFORMATION
        #from categorical data to enum ("tcp", "udp", "icmp",... => 1,2,3,...)
        #remove NaN from numerical data


        df['sTtl'] = df['sTtl'].fillna(0)
        df['dTtl'] = df['dTtl'].fillna(0)
        df['SrcWin'] = df['SrcWin'].fillna(0)
        df['DstWin'] = df['DstWin'].fillna(0)
        df['SrcTCPBase'] = df['SrcTCPBase'].fillna(0)
        df['TcpRtt'] = df['TcpRtt'].fillna(0)
        df['DstTCPBase'] = df['DstTCPBase'].fillna(0)
        df['SrcJitter'] = df['SrcJitter'].fillna(0)
        df['DstJitter'] = df['DstJitter'].fillna(0)
        df['SIntPkt'] = df['SIntPkt'].fillna(0)
        df['DIntPkt'] = df['DIntPkt'].fillna(0)
        df['Trans'] = df['Trans'].fillna(0)
        df['Min'] = df['Min'].fillna(0)
        df['Max'] = df['Max'].fillna(0)
        df['Sum'] = df['Sum'].fillna(0)
        df['Sport'] = df['Sport'].fillna(0)
        df['Dport'] = df['Dport'].fillna(0)
        df['SynAck'] = df['SynAck'].fillna(0)
        df['AckDat'] = df['AckDat'].fillna(0)

        #l = 0
        #if label == "attack":
        #    l = 1
        #df.insert(df.shape[1], "label", [l]*df.shape[0])
        df.insert(df.shape[1], "label", [label]*df.shape[0])
        
        print("computing quantiles for", filename)
        for key in ["SrcBytes", "DstBytes", "SrcLoad", "DstLoad", "SrcJitter", "DstJitter", "SIntPkt", "DIntPkt", "TcpRtt", "SynAck", "AckDat"]:
            if df[key].empty or (df[key] == 0).all():
                print("cannot compute quantile for key", key, "empty axis")
                df[key] = 0
                continue
            #binnig by quantile - each bin has the same amount of rows; we use  bins
            df[key] = pd.qcut(df[key], q=[0, .25, .5, .75, 1.], duplicates="drop", labels=False)

        # print(df.head())
        #if df_all.count().empty:
        #    df_all = df
        #else:
        #    df_all = pd.concat([df_all, df])
        
        print("writing csv", n)
        df.to_csv(os.path.join(output_path, f"raw_traffic_{label}.{n}.csv"), index=False)
        df.to_csv(f"{output_path}/raw_traffic_{label}.{n}.csv", index=False)
        
        vals = {}
        for key in variables2encode.keys():
            #print("adding unique values to set for key", key, "and file", filename)
            vals[key] = set(df[key].unique())
        
        
        var2encMut.acquire()
        for key in vals.keys():
            variables2encode[key].update(vals[key])
        var2encMut.release()


        # df_encoded = pd.get_dummiess(list(variables2encode["SrcAddr"]))
        # print(df_encoded)

    # df_all['SrcAddr'] = pd.factorize(df['SrcAddr'])[0]
    # df_all['DstAddr'] = pd.factorize(df['DstAddr'])[0]
    # df_all['Sport'] = pd.factorize(df['Sport'])[0] #to eliminate NaN values
    # df_all['Dport'] = pd.factorize(df['Dport'])[0] #to eliminate NaN values
    # df_all['Proto'] = pd.factorize(df['Proto'])[0]
    # df_all['State'] = pd.factorize(df_all['State'])[0]


    # df_encoded = pd.get_dummies(df_all, columns=['SrcAddr', 'DstAddr', 'Proto', 'State'])

    # start = 0
    # index = 1
    # df2write = df_encoded[start:start+ROW_PER_FILE]
    # print("\nstart writing data...")
    # while (df2write.shape[0] >= ROW_PER_FILE):
    #     df2write.to_csv(f"{output_path}/raw_traffic_{label}.{index}.csv", index=False)
    #     index += 1
    #     start += ROW_PER_FILE
    #     df2write = df_encoded[start:start+ROW_PER_FILE]
    #     print("written", start, "rows")
    # df_encoded[start:].to_csv(f"{output_path}/raw_traffic_{label}.{index}.csv", index=False)

    # df.to_csv("pandas.csv", index=False)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="preprocess_data.py",
        description="This script loads a folder that contains csv files generated by \
                    zeek and argus and merges them togheter."
    )
    parser.add_argument("--input_path", required=True)
    parser.add_argument("--output_path", required=True)
    parser.add_argument("--traffic_type", required=True, choices=['normal', 'attack'])
    parser.add_argument("--nthreads", required=False, type=int, default=1)

    args = parser.parse_args()

    input_path_queue = []
    counter = 0
    variables2encode = {
            "SrcAddr": set(),
            "DstAddr": set(),
            "Sport": set(),
            "Dport": set(),
            "Proto": set(),
            "State": set()
    }

    mutex = threading.Lock()
    var2encMut = threading.Lock()
    for file in os.listdir(args.input_path):
        if file.find("argus") > 0 and file.endswith(".csv"):
            print("adding filename", file, "to queue")
            input_path_queue.append(file)
    threads = [threading.Thread(target=load_with_pandas) for i in range(args.nthreads)]

    for i in range(args.nthreads):
        threads[i].start()

    for i in range(args.nthreads):
        threads[i].join()

    #first step done - executing second step to one-hot encode categorical data
    print("starting one-hot encoding...")

    # proto_state_and = list(itertools.product(variables2encode["Proto"], variables2encode["State"]))
    # variables2encode["proto_state_and"] = proto_state_and

    for key in variables2encode.keys():
        # variables2encode[key] = list(variables2encode[key])
        print(key, "to encode:", len(variables2encode[key]))
        variables2encode[key] = {variables2encode[key].pop(): i for i in range(0, len(variables2encode[key]))}
    
    for file in os.listdir(args.output_path):
        if file.endswith(".csv"):
            input_path_queue.append(file)
    threads = [threading.Thread(target=fake_one_hot_encoding) for i in range(args.nthreads)]

    for i in range(args.nthreads):
        print("starting thread", i)
        threads[i].start()

    for i in range(args.nthreads):
        threads[i].join()

    # load_with_pandas(args.traffic_type, args.input_path, args.output_path)
