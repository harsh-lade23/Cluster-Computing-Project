# Terminal-Based Apache Spark Execution & Demonstration Guide

**Project:** Predicting Telecom Network Failure Using Apache Spark and PySpark MLlib  
**Course:** Cluster Computing Academic Project  
**Target Environment:** Local Standalone Spark Cluster (`local[*]`)  
**Software Stack:** Apache Spark 4.0.5, PySpark MLlib, OpenJDK 21.0.11, Python 3.9.6

---

## 1. Overview & Objectives

In academic cluster computing courses, students demonstrate big data engines through genuine terminal workflows (similar to executing Hadoop HDFS and MapReduce commands via the CLI). 

This guide details the exact terminal commands to:
1. Verify the Java, PySpark, and Apache Spark runtime environment.
2. Launch and interact with the interactive **PySpark Shell** using the project's actual dataset (`telecom_network_failures.csv`).
3. Execute the full end-to-end Machine Learning pipeline using **`spark-submit`**.

All commands in this document have been physically verified on the project environment and match the captured evidence in `terminal_screenshots/`.

---

## 2. Environment Setup & Pre-requisites

Before executing Spark commands, activate the virtual environment and ensure `JAVA_HOME` is exported.

```bash
# 1. Navigate to the project root directory
cd "/Users/harsh.lade/Desktop/xyz/College projects/ClusterComputing"

# 2. Export Java Home (using macOS Java locator)
export JAVA_HOME=$(/usr/libexec/java_home)

# 3. Activate the Python virtual environment containing PySpark
source .venv/bin/activate
```

---

## 3. Part A: Spark Environment Verification

Before launching Spark operations, verify that the Java Virtual Machine (JVM) and Spark binaries are properly configured.

### Command 1: Verify Java Installation
```bash
java -version
```
- **What it does:** Prints the installed Java Runtime Environment (JRE/JDK) vendor and version.
- **Why it is required:** Apache Spark executes distributed tasks inside the JVM. Spark 4.x officially requires Java 17 or Java 21.
- **Expected Output:**
  ```text
  openjdk version "21.0.11" 2026-04-21
  OpenJDK Runtime Environment JBR-21.0.11+10-1163.116-nomod (build 21.0.11+10-b1163.116)
  OpenJDK 64-Bit Server VM JBR-21.0.11+10-1163.116-nomod (build 21.0.11+10-b1163.116, mixed mode, sharing)
  ```

### Command 2: Verify PySpark Package Version
```bash
python3 -c "import pyspark; print('PySpark Version:', pyspark.__version__)"
```
- **What it does:** Imports PySpark inside Python and prints its version attribute.
- **Why it is required:** Confirms that the Python environment has the PySpark API bindings properly installed.
- **Expected Output:**
  ```text
  PySpark Version: 4.0.5
  ```

### Command 3: Verify Apache Spark Binaries & Cluster Capabilities
```bash
spark-submit --version
```
- **What it does:** Runs the core Spark submission utility and outputs the official Apache Spark ASCII banner, Scala build version, and Git commit hash.
- **Why it is required:** Confirms that `spark-submit` is functional and ready to dispatch jobs to local or distributed cluster managers (YARN, Mesos, Kubernetes, Standalone).
- **Expected Output:**
  ```text
  Welcome to
        ____              __
       / __/__  ___ _____/ /__
      _\ \/ _ \/ _ `/ __/  '_/
     /___/ .__/\_,_/_/ /_/\_\   version 4.0.5
        /_/
                          
  Using Scala version 2.13.16, OpenJDK 64-Bit Server VM, 21.0.11
  Branch HEAD
  Revision b472a3aa3c4b71b5a6ff068ef396f757bd662e59
  ```

---

## 4. Part B: PySpark Interactive Shell Demonstration

The PySpark shell provides an interactive Read-Eval-Print Loop (REPL) for ad-hoc distributed data exploration.

### Step 1: Start PySpark in Local Cluster Mode
```bash
pyspark --master "local[*]"
```
- **What it does:** Launches the interactive PySpark shell. The `--master "local[*]"` flag tells Spark to run locally and spawn worker execution threads across all available CPU cores.
- **Why it is required:** Simulates a multi-node cluster on a single workstation by leveraging multi-threading and partitioned memory management.
- **Spark Banner:** The shell automatically instantiates:
  - `sc`: `SparkContext` (the master connection to the Spark execution runtime).
  - `spark`: `SparkSession` (the unified entry point for DataFrame and SQL operations).
  - Web UI at: `http://localhost:4040` (Spark application monitoring dashboard).

---

### Step 2: Load the Project CSV into a Distributed Spark DataFrame
```python
df = spark.read.csv("telecom_network_failures.csv", header=True, inferSchema=True, nullValue="")
```
- **What it does:** Reads the CSV dataset using Spark's distributed CSV data source. 
  - `header=True`: Uses the first row as column headers.
  - `inferSchema=True`: Instructs Spark to sample records and automatically detect data types (integer, double, string).
  - `nullValue=""`: Treats empty strings as true SQL `null` values.
- **Why it is required:** Raw network telemetry is loaded as an immutable, partitioned Spark DataFrame ready for distributed processing.

---

### Step 3: Count Total Records
```python
df.count()
```
- **What it does:** Triggers an action on the Spark DAG (Directed Acyclic Graph) to compute the total row count across partitions.
- **Expected Output:**
  ```text
  5000
  ```

---

### Step 4: Display DataFrame Schema
```python
df.printSchema()
```
- **What it does:** Displays the structural schema inferred by Spark, including column names, data types, and nullability flags.
- **Expected Output:**
  ```text
  root
   |-- device_id: string (nullable = true)
   |-- device_type: string (nullable = true)
   |-- region: string (nullable = true)
   |-- network_traffic_mbps: double (nullable = true)
   |-- signal_strength_dbm: double (nullable = true)
   |-- packet_loss_pct: double (nullable = true)
   |-- latency_ms: double (nullable = true)
   |-- device_status: string (nullable = true)
   |-- device_temperature_c: double (nullable = true)
   |-- historical_faults_count: integer (nullable = true)
   |-- uptime_days: double (nullable = true)
   |-- failure_next_24h: integer (nullable = true)
  ```

---

### Step 5: Display Sample Records
```python
df.select("device_id", "device_type", "region", "network_traffic_mbps", "failure_next_24h").show(5)
```
- **What it does:** Selects key telemetry columns and prints the top 5 rows in an ASCII table.
- **Expected Output:**
  ```text
  +---------+-------------------+------+--------------------+----------------+
  |device_id|        device_type|region|network_traffic_mbps|failure_next_24h|
  +---------+-------------------+------+--------------------+----------------+
  | DEV-1001|       Base_Station| North|             1755.12|               1|
  | DEV-1002|Optical_Transponder|  West|              4058.1|               1|
  | DEV-1003|             Router| South|              1496.2|               0|
  | DEV-1004|Optical_Transponder|  West|              3124.0|               0|
  | DEV-1005|             Switch| North|             4310.69|               0|
  +---------+-------------------+------+--------------------+----------------+
  only showing top 5 rows
  ```

---

### Step 6: Calculate Missing Values per Column
```python
from pyspark.sql.functions import col, count, when

df.select([count(when(col(c).isNull(), c)).alias(c) for c in ["signal_strength_dbm", "packet_loss_pct", "latency_ms", "device_status", "device_temperature_c"]]).show()
```
- **What it does:** Evaluates null counts across the features that simulate real-world sensor dropout.
- **Why it is required:** Identifies which features require statistical imputation before being passed into MLlib estimators.
- **Expected Output:**
  ```text
  +-------------------+---------------+----------+-------------+--------------------+
  |signal_strength_dbm|packet_loss_pct|latency_ms|device_status|device_temperature_c|
  +-------------------+---------------+----------+-------------+--------------------+
  |                104|            107|        79|           78|                 102|
  +-------------------+---------------+----------+-------------+--------------------+
  ```

---

### Step 7: Display Failure Class Distribution
```python
df.groupBy("failure_next_24h").count().orderBy("failure_next_24h").show()
```
- **What it does:** Groups the dataset by the binary target label (`0` = Healthy, `1` = Failure within 24 hours) and counts occurrences.
- **Why it is required:** Demonstrates the severe class imbalance typical of network failure environments (~13.7% failure rate).
- **Expected Output:**
  ```text
  +----------------+-----+
  |failure_next_24h|count|
  +----------------+-----+
  |               0| 4315|
  |               1|  685|
  +----------------+-----+
  ```

---

### Step 8: Spark SQL Aggregation Query
```python
# Register temporary in-memory SQL table
df.createOrReplaceTempView("telecom_failures")

# Execute distributed SQL query
spark.sql("""
    SELECT device_type,
           count(*) as total_devices,
           sum(cast(failure_next_24h as int)) as failures,
           round(avg(cast(failure_next_24h as int)) * 100, 2) as failure_rate_pct
    FROM telecom_failures
    GROUP BY device_type
    ORDER BY failure_rate_pct DESC
""").show()
```
- **What it does:** Uses Spark SQL's Catalyst Optimizer to group data by device type and compute failure rates.
- **Expected Output:**
  ```text
  +-------------------+-------------+--------+----------------+
  |        device_type|total_devices|failures|failure_rate_pct|
  +-------------------+-------------+--------+----------------+
  |            Gateway|          717|     103|           14.37|
  |             Switch|         1216|     174|           14.31|
  |       Base_Station|         1025|     144|           14.05|
  |Optical_Transponder|          495|      68|           13.74|
  |             Router|         1547|     196|           12.67|
  +-------------------+-------------+--------+----------------+
  ```

---

### Step 9: Exit the PySpark Shell
```python
exit()
```
- **What it does:** Terminates the PySpark Python session, stops the active `SparkContext` and `SparkSession`, and returns to the system shell prompt.

---

## 5. Part C: Full Pipeline Execution via `spark-submit`

The core academic requirement is demonstrating the entire machine learning workflow using the standard Spark cluster submission command:

```bash
spark-submit --master "local[*]" src/train_model.py
```

### Complete Execution Workflow Demonstrated:

1. **SparkSession Initialization:** Spawns a local master session utilizing all CPU cores.
2. **Data Ingestion & Profiling:** Loads `telecom_network_failures.csv` (5,000 records, 12 columns).
3. **Three-Way Partitioning (Leakage Prevention):**
   - **Training Set (65.84%, 3,292 rows):** Fits the ML pipeline transformers and trains the Logistic Regression model.
   - **Validation Set (15.00%, 750 rows):** Tunes the probability decision threshold to maximize F1-score on imbalanced data.
   - **Testing Set (19.16%, 958 rows):** Held-out untouched partition for honest final evaluation.
4. **PySpark ML Pipeline Stages:**
   - `Imputer`: Median imputation for numerical sensor dropouts (`signal_strength_dbm`, `packet_loss_pct`, `latency_ms`, `device_temperature_c`).
   - `StringIndexer` & `OneHotEncoder`: Encodes categorical features (`device_type`, `region`, `device_status`).
   - `VectorAssembler`: Assembles 13 processed features into a single ML feature vector.
   - `LogisticRegression`: Fits a binary classification model with probability output.
5. **Threshold Optimization on Validation Set:**
   - Evaluates thresholds from 0.05 to 0.50 in 0.01 increments.
   - **Optimal Threshold Selected: `0.16`** (Validation F1 = 31.61%, vs. 5.88% at default 0.50).
6. **Dual-Threshold Evaluation on Untouched Test Set:**
   - **Accuracy:** `72.34%`
   - **Precision:** `25.46%`
   - **Recall:** `52.27%` (captures over half of all imminent failure events)
   - **F1-Score:** `34.24%` (a 4x improvement over the default 0.50 threshold of 8.63%)
   - **ROC-AUC:** `0.6932`
   - **Confusion Matrix:**
     - True Negatives (TN): `624`
     - False Positives (FP): `202`
     - False Negatives (FN): `63`
     - True Positives (TP): `69`
7. **Artifact Export:**
   - `outputs/predictions/test_predictions.csv`: Detailed test predictions with probabilities.
   - `outputs/evaluation_results/metrics.json`: Machine-readable evaluation metrics.
   - `outputs/evaluation_results/evaluation_summary.txt`: Formatted human-readable report.
   - `outputs/model/logistic_regression_pipeline`: Fitted Spark MLlib pipeline model directory.

---

## 6. Summary of Screenshot Artifacts

The captured screenshots in `terminal_screenshots/` correspond to each stage of this guide:

| File Name | Content & Description |
|:---|:---|
| `01_spark_env_verification.png` | Terminal execution of `java -version`, PySpark check, and `spark-submit --version`. |
| `02_pyspark_shell_launch_load.png` | PySpark interactive shell startup banner, SparkContext/Session init, and CSV load with row count (5,000). |
| `03_pyspark_schema_samples_missing.png` | PySpark schema inspection (`printSchema`), sample records (`show(5)`), and missing value counts. |
| `04_pyspark_groupby_sql_analysis.png` | Class imbalance verification (`groupBy`) and Spark SQL aggregation query by device type. |
| `05_spark_submit_pipeline_start.png` | Execution of `spark-submit src/train_model.py`, dataset exploration, and summary statistics. |
| `06_spark_submit_training_tuning.png` | 3-way split, 7-stage ML pipeline fitting, and threshold tuning on the validation set. |
| `07_spark_submit_evaluation_artifacts.png` | Test evaluation comparison table (0.50 vs 0.16), confusion matrix, and artifact persistence. |

---

## 7. Viva / Oral Examination Tips

When asked by the examiner:
- **"Why did you use `local[*]`?"**  
  *Answer:* `local[*]` tells Spark to spin up a local standalone worker instance that utilizes all available CPU cores. Each core acts as an independent execution thread, providing distributed data partitioning and multi-core parallelism without requiring an external cluster infrastructure.
- **"What is the difference between `pyspark` and `spark-submit`?"**  
  *Answer:* `pyspark` is an interactive shell (REPL) intended for ad-hoc querying, exploratory data analysis, and schema inspection. `spark-submit` is the production job submission script used to submit packaged, batch, or long-running applications to a cluster.
- **"Why was threshold optimization necessary?"**  
  *Answer:* Because network failures represent only ~13.7% of the dataset. At the default 0.50 threshold, the model was overly conservative, predicting only 7 failure cases (Recall: 4.55%). Optimizing the threshold to 0.16 on a separate validation set increased Recall to 52.27% and F1-score from 8.63% to 34.24%, identifying 69 true failure cases while strictly preventing test data leakage.
