from sklearn.model_selection import train_test_split
from sklearn.feature_selection import mutual_info_classif
# from sklearn.linear_model import Ridge
from sklearn.naive_bayes import GaussianNB
from sklearn.inspection import permutation_importance
import argparse
import pandas as pd
import os
from matplotlib import pyplot as plt
import seaborn as sns
import threading

PEARS_CORR_FILENAME = "pearson_corr_relevant_features.csv"


def permutation_feature_importance(features):
    df = pd.DataFrame()
    print("preparing dataset")
    for file in os.listdir(args.input_path):
        if file.endswith(".csv"):
             _df = pd.read_csv(os.path.join(args.input_path, file))
             if features != None:
                _df = _df. loc[:, features]
                # _df = _df. loc[:, ['SrcAddr', 'Sport', 'DstAddr', 'Dport']]
             tmp = _df["Dport"].copy()
             tmp = tmp.apply(lambda x: 1 if x == 4 else 2)
            #  tmp = tmp.apply(lambda x: 1 if x < 5 else 2)
             _df["label"] = tmp
             df = pd.concat([df, _df])
    # df['label'] = 1 if df["SrcAddr"] < 5 else 2#.replace("normal", random.randint(1, 2), inplace=True)
    
    print(df)
    # print(df["Dport"].value_counts())
    print(df["label"].value_counts())
    input()

    print("training model")
    X_train, X_val, y_train, y_val = train_test_split(
        df, df['label'], random_state=42)
        #df, test_size=0.2, random_state=42, shuffle=True)
    
    # model = Ridge(alpha=1e-2).fit(X_train, y_train)
    model = GaussianNB().fit(X_train, y_train)
    print("computing scores")
    model.score(X_val, y_val)

    r = permutation_importance(model, X_val, y_val,
                               n_repeats=30,
                               random_state=0)
    print("done, output...")
    # print(r)
    for i in r.importances_mean.argsort()[::-1]:
        if r.importances_mean[i] - 2 * r.importances_std[i] > 0:
            print(f"{df.columns[i]:<8}"
                  f"{r.importances_mean[i]:.3f}"
                  f" +/- {r.importances_std[i]:.3f}")
    
    #TODO write output to csv

def infogain_thread(df, columns):
    counter = 1
    maxfeatures = len(columns)
    discrete_feature_bitmask = [False if dtype == "float64" else True for dtype in df.dtypes]
    for col in columns:
        print("infogain_thread: computing for column", col, "of type", df[col].dtype, f"({counter}/{maxfeatures})")
        #TODO some columns are seen as float, but in fact are not (e.g. ttl)
        if df[col].dtype == "float64":
            mi = 0
        else:
            mi = mutual_info_classif(df, df[col], random_state=42, discrete_features=discrete_feature_bitmask)
        df_mutual_information[col] = mi
        counter += 1

def information_gain():
    global df_mutual_information

    df = pd.DataFrame()
    print("preparing dataset")
    for file in os.listdir(args.input_path):
        if file.endswith(".csv"):
             _df = pd.read_csv(os.path.join(args.input_path, file))
            #  _df = _df.loc[:, ['SrcAddr', 'Sport', 'DstAddr', 'Dport']]
             tmp = _df["SrcAddr"].copy()
             tmp = tmp.apply(lambda x: 1 if x <10 else 2)
            #  tmp = tmp.apply(lambda x: 1 if x < 5 else 2)
             _df["label"] = tmp
             df = pd.concat([df, _df])
    # df['label'] = 1 if df["SrcAddr"] < 5 else 2#.replace("normal", random.randint(1, 2), inplace=True)
    
    # print(df)
    # # print(df["Dport"].value_counts())
    # print(df["label"].value_counts())
    # input()

    print("Splitting dataset")
    X, _, y, _ = train_test_split(
        df, df['label'], random_state=42)

    cols_per_thread = int(len(X.columns)/args.nthreads) + 1

    if args.nthreads > 1:
        df_mutual_information = pd.DataFrame(columns=[df.columns], index=[df.columns])
        threads = [
            threading.Thread(
                target=infogain_thread, 
                args=[X, X.columns[i:i+cols_per_thread]]
            ) 
            for i in range(0, len(X.columns), cols_per_thread)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
    else:
        infogain_thread(X, X.columns)
    # for col in X.columns:
        # mi = mutual_info_classif(X, X[col], random_state=42)
        # print(mi)
        # df_mi[col] = mi
    df_mutual_information = (df_mutual_information-df_mutual_information.min())/(df_mutual_information.max()-df_mutual_information.min())
    print(df_mutual_information)
    for col in df_mutual_information.columns:
        # print(col)
        # print(df_mutual_information.loc[col]["label"])
        if not df_mutual_information[col].any():
            print("dropping", col)
            df_mutual_information.drop(col, inplace=True, axis=1)
            # df_mutual_information.drop(col, axis=1, inplace=True)
            continue
        if df_mutual_information.loc[col]["label"] < 0.05: #TODO
            df_mutual_information.drop(col, inplace=True)
            df_mutual_information.drop(col, axis=1, inplace=True)

    print(df_mutual_information)
    input()

    plt.figure(figsize=(12, 10))
    sns.heatmap(df_mutual_information, annot=True, cmap=plt.cm.Reds)
    # sns.heatmap(df_mutual_information, annot=True, cmap=plt.cm.Reds, annot_kws={'fontsize': 5})
    plt.show()
    

"""
NOTE features should be uncorrelated between them! TODO
"""
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="split_data.py",
        description="Split data into training and testing dataset."
    )
    parser.add_argument("--input_path", required=True)
    parser.add_argument("--output_path", required=True)
    parser.add_argument("--method", required=True, choices=["infogain", "pfi", "all"])
    parser.add_argument("--nthreads", required=False, default=1, type=int)

    args = parser.parse_args()

    df_mutual_information = pd.DataFrame()

    if args.method == "infogain":
        information_gain()
    elif args.method == "pfi":
        permutation_feature_importance()
    else:
        #TODO
        features = information_gain()
        permutation_feature_importance(features)
