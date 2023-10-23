from sklearn.model_selection import train_test_split
from sklearn.linear_model import Ridge
from sklearn.inspection import permutation_importance
import argparse
import pandas as pd
import os
from matplotlib import pyplot as plt
import seaborn as sns

PEARS_CORR_FILENAME = "pearson_corr_relevant_features.csv"

def permutation_feature_importance():
    df = pd.DataFrame()
    for file in os.listdir(args.input_path):
        if file.endswith(".csv"):
             _df = pd.read_csv(os.path.join(args.input_path, file))
            # TODO drop columns 
             pd.concat(df, _df)

    X_train, X_val, y_train, y_val = train_test_split(
        df, test_size=0.2, random_state=42, shuffle=True)
    
    model = Ridge(alpha=1e-2).fit(X_train, y_train)
    model.score(X_val, y_val)

    r = permutation_importance(model, X_val, y_val,
                               n_repeats=30,
                               random_state=0)
    for i in r.importances_mean.argsort()[::-1]:
        if r.importances_mean[i] - 2 * r.importances_std[i] > 0:
            print(f"{df.columns[i]:<8}"
                  f"{r.importances_mean[i]:.3f}"
                  f" +/- {r.importances_std[i]:.3f}")
    
    #TODO write output to csv

def pearson_correlation():
    df = pd.DataFrame()
    for file in os.listdir(args.input_path):
        if file.endswith(".csv"):
             _df = pd.read_csv(os.path.join(args.input_path, file))
            # TODO drop columns 
             pd.concat(df, _df)
    cor = df.corr()
    sns.heatmap(cor, annot=True, cmap=plt.cm.Reds)
    plt.savefig(os.path.join(args.outputh_path, "pearson_correlation.jpg"))

    cor_target = abs(cor["label"])
    relevant_features = cor_target[cor_target>0.5]
    #NOTE do we need to drop features correlating with each other?

    relevant_features.to_csv(os.path.join(args.outputh_path, PEARS_CORR_FILENAME))
    #TODO how is this file formatted?

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="split_data.py",
        description="Split data into training and testing dataset."
    )
    parser.add_argument("--input_path", required=True)
    parser.add_argument("--output_path", required=True)
    parser.add_argument("--method", required=True, range=["pearson", "pfi"])

    args = parser.parse_args()

    if args.method == "pearson":
        pearson_correlation()
    else:
        permutation_feature_importance()
