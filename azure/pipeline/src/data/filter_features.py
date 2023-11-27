from sklearn.model_selection import train_test_split
from sklearn.feature_selection import mutual_info_classif
from sklearn import preprocessing
# from sklearn.linear_model import Ridge
from sklearn.naive_bayes import BernoulliNB
from sklearn.inspection import permutation_importance
import argparse
import pandas as pd
import os
from matplotlib import pyplot as plt
import seaborn as sns
import threading
import numpy as np
from scipy.cluster import hierarchy
from collections import defaultdict
import json

MAX_FILE_INPUT = 20

def plot_permutation_importance(result, X, ax):
    perm_sorted_idx = result.importances_mean.argsort()[-5:] #get only top 5
    print(perm_sorted_idx)

    ax.boxplot(
        result.importances[perm_sorted_idx].T,
        vert=False,
        labels=X.columns[perm_sorted_idx],
    )
    ax.axvline(x=0, color="k", linestyle="--")
    return ax

def permutation_feature_importance(dist_linkage):
    global df
    
    """
    for col in df.columns:
        if col == "label":
            continue
        if col not in features:
            df.drop(columns=col, inplace=True)    
    """
    cluster_ids = hierarchy.fcluster(dist_linkage, 1, criterion="distance")
    cluster_id_to_feature_ids = defaultdict(list)
    for idx, cluster_id in enumerate(cluster_ids):
        cluster_id_to_feature_ids[cluster_id].append(idx)
    selected_features = [v[0] for v in cluster_id_to_feature_ids.values()]
    selected_features_names = df.columns[selected_features]
   # selected_features_names="SrcLoad,DstPkts,DstTCPBase,SrcWin,SrcPkts,State,SrcBytes,dTtl,SrcLoss,SrcAddr,DstBytes".split(",")

    X_train, X_val, y_train, y_val = train_test_split(
        df, df['label'], random_state=42, test_size=0.3)
        #df, test_size=0.2, random_state=42, shuffle=True)
    
    X_train.drop("label", inplace=True, axis=1)
    X_val.drop("label", inplace=True, axis=1)
    

    X_train_sel = X_train[selected_features_names]
    X_val_sel = X_val[selected_features_names]

    model = BernoulliNB()
    model.fit(X_train_sel, y_train)
    
    print(
        "Baseline accuracy on test data with features removed:"
        f" {model.score(X_val_sel, y_val):.2}"
    )

    r = permutation_importance(model, X_val_sel, y_val,
                               n_repeats=30,
                               random_state=0,
                               n_jobs=args.nthreads)
    print("done, output...")
    
    final_features = []

    for i in r.importances_mean.argsort()[::-1]:
        if r.importances_mean[i] - 2 * r.importances_std[i] > 0:
            final_features.append(selected_features_names[i])

            print(f"{selected_features_names[i]:<8}"
                  f"{r.importances_mean[i]:.3f}"
                  f" +/- {r.importances_std[i]:.3f}")
    
    filter_features = open(os.path.join(args.output_path, "feature_list.txt"), "w")
    for ft in final_features:
        filter_features.write(f"{ft},")
    filter_features.write("\n")
    filter_features.close()
    
    r_list = {}

    r_list["importances_mean"] = r["importances_mean"].tolist()
    r_list["importances_std"] = r["importances_std"].tolist()
    r_list["importances"] = r["importances"].tolist()
    json.dump(r_list, open(os.path.join(args.output_path, "permutation_feature_importance.json"), "w"))

    fig, ax = plt.subplots(figsize=(7, 6))
    plot_permutation_importance(r, X_val_sel, ax)
    ax.set_title("Permutation Importances on selected subset of features\n(test set)")
    ax.set_xlabel("Decrease in accuracy score")
    ax.figure.tight_layout()
    plt.savefig(os.path.join(args.output_path, "permutation_feature_importance.png"))



def infogain_thread(df, columns):
    counter = 1
    maxfeatures = len(columns)
    discrete_feature_bitmask = [False if dtype == "float64" else True for dtype in df.dtypes]
    for col in columns:
        print("infogain_thread: computing for column", col, "of type", df[col].dtype, f"({counter}/{maxfeatures})")
        if df[col].dtype == "float64":
            # NOTE a logistic regression model requires the values of the response variable to be categorical
            lab = preprocessing.LabelEncoder()
            y_transformed = lab.fit_transform(df[col])
            mi = mutual_info_classif(df, y_transformed, random_state=42, discrete_features=discrete_feature_bitmask)
        else:
            mi = mutual_info_classif(df, df[col], random_state=42, discrete_features=discrete_feature_bitmask)
        try:
            df_mutual_information[col] = mi
        except Exception as e:
            print(e)
            print("the offending vector is:")
            print(mi)
        counter += 1

def information_gain():
    global df_mutual_information
    global df
    
    print("Splitting dataset")
    X, _, y, _ = train_test_split(
        df, df['label'], random_state=42)

    cols_per_thread = int(len(X.columns)/args.nthreads) + 1
    
    if args.nthreads > 1:
        df_mutual_information = pd.DataFrame(columns=[df.columns], index=[df.columns])
        # print("My index are:", df_mutual_information.index)
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

    plt.figure(figsize=(20, 18))
    # sns.heatmap(df_mutual_information, annot=True, cmap=plt.cm.Reds)
    sns.heatmap(df_mutual_information, annot=True, cmap=plt.cm.Reds, annot_kws={'fontsize': 5})
    # plt.show()
    plt.savefig(os.path.join(args.output_path, "mutual_information_gain.png"))

    df_mutual_information.to_csv(os.path.join(args.output_path, "mutual_information_gain.csv"))

    # We convert the correlation matrix to a distance matrix before performing
    # hierarchical clustering using Ward's linkage.
    distance_matrix = 1 - np.abs(df_mutual_information)
    dist_linkage = hierarchy.ward(distance_matrix)    



    return dist_linkage #TODO

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="filter_features.py",
        description="Filter most important features."
    )
    parser.add_argument("--input_path", required=True)
    parser.add_argument("--output_path", required=True)
    parser.add_argument("--nthreads", required=False, default=1, type=int)

    args = parser.parse_args()

    df_mutual_information = pd.DataFrame()
    df = pd.DataFrame()
    print("preparing dataset")
    file_read = 0
    for file in os.listdir(args.input_path):
        if file.endswith(".csv"):
            print("opening", file)
            _df = pd.read_csv(os.path.join(args.input_path, file), dtype={"label": 'string', "sTtl": "int64", "dTtl": "int64", "Trans": "int64", "SrcTCPBase": "int64", "DstTCPBase": "int64"})
            df = pd.concat([df, _df])
            file_read += 1
            if file_read > MAX_FILE_INPUT:
                break
    # print(df["label"].value_counts())
    # input()
    
    print(df)
    df['label'], _ = pd.factorize(df['label'])


    features = information_gain()
    permutation_feature_importance(features)
