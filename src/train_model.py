"""
Predicting Telecom Network Failure using Apache Spark and PySpark MLlib
========================================================================

Course/Project: Cluster Computing Academic Project
Script: src/train_model.py
Description:
    End-to-end distributed machine learning pipeline for predicting network component
    failures within 24 hours using Apache Spark (standalone/local mode) and Spark MLlib.

Key Concepts Demonstrated:
    1. SparkSession management & local standalone distributed processing.
    2. Spark DataFrame operations (schema inference, descriptive stats, missing value inspection).
    3. Three-way data partitioning: Train (64%), Validation (16%), Test (20%).
       - Training set: Fits preprocessing transformations and MLlib LogisticRegression model.
       - Validation set: Tunes the decision threshold to maximize F1-score on imbalanced data.
       - Test set: Remains strictly untouched until final evaluation.
    4. Missing value imputation:
       - Numerical: Spark ML Imputer (median strategy, fitted on training data).
       - Categorical: Mode replacement computed strictly from training data (no leakage).
    5. Categorical feature encoding via StringIndexer and OneHotEncoder.
    6. Feature Vector Assembly via VectorAssembler.
    7. Spark ML Pipeline architecture (stages encapsulation & unified fit/transform).
    8. Logistic Regression binary classification with decision threshold optimization.
    9. Dual-Threshold Evaluation reporting:
       - Default Threshold (0.50)
       - Optimal Validation Threshold (selected to maximize validation F1)
       - Metrics: Precision, Recall, F1, Accuracy, ROC-AUC, Confusion Matrix.
    10. Model persistence and prediction export for downstream dashboard consumption.
"""

import json
import os
import sys

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count, when, isnan, udf
from pyspark.sql.types import DoubleType, IntegerType

from pyspark.ml import Pipeline
from pyspark.ml.feature import (
    Imputer,
    StringIndexer,
    OneHotEncoder,
    VectorAssembler
)
from pyspark.ml.classification import LogisticRegression
from pyspark.ml.evaluation import BinaryClassificationEvaluator
from pyspark.ml.linalg import Vector


# =====================================================================
# STEP 1: INITIALIZE LOCAL SPARK SESSION
# =====================================================================
def get_spark_session() -> SparkSession:
    """Initializes and returns a configured local SparkSession."""
    spark = (
        SparkSession.builder
        .appName("TelecomNetworkFailurePrediction")
        .master("local[*]")
        .config("spark.driver.memory", "2g")
        .config("spark.ui.showConsoleProgress", "false")
        # JVM module flags for Java 17/21 compatibility
        .config(
            "spark.driver.extraJavaOptions",
            "--add-opens=java.base/java.lang=ALL-UNNAMED "
            "--add-opens=java.base/java.lang.invoke=ALL-UNNAMED "
            "--add-opens=java.base/java.lang.reflect=ALL-UNNAMED "
            "--add-opens=java.base/java.io=ALL-UNNAMED "
            "--add-opens=java.base/java.net=ALL-UNNAMED "
            "--add-opens=java.base/java.nio=ALL-UNNAMED "
            "--add-opens=java.base/java.util=ALL-UNNAMED "
            "--add-opens=java.base/java.util.concurrent=ALL-UNNAMED "
            "--add-opens=java.base/java.util.concurrent.atomic=ALL-UNNAMED "
            "--add-opens=java.base/sun.nio.ch=ALL-UNNAMED"
        )
        .getOrCreate()
    )
    # Set logging level to ERROR to keep educational console output clean and readable
    spark.sparkContext.setLogLevel("ERROR")
    return spark


# =====================================================================
# STEP 2: LOAD DATA AND EXPLORATORY INSPECTION
# =====================================================================
def load_and_inspect_data(spark: SparkSession, data_path: str):
    """Loads CSV and prints schema, samples, row counts, missing values, and statistics."""
    print("\n" + "=" * 75)
    print("STEP 1: LOADING DATASET & INITIAL EXPLORATION")
    print("=" * 75)

    if not os.path.exists(data_path):
        raise FileNotFoundError(f"Dataset not found at path: {data_path}")

    # Load CSV into Spark DataFrame; nullValue="" treats empty strings as true nulls
    df = spark.read.csv(data_path, header=True, inferSchema=True, nullValue="")

    print("\n[1.1] Spark DataFrame Schema:")
    df.printSchema()

    print("\n[1.2] First 5 Records (Sample):")
    df.show(5, truncate=False)

    total_records = df.count()
    print(f"\n[1.3] Total Record Count: {total_records:,} rows")

    print("\n[1.4] Summary Statistics for Key Telemetry Metrics:")
    df.select(
        "network_traffic_mbps", "signal_strength_dbm",
        "packet_loss_pct", "latency_ms", "device_temperature_c"
    ).describe().show()

    print("\n[1.5] Missing Values Count per Column:")
    missing_exprs = []
    for col_name, dtype in df.dtypes:
        if dtype == "string":
            expr = count(when(col(col_name).isNull() | (col(col_name) == ""), col_name)).alias(col_name)
        else:
            expr = count(when(col(col_name).isNull() | isnan(col(col_name)), col_name)).alias(col_name)
        missing_exprs.append(expr)

    missing_df = df.select(missing_exprs)
    missing_df.show(vertical=True)

    print("\n[1.6] Target Class Distribution ('failure_next_24h'):")
    target_counts = df.groupBy("failure_next_24h").count().orderBy("failure_next_24h")
    target_counts.show()

    return df


# =====================================================================
# STEP 3: THREE-WAY DATASET SPLIT (TRAIN / VALIDATION / TEST)
# =====================================================================
# What it does:
#   1. Splits the data into Train+Validation (80%) and Test (20%) using seed=42.
#   2. Splits the Train+Validation partition into Training (80%) and Validation (20%).
# Why it is required:
#   - Training data: Fits pipeline transformers and trains the Logistic Regression model.
#   - Validation data: Tunes the classification decision threshold to maximize F1-score.
#   - Test data: Remains strictly untouched to provide an unbiased final evaluation.
# Concept demonstrated:
#   Rigorous machine learning workflow preventing both data leakage and threshold snooping.
# =====================================================================
def split_data(df, seed: int = 42):
    """Splits Spark DataFrame into Train (64%), Validation (16%), and Test (20%) sets."""
    print("\n" + "=" * 75)
    print("STEP 2: THREE-WAY DATA SPLIT (Train / Validation / Test)")
    print("=" * 75)

    # Initial 80/20 split: preserves the exact untouched test set from Phase 2
    train_val_df, test_df = df.randomSplit([0.8, 0.2], seed=seed)

    # Secondary split on the training portion: isolates validation set for threshold tuning
    train_df, val_df = train_val_df.randomSplit([0.8, 0.2], seed=seed)

    train_df = train_df.cache()
    val_df = val_df.cache()
    test_df = test_df.cache()

    n_train = train_df.count()
    n_val = val_df.count()
    n_test = test_df.count()
    total = n_train + n_val + n_test

    print(f"Training Partition   : {n_train:,} records ({n_train / total * 100:.2f}%) -> Used for model fitting")
    print(f"Validation Partition : {n_val:,} records ({n_val / total * 100:.2f}%) -> Used for threshold tuning")
    print(f"Testing Partition    : {n_test:,} records ({n_test / total * 100:.2f}%) -> Held-out untouched test set")

    print("\nTarget Distribution across Partitions:")
    print("--- Training Partition ---")
    train_df.groupBy("failure_next_24h").count().orderBy("failure_next_24h").show()

    print("--- Validation Partition ---")
    val_df.groupBy("failure_next_24h").count().orderBy("failure_next_24h").show()

    print("--- Testing Partition ---")
    test_df.groupBy("failure_next_24h").count().orderBy("failure_next_24h").show()

    return train_df, val_df, test_df


# =====================================================================
# STEP 4: PREPROCESSING & PIPELINE CONSTRUCTION
# =====================================================================
def build_and_train_pipeline(train_df):
    """
    Constructs the Spark MLlib Pipeline and fits it strictly on training data.
    """
    print("\n" + "=" * 75)
    print("STEP 3: FEATURE PREPROCESSING & MODEL TRAINING PIPELINE")
    print("=" * 75)

    # 1. Cast target label to DoubleType ('label')
    train_df = train_df.withColumn("label", col("failure_next_24h").cast(DoubleType()))

    # 2. Impute missing categorical values for 'device_status' using Training Mode strictly
    status_mode = (
        train_df.filter(col("device_status").isNotNull() & (col("device_status") != ""))
        .groupBy("device_status")
        .count()
        .orderBy(col("count").desc())
        .first()["device_status"]
    )
    print(f"[Preprocessing] Computed Training Mode for 'device_status': '{status_mode}'")
    train_df = train_df.fillna({"device_status": status_mode})

    # 3. Spark ML Imputer for numerical columns with missing values (Median Strategy)
    imputed_num_cols = ["signal_strength_dbm", "packet_loss_pct", "latency_ms", "device_temperature_c"]
    imputer_output_cols = [f"{c}_imputed" for c in imputed_num_cols]

    imputer = Imputer(
        inputCols=imputed_num_cols,
        outputCols=imputer_output_cols,
        strategy="median"
    )

    # 4. Categorical StringIndexer
    categorical_cols = ["device_type", "region", "device_status"]
    indexed_cols = [f"{c}_indexed" for c in categorical_cols]
    encoded_cols = [f"{c}_encoded" for c in categorical_cols]

    string_indexers = [
        StringIndexer(inputCol=c, outputCol=f"{c}_indexed", handleInvalid="keep")
        for c in categorical_cols
    ]

    # 5. OneHotEncoder
    one_hot_encoder = OneHotEncoder(
        inputCols=indexed_cols,
        outputCols=encoded_cols,
        dropLast=False
    )

    # 6. Complete list of assembled features
    feature_columns = (
        imputer_output_cols +
        ["network_traffic_mbps", "historical_faults_count", "uptime_days"] +
        encoded_cols
    )

    vector_assembler = VectorAssembler(
        inputCols=feature_columns,
        outputCol="features",
        handleInvalid="error"
    )

    # 7. Logistic Regression Classifier
    lr = LogisticRegression(
        featuresCol="features",
        labelCol="label",
        predictionCol="prediction",
        probabilityCol="probability",
        rawPredictionCol="rawPrediction",
        maxIter=100,
        regParam=0.01
    )

    pipeline_stages = [imputer] + string_indexers + [one_hot_encoder, vector_assembler, lr]
    pipeline = Pipeline(stages=pipeline_stages)

    print("\n[Pipeline Stages]:")
    for i, stage in enumerate(pipeline_stages, 1):
        print(f"  Stage {i}: {stage.__class__.__name__}")

    print("\nFitting Spark ML Pipeline on training dataset...")
    pipeline_model = pipeline.fit(train_df)
    print(">>> Model training complete!")

    return pipeline_model, status_mode


# =====================================================================
# STEP 5: CLASSIFICATION THRESHOLD OPTIMIZATION (VALIDATION SET)
# =====================================================================
# What it does:
#   1. Predicts continuous probabilities on the validation partition.
#   2. Sweeps candidate decision thresholds from 0.08 to 0.50.
#   3. Evaluates Precision, Recall, and F1-score for each candidate threshold.
#   4. Selects the threshold that maximizes validation F1-score.
# Why it is required:
#   Imbalanced datasets naturally have low base rates (~13.7%). A default 0.50 cutoff
#   demands excessive certainty before flagging a failure, leading to poor recall.
#   Tuning the threshold on validation data aligns the model with operational reality
#   without snooping or modifying the test set.
# =====================================================================
def optimize_threshold(pipeline_model, val_df, status_mode: str):
    """
    Evaluates probability thresholds on the validation partition and selects
    the threshold that maximizes validation F1-score.
    """
    print("\n" + "=" * 75)
    print("STEP 4: CLASSIFICATION THRESHOLD OPTIMIZATION (VALIDATION SET)")
    print("=" * 75)

    val_df = val_df.withColumn("label", col("failure_next_24h").cast(DoubleType()))
    val_df = val_df.fillna({"device_status": status_mode})

    # Transform validation data
    val_preds = pipeline_model.transform(val_df)

    extract_prob_udf = udf(lambda v: float(v[1]), DoubleType())
    val_preds = val_preds.withColumn("failure_probability", extract_prob_udf(col("probability")))

    # Collect validation ground truth and predicted probabilities
    val_records = [
        (row["label"], row["failure_probability"])
        for row in val_preds.select("label", "failure_probability").collect()
    ]

    total_val = len(val_records)
    actual_failures = sum(1 for y, _ in val_records if y == 1.0)
    print(f"Validation Records: {total_val} (Actual Failures: {actual_failures}, {actual_failures / total_val * 100:.2f}%)")

    # Grid search candidate thresholds from 0.08 to 0.50 in steps of 0.01
    best_threshold = 0.50
    best_f1 = -1.0
    best_metrics = {}
    threshold_search_results = []

    for t_int in range(8, 51, 1):
        t = round(t_int / 100.0, 2)
        tp = sum(1 for y, p in val_records if y == 1.0 and p >= t)
        fp = sum(1 for y, p in val_records if y == 0.0 and p >= t)
        fn = sum(1 for y, p in val_records if y == 1.0 and p < t)
        tn = sum(1 for y, p in val_records if y == 0.0 and p < t)

        prec = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        rec = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = (2.0 * prec * rec) / (prec + rec) if (prec + rec) > 0 else 0.0
        acc = (tp + tn) / total_val

        threshold_search_results.append({
            "threshold": t, "precision": prec, "recall": rec, "f1_score": f1,
            "accuracy": acc, "tp": tp, "fp": fp, "fn": fn, "tn": tn,
            "predicted_failures": tp + fp
        })

        if f1 > best_f1:
            best_f1 = f1
            best_threshold = t
            best_metrics = threshold_search_results[-1]

    # Display Top-5 Validation Thresholds
    print("\nTop-5 Thresholds Evaluated on Validation Set (Ranked by F1):")
    print(f"{'Threshold':<10} | {'Precision':<10} | {'Recall':<10} | {'F1-Score':<10} | {'Accuracy':<10} | {'Pred Failures':<14}")
    print("-" * 75)
    sorted_by_f1 = sorted(threshold_search_results, key=lambda x: x["f1_score"], reverse=True)
    for r in sorted_by_f1[:5]:
        print(f"{r['threshold']:<10.2f} | {r['precision'] * 100:>8.2f}% | {r['recall'] * 100:>8.2f}% | {r['f1_score'] * 100:>8.2f}% | {r['accuracy'] * 100:>8.2f}% | {r['predicted_failures']:>14}")

    print("\nDefault Threshold (0.50) on Validation Set for Comparison:")
    def_val = next(r for r in threshold_search_results if r["threshold"] == 0.50)
    print(f"0.50       | {def_val['precision'] * 100:>8.2f}% | {def_val['recall'] * 100:>8.2f}% | {def_val['f1_score'] * 100:>8.2f}% | {def_val['accuracy'] * 100:>8.2f}% | {def_val['predicted_failures']:>14}")

    print(f"\n>>> Selected Optimal Threshold: {best_threshold:.2f} (Achieves Max Validation F1 = {best_f1 * 100:.2f}%)")

    return best_threshold, threshold_search_results


# =====================================================================
# STEP 6: DUAL-THRESHOLD EVALUATION ON UNTOUCHED TEST SET
# =====================================================================
# What it does:
#   Evaluates the test set at:
#   1. Default Threshold (0.50)
#   2. Selected Optimal Validation Threshold (e.g. 0.16)
#   Reports complete metrics, confusion matrices, and predicted failure counts.
# =====================================================================
def evaluate_test_set(pipeline_model, test_df, status_mode: str, selected_threshold: float):
    """
    Evaluates model on the held-out test partition at both default (0.50)
    and selected validation thresholds.
    """
    print("\n" + "=" * 75)
    print("STEP 5: DUAL-THRESHOLD EVALUATION ON UNTOUCHED TEST DATASET")
    print("=" * 75)

    test_df = test_df.withColumn("label", col("failure_next_24h").cast(DoubleType()))
    test_df = test_df.fillna({"device_status": status_mode})

    # Inference through pipeline
    test_preds = pipeline_model.transform(test_df)

    extract_prob_udf = udf(lambda v: float(v[1]), DoubleType())
    test_preds = test_preds.withColumn("failure_probability", extract_prob_udf(col("probability")))
    test_preds = test_preds.cache()

    # ROC-AUC is threshold-independent
    evaluator_auc = BinaryClassificationEvaluator(
        labelCol="label",
        rawPredictionCol="rawPrediction",
        metricName="areaUnderROC"
    )
    roc_auc = evaluator_auc.evaluate(test_preds)

    test_records = [
        (row["label"], row["failure_probability"])
        for row in test_preds.select("label", "failure_probability").collect()
    ]
    total_test = len(test_records)
    actual_test_failures = sum(1 for y, _ in test_records if y == 1.0)

    print(f"Test Partition Size : {total_test} records")
    print(f"Actual Test Failures: {actual_test_failures} ({actual_test_failures / total_test * 100:.2f}%)")
    print(f"ROC-AUC Score       : {roc_auc:.4f} (Threshold-independent discriminative ranking)")

    def compute_metrics_at_threshold(thresh: float):
        tp = sum(1 for y, p in test_records if y == 1.0 and p >= thresh)
        fp = sum(1 for y, p in test_records if y == 0.0 and p >= thresh)
        fn = sum(1 for y, p in test_records if y == 1.0 and p < thresh)
        tn = sum(1 for y, p in test_records if y == 0.0 and p < thresh)

        prec = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        rec = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = (2.0 * prec * rec) / (prec + rec) if (prec + rec) > 0 else 0.0
        acc = (tp + tn) / total_test if total_test > 0 else 0.0

        return {
            "threshold": thresh,
            "accuracy": round(acc, 4),
            "precision": round(prec, 4),
            "recall": round(rec, 4),
            "f1_score": round(f1, 4),
            "roc_auc": round(roc_auc, 4),
            "confusion_matrix": {
                "tp": tp, "fp": fp, "tn": tn, "fn": fn
            },
            "predicted_failures_count": tp + fp
        }

    metrics_default = compute_metrics_at_threshold(0.50)
    metrics_optimized = compute_metrics_at_threshold(selected_threshold)

    # Print Comparative Report
    print("\n" + "=" * 75)
    print("COMPARATIVE EVALUATION RESULTS (TEST SET)")
    print("=" * 75)
    print(f"{'Metric':<28} | {'Default (Threshold = 0.50)':<25} | {'Optimized (Threshold = ' + f'{selected_threshold:.2f})':<25}")
    print("-" * 85)
    print(f"{'Accuracy':<28} | {metrics_default['accuracy'] * 100:>22.2f}% | {metrics_optimized['accuracy'] * 100:>22.2f}%")
    print(f"{'Precision (Positive Class)':<28} | {metrics_default['precision'] * 100:>22.2f}% | {metrics_optimized['precision'] * 100:>22.2f}%")
    print(f"{'Recall (Positive Class)':<28} | {metrics_default['recall'] * 100:>22.2f}% | {metrics_optimized['recall'] * 100:>22.2f}%")
    print(f"{'F1-Score (Positive Class)':<28} | {metrics_default['f1_score'] * 100:>22.2f}% | {metrics_optimized['f1_score'] * 100:>22.2f}%")
    print(f"{'ROC-AUC':<28} | {metrics_default['roc_auc']:>23.4f} | {metrics_optimized['roc_auc']:>23.4f}")
    print(f"{'Predicted Failures Count':<28} | {metrics_default['predicted_failures_count']:>23} | {metrics_optimized['predicted_failures_count']:>23}")
    print(f"{'True Positives (TP)':<28} | {metrics_default['confusion_matrix']['tp']:>23} | {metrics_optimized['confusion_matrix']['tp']:>23}")
    print(f"{'False Positives (FP)':<28} | {metrics_default['confusion_matrix']['fp']:>23} | {metrics_optimized['confusion_matrix']['fp']:>23}")
    print(f"{'False Negatives (FN)':<28} | {metrics_default['confusion_matrix']['fn']:>23} | {metrics_optimized['confusion_matrix']['fn']:>23}")
    print(f"{'True Negatives (TN)':<28} | {metrics_default['confusion_matrix']['tn']:>23} | {metrics_optimized['confusion_matrix']['tn']:>23}")

    print("\nConfusion Matrix at Default Threshold (0.50):")
    print(f"  Actual Healthy (0) : TN = {metrics_default['confusion_matrix']['tn']}, FP = {metrics_default['confusion_matrix']['fp']}")
    print(f"  Actual Failure (1) : FN = {metrics_default['confusion_matrix']['fn']}, TP = {metrics_default['confusion_matrix']['tp']}")

    print(f"\nConfusion Matrix at Optimized Threshold ({selected_threshold:.2f}):")
    print(f"  Actual Healthy (0) : TN = {metrics_optimized['confusion_matrix']['tn']}, FP = {metrics_optimized['confusion_matrix']['fp']}")
    print(f"  Actual Failure (1) : FN = {metrics_optimized['confusion_matrix']['fn']}, TP = {metrics_optimized['confusion_matrix']['tp']}")

    evaluation_report = {
        "test_records_count": total_test,
        "actual_failures_count": actual_test_failures,
        "selected_validation_threshold": selected_threshold,
        "default_threshold_metrics": metrics_default,
        "optimized_threshold_metrics": metrics_optimized
    }

    return test_preds, evaluation_report


# =====================================================================
# STEP 7: SAVE PREDICTIONS, METRICS & TRAINED MODEL
# =====================================================================
def save_artifacts(pipeline_model, test_preds, evaluation_report, selected_threshold: float, output_base="outputs"):
    """
    Saves predictions CSV with optimized threshold binary decisions,
    metrics JSON, summary text, and the serialized Spark ML model.
    """
    print("\n" + "=" * 75)
    print("STEP 6: SAVING UPDATED ARTIFACTS, PREDICTIONS & MODEL")
    print("=" * 75)

    os.makedirs(os.path.join(output_base, "model"), exist_ok=True)
    os.makedirs(os.path.join(output_base, "predictions"), exist_ok=True)
    os.makedirs(os.path.join(output_base, "evaluation_results"), exist_ok=True)

    # 1. Format predictions DataFrame
    # Include optimized binary prediction based on selected threshold
    formatted_preds = test_preds.withColumn(
        "predicted_failure",
        when(col("failure_probability") >= selected_threshold, 1).otherwise(0).cast(IntegerType())
    ).select(
        col("device_id"),
        col("device_type"),
        col("region"),
        col("failure_next_24h").alias("actual_failure"),
        col("predicted_failure"),
        col("failure_probability")
    )

    print("\n[Sample Predictions Export (with Optimized Decision Threshold)]:")
    formatted_preds.show(10, truncate=False)

    # 2. Save predictions as CSV
    pred_csv_dir = os.path.join(output_base, "predictions", "test_predictions_csv")
    formatted_preds.coalesce(1).write.mode("overwrite").option("header", "true").csv(pred_csv_dir)
    print(f">>> Predictions exported to: {pred_csv_dir}")

    # Save direct consolidated CSV copy
    for fname in os.listdir(pred_csv_dir):
        if fname.startswith("part-") and fname.endswith(".csv"):
            import shutil
            shutil.copyfile(
                os.path.join(pred_csv_dir, fname),
                os.path.join(output_base, "predictions", "test_predictions.csv")
            )
            print(f">>> Consolidated predictions file saved at: {os.path.join(output_base, 'predictions', 'test_predictions.csv')}")
            break

    # 3. Save comprehensive metrics JSON
    metrics_json_path = os.path.join(output_base, "evaluation_results", "metrics.json")
    with open(metrics_json_path, "w", encoding="utf-8") as f:
        json.dump(evaluation_report, f, indent=4)
    print(f">>> Metrics JSON saved to: {metrics_json_path}")

    # 4. Save human-readable text summary
    metrics_txt_path = os.path.join(output_base, "evaluation_results", "evaluation_summary.txt")
    with open(metrics_txt_path, "w", encoding="utf-8") as f:
        f.write("TELECOM NETWORK FAILURE PREDICTION - EVALUATION SUMMARY (PHASE 2.1)\n")
        f.write("=" * 70 + "\n\n")
        f.write(f"Total Test Records               : {evaluation_report['test_records_count']}\n")
        f.write(f"Actual Failures in Test Set      : {evaluation_report['actual_failures_count']}\n")
        f.write(f"Selected Validation Threshold    : {selected_threshold:.2f}\n\n")

        f.write("DEFAULT THRESHOLD (0.50) PERFORMANCE:\n")
        f.write("-" * 45 + "\n")
        for k, v in evaluation_report["default_threshold_metrics"].items():
            f.write(f"  {k:<28}: {v}\n")

        f.write(f"\nOPTIMIZED THRESHOLD ({selected_threshold:.2f}) PERFORMANCE:\n")
        f.write("-" * 45 + "\n")
        for k, v in evaluation_report["optimized_threshold_metrics"].items():
            f.write(f"  {k:<28}: {v}\n")
    print(f">>> Metrics Text Summary saved to: {metrics_txt_path}")

    # 5. Persist the trained Spark ML Pipeline Model
    model_save_path = os.path.join(output_base, "model", "logistic_regression_pipeline")
    pipeline_model.write().overwrite().save(model_save_path)
    print(f">>> Spark ML Model saved to: {model_save_path}")


# =====================================================================
# MAIN PIPELINE EXECUTION
# =====================================================================
def main():
    print("=" * 75)
    print("TELECOM NETWORK FAILURE PREDICTION - APACHE SPARK & PYSPARK MLLIB")
    print("PHASE 2.1: CLASSIFICATION THRESHOLD OPTIMIZATION")
    print("=" * 75)

    data_path = "telecom_network_failures.csv"
    spark = get_spark_session()

    try:
        # Step 1: Load and inspect dataset
        df = load_and_inspect_data(spark, data_path)

        # Step 2: Three-way train/validation/test split
        train_df, val_df, test_df = split_data(df, seed=42)

        # Step 3: Build pipeline and fit strictly on training partition
        pipeline_model, status_mode = build_and_train_pipeline(train_df)

        # Step 4: Tune classification threshold on validation partition
        selected_threshold, _ = optimize_threshold(pipeline_model, val_df, status_mode)

        # Step 5: Evaluate on untouched test partition at both default and optimal thresholds
        test_preds, evaluation_report = evaluate_test_set(
            pipeline_model, test_df, status_mode, selected_threshold
        )

        # Step 6: Save updated artifacts, predictions, and metrics
        save_artifacts(
            pipeline_model, test_preds, evaluation_report, selected_threshold, output_base="outputs"
        )

        print("\n" + "=" * 75)
        print("PHASE 2.1 PIPELINE EXECUTION COMPLETED SUCCESSFULLY!")
        print("=" * 75)

    finally:
        spark.stop()


if __name__ == "__main__":
    main()
