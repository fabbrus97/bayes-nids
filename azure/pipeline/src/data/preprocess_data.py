import pandas as pd
import os

ROW_PER_FILE = 10000

def load_with_pandas(label, input_path, output_path):

    df_all = pd.DataFrame()

    for filename in os.listdir(os.path.join(input_path, "argus")):
        if not filename.endswith(".csv"):
            continue
        
        zeek_df = pd.pandas.read_csv(os.path.join(input_path, "zeek", filename), names=["uid","ts","is_sm_ips_ports","ct_state_ttl","ct_flw_http_mthd","is_ftp_login","ct_ftp_login","ct_srv_src","ct_srv_dst","ct_dst_ltm","ct_src_ltm","ct_src_dport_ltm","ct_dst_sport_ltm","ct_dst_src_ltm","is_telnet_login"])
        # print(zeek_df.head())

        zeek_df_grp = zeek_df.groupby('uid', group_keys=True, sort=False).max()
        # print(zeek_df_grp)

        argus_df = pd.pandas.read_csv(os.path.join(input_path, "argus", filename))
        # print(argus_df)

        df = argus_df.merge(zeek_df_grp, how="inner", left_on="StartTime", right_on="ts").sort_values("LastTime").drop("ts", axis=1)
        
        #    DATA TRANSFORMATION
        #from categorical data to enum ("tcp", "udp", "icmp",... => 1,2,3,...)
        #remove NaN from numerical data

        df['sTtl'] = df['sTtl'].fillna(0)
        df['dTtl'] = df['dTtl'].fillna(0)
        df['SrcWin'] = df['SrcWin'].fillna(0)
        df['DstWin'] = df['DstWin'].fillna(0)
        df['SrcTCPBase'] = df['SrcTCPBase'].fillna(0)
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
        
        df.insert(df.shape[1], "label", [label]*df.shape[0])

        for key in ["SrcBytes", "DstBytes", "SrcLoad", "DstLoad", "SrcJitter", "DstJitter", "SIntPkt", "DIntPkt", "TcpRtt", "SynAck", "AckDat"]:
            #binnig by quantile - each bin has the same amount of rows; we use  bins
            df[key] = pd.qcut(df[key], q=[0, .25, .5, .75, 1.], duplicates="drop", labels=False)

        
        # print(df.head())
        if df_all.count().empty:
            df_all = df
        else:
            pd.concat([df_all, df])
    
    # df_all['SrcAddr'] = pd.factorize(df['SrcAddr'])[0]
    # df_all['DstAddr'] = pd.factorize(df['DstAddr'])[0]
    # df_all['Sport'] = pd.factorize(df['Sport'])[0] #to eliminate NaN values
    # df_all['Dport'] = pd.factorize(df['Dport'])[0] #to eliminate NaN values
    # df_all['Proto'] = pd.factorize(df['Proto'])[0]
    df_all['State'] = pd.factorize(df['State'])[0]

    df_encoded = pd.get_dummies(df_all, columns=['SrcAddr', 'DstAddr', 'Proto', 'State'])

    start = 0
    index = 1
    df2write = df_encoded[start:start+ROW_PER_FILE]
    while (df2write.shape[0] >= ROW_PER_FILE):
        df2write.to_csv(f"{output_path}/raw_features-{index}.csv", index=False)
        index += 1
        start += ROW_PER_FILE
        df2write = df_encoded[start:start+ROW_PER_FILE]
    df_encoded[start:].to_csv(f"{output_path}/raw_features-{index}.csv", index=False)

    # df.to_csv("pandas.csv", index=False)

if __name__ == "__main__":
    #TODO parse input
    load_with_pandas("normal", "input", "output")
