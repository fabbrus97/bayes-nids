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
from scipy.spatial.distance import squareform

MAX_FILE_INPUT = 20

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

    X_train, X_val, y_train, y_val = train_test_split(
        df, df['label'], random_state=42, test_size=0.3)
        #df, test_size=0.2, random_state=42, shuffle=True)
    
    X_train.drop("label", inplace=True, axis=1)
    X_val.drop("label", inplace=True, axis=1)
    

    X_train_sel = X_train[selected_features_names]
    X_test_sel = X_val[selected_features_names]

    model = BernoulliNB().fit(X_train, y_train)
    model.fit(X_train_sel, y_train)
    
    print(
        "Baseline accuracy on test data with features removed:"
        f" {model.score(X_test_sel, y_val):.2}"
    )






    # print("pfi: training model")
    # X_train, X_val, y_train, y_val = train_test_split(
    #     df, df['label'], random_state=42, test_size=0.3)
    #     #df, test_size=0.2, random_state=42, shuffle=True)
    
    # X_train.drop("label", inplace=True, axis=1)
    # X_val.drop("label", inplace=True, axis=1)
    # print(X_train)

    # # model = Ridge(alpha=1e-2).fit(X_train, y_train)
    # model = BernoulliNB().fit(X_train, y_train)
    # print("computing scores")
    # score = model.score(X_val, y_val)
    # print("Model score:", score)

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
    sns.heatmap(df_mutual_information, annot=True, cmap=plt.cm.Reds, annot_kws={'fontsize': 5})
    plt.show()


    # We convert the correlation matrix to a distance matrix before performing
    # hierarchical clustering using Ward's linkage.
    distance_matrix = 1 - np.abs(df_mutual_information)
    dist_linkage = hierarchy.ward(distance_matrix)    
    return dist_linkage #TODO
    # dist_linkage = hierarchy.ward(squareform(distance_matrix))    

    # print(df_mutual_information)
    for col in df_mutual_information.columns:
        print(col)
        # print(df_mutual_information.loc[col]["label"])
        if df_mutual_information.loc[col]["label"] < args.value:
            print("val too low, dropping", col)
            df_mutual_information.drop(col, inplace=True)
            df_mutual_information.drop(col, axis=1, inplace=True)

        elif col != "label" and not df_mutual_information[col].any():
            print("all nan, dropping", col)
            # print(df_mutual_information.loc[col])
            df_mutual_information.drop(col, inplace=True, axis=1)
            # print("now df is")
            # print(df_mutual_information)
            
            # continue

    print(df_mutual_information)
    

    plt.figure(figsize=(20, 18))
    # sns.heatmap(df_mutual_information, annot=True, cmap=plt.cm.Reds)
    sns.heatmap(df_mutual_information, annot=True, cmap=plt.cm.Reds, annot_kws={'fontsize': 5})
    # plt.show()
    plt.savefig(os.path.join("filter_output", "infogain_with_corr_feats.png"))
    df_mutual_information.to_csv(os.path.join("filter_output", "infogain_with_corr_feats.csv")) #TODO
   
    #remove mutual correlated features
    rows2delete = set()
    for row in df_mutual_information.index.to_list():
        if row == "label":
            continue
        for col in df_mutual_information.columns.to_list():
            
            print("examining row, col:", row, col)
            
            if col == df_mutual_information.columns[-1]: #"label":
                print("label col found, skipping")
                continue
            if row == col:
                print("row==col, skipping")
                continue

            if df_mutual_information.loc[row][col] > 0.7: #made up value for correlation 
                #the variable row is correlated with col
                print("they are correlated! value:", df_mutual_information.loc[row][col])
                if df_mutual_information.loc[row]["label"] < df_mutual_information.loc[col]["label"]:
                    print(row, "is the least correlated with label:", df_mutual_information.loc[row]["label"], "vs", df_mutual_information.loc[col]["label"])
                    # df_mutual_information.drop(row, inplace=True)
                    rows2delete.add(row)
                else:
                    # df_mutual_information.drop(col, inplace=True)
                    print(col, "is the least correlated with label:", df_mutual_information.loc[col]["label"], "vs", df_mutual_information.loc[row]["label"])
                    rows2delete.add(col)

    print("rows2delete:", rows2delete)

    for i in rows2delete:
        df_mutual_information.drop(i, inplace=True)
  
    print(df_mutual_information)
    # input()

    plt.figure(figsize=(20, 18))
    # sns.heatmap(df_mutual_information, annot=True, cmap=plt.cm.Reds)
    sns.heatmap(df_mutual_information, annot=True, cmap=plt.cm.Reds, annot_kws={'fontsize': 5})
    # plt.show()
    plt.savefig(os.path.join("filter_output", "infogain.png"))
    df_mutual_information.to_csv(os.path.join("filter_output", "infogain.csv")) #TODO make folder filter_output
    feature_list_file = open(os.path.join("filter_output", "feature_list.txt"), "w")
    feature_list_file.write(",".join([i[0] for i in df_mutual_information.index.values.tolist()]) + "\n")
    return df_mutual_information.index


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="filter_features.py",
        description="Filter most important features."
    )
    parser.add_argument("--input_path", required=True)
    parser.add_argument("--output_path", required=True)
    parser.add_argument("--value", required=False, default=0.5, type=float) #remove features with importance score less than this value
    parser.add_argument("--method", required=True, choices=["infogain", "pfi", "all"])
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

    df['label'], _ = pd.factorize(df['label'])


    if args.method == "infogain":
        information_gain()
    elif args.method == "pfi":
        permutation_feature_importance([])
    else:
        features = information_gain()
        permutation_feature_importance(features)
