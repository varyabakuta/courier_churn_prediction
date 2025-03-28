# -*- coding: utf-8 -*-
"""Churn model proof of concept Bakuta.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1FWISoyHlZk_Tmvn78m5XxkbFjD-SHEPz

# Data import
"""

import pandas as pd

def load_and_fix_dates(input_path: str, output_path: str) -> None:
    """
    Loads a dataset from an Excel file, converts the 'first_order_delivered' column
    from Unix day counts to datetime format, and saves the updated dataset to a new Excel file.

    Parameters:
    ----------
    input_path : str
        Path to the original Excel file.
    output_path : str
        Path where the corrected Excel file will be saved.
    """
    # Step 1: Load the dataset from the Excel file
    df = pd.read_excel(input_path)

    # Step 2: Convert 'first_order_delivered' from Unix day format to datetime
    df['first_order_delivered'] = pd.to_datetime(
        df['first_order_delivered'], origin='1970-01-01', unit='D'
    )

    # Step 3: Print a preview of the converted dates
    print(df[['first_order_delivered']].head())

    # Step 4: Save the updated DataFrame to a new Excel file
    df.to_excel(output_path, index=False)

    print("DataFrame successfully loaded and corrected.")


# Example usage
load_and_fix_dates(
    input_path="churn_w_features.xlsx",
    output_path="churn_w_features_fixed.xlsx"
)

"""# EDA"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.cross_decomposition import PLSRegression
from sklearn.preprocessing import StandardScaler


def load_and_clean_dataset(file_path: str) -> pd.DataFrame:
    """
    Loads the dataset, handles missing values and placeholder values,
    and prepares the data for further analysis.

    Parameters
    ----------
    file_path : str
        Path to the Excel file.

    Returns
    -------
    pd.DataFrame
        Cleaned dataset.
    """
    df = pd.read_excel(file_path)

    # Drop irrelevant or deprecated columns
    df.drop(columns=[
        "churn_days", "days_since_last_order",
        "life_time_days_cnt", "life_time_order_cnt"
    ], inplace=True, errors="ignore")

    # Replace invalid values (-1e6, 1e6) with 0 in specified features
    placeholder_cols = [
        "max_order_cpo_14d", "max_order_cpo_30d", "max_order_cpo_3d", "max_order_cpo_7d",
        "min_order_cpo_14d", "min_order_cpo_30d", "min_order_cpo_3d", "min_order_cpo_7d"
    ]
    df[placeholder_cols] = df[placeholder_cols].replace({-1_000_000: 0, 1_000_000: 0})

    # Define numeric features for imputation
    numeric_features = [
        "active_days_14d", "active_days_30d", "active_days_3d", "active_days_7d",
        "age",
        "avg_order_cpo_14d", "avg_order_cpo_30d", "avg_order_cpo_3d", "avg_order_cpo_7d",
        "avg_trip_distance_14d", "avg_trip_distance_30d", "avg_trip_distance_3d", "avg_trip_distance_7d",
        "max_order_cpo_14d", "max_order_cpo_30d", "max_order_cpo_3d", "max_order_cpo_7d",
        "min_order_cpo_14d", "min_order_cpo_30d", "min_order_cpo_3d", "min_order_cpo_7d",
        "num_orders_14d", "num_orders_30d", "num_orders_3d", "num_orders_7d",
        "num_orders_total",
        "orders_friday", "orders_monday", "orders_saturday", "orders_sunday",
        "orders_thursday", "orders_tuesday", "orders_wednesday",
        "total_income_14d", "total_income_30d", "total_income_3d", "total_income_7d",
        "weekend_orders_ratio"
    ]

    # Fill missing numeric values with zero
    df[numeric_features] = df[numeric_features].fillna(0)

    # Fill missing values in categorical columns
    df["hiring_channel_name"] = df["hiring_channel_name"].fillna("Unknown")

    return df


def explore_data(df: pd.DataFrame) -> None:
    """
    Performs exploratory data analysis (EDA) on the dataset,
    including basic stats, distribution plots, and correlation analysis.

    Parameters
    ----------
    df : pd.DataFrame
        The input cleaned dataset.
    """
    print("Dataset Overview:")
    print(df.info())

    print("\nMissing Values:")
    print(df.isnull().sum())

    # Churn distribution
    plt.figure(figsize=(6, 4))
    sns.countplot(x=df["churn_flag"], palette="Set2")
    plt.title("Churn Flag Distribution (0 = Active, 1 = Churn)")
    plt.show()

    # Categorical feature distribution by churn
    categorical_features = ["movement_type", "hiring_channel_name", "region_id"]
    for col in categorical_features:
        plt.figure(figsize=(8, 4))
        sns.countplot(y=df[col], hue=df["churn_flag"], palette="Set2")
        plt.title(f"Distribution of {col} by Churn")
        plt.show()

    # Redefine numeric features to reuse
    numeric_features = [
        "active_days_14d", "active_days_30d", "active_days_3d", "active_days_7d",
        "age",
        "avg_order_cpo_14d", "avg_order_cpo_30d", "avg_order_cpo_3d", "avg_order_cpo_7d",
        "avg_trip_distance_14d", "avg_trip_distance_30d", "avg_trip_distance_3d", "avg_trip_distance_7d",
        "max_order_cpo_14d", "max_order_cpo_30d", "max_order_cpo_3d", "max_order_cpo_7d",
        "min_order_cpo_14d", "min_order_cpo_30d", "min_order_cpo_3d", "min_order_cpo_7d",
        "num_orders_14d", "num_orders_30d", "num_orders_3d", "num_orders_7d",
        "num_orders_total",
        "orders_friday", "orders_monday", "orders_saturday", "orders_sunday",
        "orders_thursday", "orders_tuesday", "orders_wednesday",
        "total_income_14d", "total_income_30d", "total_income_3d", "total_income_7d",
        "weekend_orders_ratio"
    ]

    # Summary statistics
    print("\nSummary Statistics of Numerical Features:")
    print(df[numeric_features].describe())

    # Histograms
    df[numeric_features].hist(figsize=(16, 10), bins=30)
    plt.suptitle("Distribution of Numerical Features", fontsize=16)
    plt.show()

    # Correlation heatmap
    plt.figure(figsize=(22, 16))
    sns.heatmap(
        df[numeric_features + ["churn_flag"]].corr(),
        annot=True, cmap="coolwarm", fmt=".2f", linewidths=0.5
    )
    plt.title("Feature Correlation Matrix", fontsize=16)
    plt.xticks(rotation=45, ha='right')
    plt.yticks(rotation=0)
    plt.show()

    # Time-related feature distribution by churn
    time_features = ["most_active_weekday", "least_active_weekday"]
    for col in time_features:
        plt.figure(figsize=(8, 4))
        sns.boxplot(x=df["churn_flag"], y=df[col], palette="Set2")
        plt.title(f"{col} vs Churn")
        plt.show()

    print("EDA completed successfully.")


# === Script Execution ===
if __name__ == "__main__":
    dataset_path = "churn_w_features_fixed.xlsx"
    df = load_and_clean_dataset(dataset_path)

    # Optional: Save intermediate cleaned version
    df.to_csv("churn_w_features_cleaned.csv", index=False)

    explore_data(df)

"""
Generate KDE plots for each numerical feature (with values > 0)
separated by churn label. Save the resulting multi-subplot figure
to a PNG file.
"""

import matplotlib.pyplot as plt
import seaborn as sns

# Create a subplot grid
fig, axes = plt.subplots(n_rows, n_cols, figsize=(5 * n_cols, 4 * n_rows))
axes = axes.flatten()

used_axes = 0  # Counter for the number of axes actually used

# Generate KDE plots for each numeric feature (excluding non-positive values)
for feature in numeric_original_features:
    if df[feature].nunique() > 1:
        ax = axes[used_axes]

        # Plot for non-churned couriers (label = 0)
        sns.kdeplot(
            data=df[(df["churn_flag"] == 0) & (df[feature] > 0)],
            x=feature,
            fill=True,
            label="Churn = 0",
            color="blue",
            alpha=0.5,
            ax=ax,
            bw_adjust=0.5,
            cut=0,
            gridsize=1000
        )

        # Plot for churned couriers (label = 1)
        sns.kdeplot(
            data=df[(df["churn_flag"] == 1) & (df[feature] > 0)],
            x=feature,
            fill=True,
            label="Churn = 1",
            color="red",
            alpha=0.5,
            ax=ax,
            bw_adjust=0.5,
            cut=0,
            gridsize=1000
        )

        ax.set_title(feature)
        ax.legend()
        used_axes += 1

# Remove unused axes
for j in range(used_axes, len(axes)):
    fig.delaxes(axes[j])

# Final layout and save to file
plt.tight_layout()
plt.savefig("feature_distributions_positive_only.png", dpi=300)
plt.show()

"""# Standartization + PLS"""

import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cross_decomposition import PLSRegression

numeric_features = [
        "active_days_14d", "active_days_30d", "active_days_3d", "active_days_7d",
        "age",
        "avg_order_cpo_14d", "avg_order_cpo_30d", "avg_order_cpo_3d", "avg_order_cpo_7d",
        "avg_trip_distance_14d", "avg_trip_distance_30d", "avg_trip_distance_3d", "avg_trip_distance_7d",
        "max_order_cpo_14d", "max_order_cpo_30d", "max_order_cpo_3d", "max_order_cpo_7d",
        "min_order_cpo_14d", "min_order_cpo_30d", "min_order_cpo_3d", "min_order_cpo_7d",
        "num_orders_14d", "num_orders_30d", "num_orders_3d", "num_orders_7d",
        "num_orders_total",
        "orders_friday", "orders_monday", "orders_saturday", "orders_sunday",
        "orders_thursday", "orders_tuesday", "orders_wednesday",
        "total_income_14d", "total_income_30d", "total_income_3d", "total_income_7d",
        "weekend_orders_ratio"
    ]

# Ensure 'courier_id' and 'churn_flag' are not included in numeric features
numeric_features = [col for col in numeric_features if col not in ["courier_id", "churn_flag"]]

# Identify non-numeric features as all columns not in numeric_features or 'courier_id'
non_numeric_features = [col for col in df.columns if col not in numeric_features + ["courier_id"]]

# Extract non-numeric data (including 'courier_id' for later merge)
df_non_numeric = df[["courier_id"] + non_numeric_features]

# Standardize numeric features before applying PLS
scaler = StandardScaler()
df_scaled = scaler.fit_transform(df[numeric_features])

# Define target variable for PLS
y = df["churn_flag"]

# Fit PLS regression model on numeric features
n_components = min(len(numeric_features), 15)
pls = PLSRegression(n_components=n_components)
X_scores = pls.fit_transform(df_scaled, y)[0]  # Use X_scores from the output tuple

# Convert scores to DataFrame with meaningful names
pls_columns = [f"PLS_{i+1}" for i in range(X_scores.shape[1])]
df_pls = pd.DataFrame(X_scores, columns=pls_columns)
df_pls["courier_id"] = df["courier_id"]

# Ensure that 'courier_id' order matches between DataFrames
if not (df_pls["courier_id"].values == df_non_numeric["courier_id"].values).all():
    print("⚠️ Mismatch in 'courier_id' order — sorting to align.")
    df_pls = df_pls.sort_values("courier_id").reset_index(drop=True)
    df_non_numeric = df_non_numeric.sort_values("courier_id").reset_index(drop=True)
else:
    print("✅ 'courier_id' order is aligned.")

# Drop 'courier_id' from non-numeric set to avoid duplication
df_non_numeric = df_non_numeric.drop(columns=["courier_id"])

# Combine PLS-transformed numeric data with non-numeric data
df_final = pd.concat([df_pls, df_non_numeric], axis=1)

# Save final result
output_path = "churn_w_features_PLS.csv"
df_final.to_csv(output_path, index=False)

# Final check
print(f"✅ Final dataset saved to '{output_path}'. Shape: {df_final.shape}")

"""# Train/test split"""

from sklearn.model_selection import train_test_split

# Define feature matrix (X) and target vector (y)
X = df_final.drop(columns=["courier_id", "churn_flag"])  # Exclude ID and target
y = df_final["churn_flag"]  # Target variable

# Split the dataset into training (80%) and testing (20%) sets using stratification
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

# Combine features and target for train set and save to file
train_df = X_train.copy()
train_df["churn_flag"] = y_train
train_df.to_csv("train_churn_PLS.csv", index=False)

# Combine features and target for test set and save to file
test_df = X_test.copy()
test_df["churn_flag"] = y_test
test_df.to_csv("test_churn_PLS.csv", index=False)

# Print confirmation and summary
print("✅ Train-test split completed successfully.")
print(f"Train set size: {X_train.shape[0]} rows")
print(f"Test set size: {X_test.shape[0]} rows")

"""# Training, evaluation on test for baseline models"""

!pip install --upgrade --force-reinstall numpy==1.26.4

!pip uninstall -y catboost
!pip install catboost

from catboost import CatBoostClassifier
print("CatBoost imported successfully! 🚀")

"""
Train multiple classification models and evaluate them on a churn prediction dataset.
Includes preprocessing, encoding, ROC analysis, metric table generation,
and confusion matrix visualization.
"""

import time
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import (
    roc_auc_score, f1_score, recall_score, precision_score,
    classification_report, roc_curve, auc, confusion_matrix
)
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier
from catboost import CatBoostClassifier
from sklearn.utils.multiclass import unique_labels

# Load training and testing datasets
df_train = pd.read_csv("train_churn_PLS.csv")
df_test = pd.read_csv("test_churn_PLS.csv")

# Convert date columns to datetime and compute account age
current_date = datetime(2025, 3, 11)
for df in [df_train, df_test]:
    df["first_order_delivered"] = pd.to_datetime(df["first_order_delivered"])
    df["account_age_days"] = (current_date - df["first_order_delivered"]).dt.days
    df.drop(columns=["first_order_delivered"], inplace=True)

# One-hot encode categorical features
df_train = pd.get_dummies(df_train, columns=["movement_type", "hiring_channel_name"], drop_first=True)
df_test = pd.get_dummies(df_test, columns=["movement_type", "hiring_channel_name"], drop_first=True)

# Align test set columns with train set
df_test = df_test.reindex(columns=df_train.columns, fill_value=0)

# Label encode region_id
le = LabelEncoder()
df_train["region_id"] = le.fit_transform(df_train["region_id"])
df_test["region_id"] = le.transform(df_test["region_id"])

# Separate features and target
X_train = df_train.drop(columns=["churn_flag"])
y_train = df_train["churn_flag"]
X_test = df_test.drop(columns=["churn_flag"])
y_test = df_test["churn_flag"]

# Scale features for scaling-sensitive models
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Define models to evaluate
models = {
    "Logistic Regression": LogisticRegression(max_iter=500),
    "Decision Tree": DecisionTreeClassifier(random_state=42),
    "Random Forest": RandomForestClassifier(n_estimators=100, random_state=42),
    "XGBoost": XGBClassifier(use_label_encoder=False, eval_metric="logloss", random_state=42),
    "LightGBM": LGBMClassifier(random_state=42),
    "CatBoost": CatBoostClassifier(verbose=0, random_state=42),
    "SVM": SVC(probability=True, random_state=42)
}

results = []
roc_data = []

# Train and evaluate each model
for name, model in models.items():
    print(f"Training {name}...")
    start = time.time()

    if name in ["Logistic Regression", "SVM"]:
        model.fit(X_train_scaled, y_train)
        y_train_pred = model.predict(X_train_scaled)
        y_train_proba = model.predict_proba(X_train_scaled)[:, 1]
        y_test_pred = model.predict(X_test_scaled)
        y_test_proba = model.predict_proba(X_test_scaled)[:, 1]
    else:
        model.fit(X_train, y_train)
        y_train_pred = model.predict(X_train)
        y_train_proba = model.predict_proba(X_train)[:, 1]
        y_test_pred = model.predict(X_test)
        y_test_proba = model.predict_proba(X_test)[:, 1]

    training_time = time.time() - start

    # Compute ROC curve
    fpr, tpr, _ = roc_curve(y_test, y_test_proba)
    roc_auc = auc(fpr, tpr)
    roc_data.append((name, fpr, tpr, roc_auc))

    # Classification report
    report = classification_report(y_test, y_test_pred, output_dict=True)
    results.append({
        "Model": name,
        "Accuracy": report["accuracy"],
        "Precision (1)": report["1"]["precision"],
        "Recall (1)": report["1"]["recall"],
        "F1-score (1)": report["1"]["f1-score"],
        "AUC-ROC": roc_auc,
        "Training Time (s)": round(training_time, 2)
    })

# Plot ROC curves
plt.figure(figsize=(10, 8))
for name, fpr, tpr, roc_auc in roc_data:
    plt.plot(fpr, tpr, label=f"{name} (AUC = {roc_auc:.3f})")
plt.plot([0, 1], [0, 1], linestyle="--", color="gray")
plt.xlabel("False Positive Rate")
plt.ylabel("True Positive Rate")
plt.title("ROC Curves for All Models")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

# Display result metrics table
df_results = pd.DataFrame(results).sort_values(by="AUC-ROC", ascending=False)

plt.figure(figsize=(10, 0.5 * len(df_results) + 1))
ax = plt.gca()
ax.axis("off")
numeric_vals = df_results.drop(columns=["Model"]).values
table = plt.table(
    cellText=np.hstack([df_results[["Model"]].values, np.round(numeric_vals, 3)]),
    colLabels=df_results.columns,
    cellLoc="center",
    loc="center"
)
table.auto_set_font_size(False)
table.set_fontsize(10)
table.scale(1, 1.5)
plt.title("Model Comparison Metrics", fontsize=14)
plt.show()

# Plot normalized confusion matrices
for name, model in models.items():
    if name in ["Logistic Regression", "SVM"]:
        y_pred = model.predict(X_test_scaled)
    else:
        y_pred = model.predict(X_test)

    cm = confusion_matrix(y_test, y_pred, normalize="true")

    plt.figure(figsize=(4, 3))
    sns.heatmap(cm, annot=True, fmt=".2f", cmap="Blues", cbar=False,
                xticklabels=unique_labels(y_test, y_pred),
                yticklabels=unique_labels(y_test, y_pred))
    plt.title(f"Normalized Confusion Matrix: {name}")
    plt.xlabel("Predicted")
    plt.ylabel("Actual")
    plt.tight_layout()
    plt.show()

"""# Feature imporatnce for the best baseline model"""

"""
Compute and visualize SHAP values for PLS features using a trained CatBoost model.
This script uses TreeExplainer to interpret model predictions specifically based on PLS components.
"""

import shap
import matplotlib.pyplot as plt
import pandas as pd

# Initialize SHAP TreeExplainer with the trained CatBoost model
explainer = shap.TreeExplainer(models["CatBoost"])

# Compute SHAP values for the entire test set
shap_values = explainer.shap_values(X_test)

# Extract PLS-based features from the test set
pls_features = [col for col in X_test.columns if col.startswith("PLS_")]
X_test_pls = X_test[pls_features]

# Select SHAP values corresponding only to the PLS features
pls_indices = [X_test.columns.get_loc(feature) for feature in pls_features]
shap_values_pls = shap_values[:, pls_indices]

# Plot SHAP summary beeswarm plot for PLS features
shap.summary_plot(
    shap_values_pls,
    features=X_test_pls,
    feature_names=pls_features,
    show=True
)

"""
Identify and display the top 20 original features contributing to the PLS_12 component
based on the absolute weight magnitude in the PLS regression.
"""

import pandas as pd

# Create a DataFrame of original feature weights across all PLS components
pls_weights_df = pd.DataFrame(
    pls.x_weights_,  # shape: (n_original_features, n_components)
    index=numeric_features,
    columns=[f"PLS_{i + 1}" for i in range(pls.x_weights_.shape[1])]
)

# Extract weights for the PLS_12 component
pls_12_contributions = pls_weights_df["PLS_12"]

# Sort features by absolute contribution to PLS_12
top_20_features = pls_12_contributions.abs().sort_values(ascending=False).head(20)

# Retain original signed contributions for interpretation
top_20_signed = pls_12_contributions[top_20_features.index]

# Display the result
print("Top 20 original features contributing to PLS_12:")
display(top_20_signed.to_frame(name="Weight in PLS_12"))

"""# Parameters tuning with Optuna"""

!pip install optuna

"""
Hyperparameter tuning using Optuna for multiple classification models
on a courier churn prediction dataset.
"""

import time
import optuna
import pandas as pd
from datetime import datetime
from sklearn.model_selection import train_test_split
from sklearn.metrics import f1_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier
from catboost import CatBoostClassifier
from sklearn.svm import SVC

# Load datasets
train_path = "train_churn_PLS.csv"
test_path = "test_churn_PLS.csv"
df_train = pd.read_csv(train_path)
df_test = pd.read_csv(test_path)

# Convert date columns and compute account age
current_date = datetime(2025, 3, 11)
for df in [df_train, df_test]:
    df["first_order_delivered"] = pd.to_datetime(df["first_order_delivered"])
    df["account_age_days"] = (current_date - df["first_order_delivered"]).dt.days
    df.drop(columns=["first_order_delivered"], inplace=True)

# One-hot encode categorical features
df_train = pd.get_dummies(df_train, columns=["movement_type", "hiring_channel_name"], drop_first=True)
df_test = pd.get_dummies(df_test, columns=["movement_type", "hiring_channel_name"], drop_first=True)

# Align test columns with training data
df_test = df_test.reindex(columns=df_train.columns, fill_value=0)

# Label encode region_id
label_encoder = LabelEncoder()
df_train["region_id"] = label_encoder.fit_transform(df_train["region_id"])
df_test["region_id"] = label_encoder.transform(df_test["region_id"])

# Define features and target variable
X_train = df_train.drop(columns=["churn_flag"])
y_train = df_train["churn_flag"]
X_test = df_test.drop(columns=["churn_flag"])
y_test = df_test["churn_flag"]

# Scale features for models sensitive to feature scale
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)

def objective(trial):
    """
    Objective function for Optuna optimization. Selects model and its hyperparameters,
    trains on a training split and evaluates on a validation set using F1-score.
    """
    model_name = trial.suggest_categorical(
        "model", ["Logistic Regression", "Decision Tree", "Random Forest",
                  "XGBoost", "LightGBM", "CatBoost", "SVM"]
    )

    if model_name == "Logistic Regression":
        C = trial.suggest_float("C", 1e-3, 10.0, log=True)
        model = LogisticRegression(C=C, max_iter=500, random_state=42)
        X_data = X_train_scaled

    elif model_name == "Decision Tree":
        max_depth = trial.suggest_int("max_depth", 2, 20)
        min_samples_split = trial.suggest_int("min_samples_split", 2, 20)
        model = DecisionTreeClassifier(max_depth=max_depth,
                                       min_samples_split=min_samples_split,
                                       random_state=42)
        X_data = X_train

    elif model_name == "Random Forest":
        n_estimators = trial.suggest_int("n_estimators", 50, 300)
        max_depth = trial.suggest_int("max_depth", 2, 20)
        model = RandomForestClassifier(n_estimators=n_estimators,
                                       max_depth=max_depth,
                                       random_state=42)
        X_data = X_train

    elif model_name == "XGBoost":
        n_estimators = trial.suggest_int("n_estimators", 50, 300)
        learning_rate = trial.suggest_float("learning_rate", 0.01, 0.3, log=True)
        max_depth = trial.suggest_int("max_depth", 2, 20)
        model = XGBClassifier(n_estimators=n_estimators,
                              learning_rate=learning_rate,
                              max_depth=max_depth,
                              use_label_encoder=False,
                              eval_metric="logloss",
                              random_state=42)
        X_data = X_train

    elif model_name == "LightGBM":
        n_estimators = trial.suggest_int("n_estimators", 50, 300)
        learning_rate = trial.suggest_float("learning_rate", 0.01, 0.3, log=True)
        max_depth = trial.suggest_int("max_depth", 2, 20)
        model = LGBMClassifier(n_estimators=n_estimators,
                               learning_rate=learning_rate,
                               max_depth=max_depth,
                               random_state=42)
        X_data = X_train

    elif model_name == "CatBoost":
        n_estimators = trial.suggest_int("n_estimators", 50, 300)
        learning_rate = trial.suggest_float("learning_rate", 0.01, 0.3, log=True)
        depth = trial.suggest_int("depth", 2, 10)
        model = CatBoostClassifier(n_estimators=n_estimators,
                                   learning_rate=learning_rate,
                                   depth=depth,
                                   verbose=0,
                                   random_state=42)
        X_data = X_train

    elif model_name == "SVM":
        C = trial.suggest_float("C", 1e-3, 10.0, log=True)
        model = SVC(C=C, probability=True, random_state=42)
        X_data = X_train_scaled

    # Train-validation split
    X_train_opt, X_val, y_train_opt, y_val = train_test_split(
        X_data, y_train, test_size=0.2, random_state=42, stratify=y_train
    )

    # Train and evaluate model
    model.fit(X_train_opt, y_train_opt)
    y_pred = model.predict(X_val)
    f1 = f1_score(y_val, y_pred)

    return f1

# Launch Optuna optimization
study = optuna.create_study(direction="maximize")
study.optimize(objective, n_trials=50)

# Display best result
print("Best hyperparameters found by Optuna:")
print(study.best_params)

"""# Training and evaluating best model"""

"""
Train and evaluate the best XGBoost model using optimal hyperparameters.
Generates classification report, ROC curve, confusion matrix, and a summary table.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from xgboost import XGBClassifier
from sklearn.metrics import (
    classification_report,
    roc_auc_score,
    roc_curve,
    confusion_matrix
)
from sklearn.utils.multiclass import unique_labels

# Initialize the XGBoost model with the best hyperparameters
best_xgb = XGBClassifier(
    n_estimators=53,
    learning_rate=0.11486744748271062,
    max_depth=15,
    use_label_encoder=False,
    eval_metric="logloss",
    random_state=42
)

# Train the model
best_xgb.fit(X_train, y_train)

# Predict on test set
y_pred = best_xgb.predict(X_test)
y_pred_proba = best_xgb.predict_proba(X_test)[:, 1]

# Classification report
print("🔹 Classification Report on Test Set:")
print(classification_report(y_test, y_pred))

# AUC-ROC score
auc_score = roc_auc_score(y_test, y_pred_proba)
print(f"🔹 AUC-ROC Score: {auc_score:.4f}")

# ROC Curve
fpr, tpr, _ = roc_curve(y_test, y_pred_proba)
plt.figure(figsize=(6, 5))
plt.plot(fpr, tpr, label=f"XGBoost (AUC = {auc_score:.3f})")
plt.plot([0, 1], [0, 1], linestyle="--", color="gray")
plt.xlabel("False Positive Rate")
plt.ylabel("True Positive Rate")
plt.title("ROC Curve - XGBoost")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

# Confusion matrix (normalized)
cm = confusion_matrix(y_test, y_pred, normalize="true")
plt.figure(figsize=(4, 3))
sns.heatmap(cm, annot=True, fmt=".2f", cmap="Blues", cbar=False,
            xticklabels=unique_labels(y_test, y_pred),
            yticklabels=unique_labels(y_test, y_pred))
plt.title("Normalized Confusion Matrix - XGBoost")
plt.xlabel("Predicted")
plt.ylabel("Actual")
plt.tight_layout()
plt.show()

# Tabular summary of test metrics
report_dict = classification_report(y_test, y_pred, output_dict=True)
summary = {
    "Accuracy": report_dict["accuracy"],
    "Precision (1)": report_dict["1"]["precision"],
    "Recall (1)": report_dict["1"]["recall"],
    "F1-score (1)": report_dict["1"]["f1-score"],
    "AUC-ROC": auc_score
}
df_summary = pd.DataFrame([summary]).round(3)

# Display the summary table
plt.figure(figsize=(8, 2))
ax = plt.gca()
ax.axis("off")
table = plt.table(cellText=df_summary.values,
                  colLabels=df_summary.columns,
                  cellLoc="center",
                  loc="center")
table.auto_set_font_size(False)
table.set_fontsize(10)
table.scale(1.2, 1.5)
plt.title("XGBoost Test Set Performance Metrics", fontsize=14)
plt.tight_layout()
plt.show()