# Predicting Telecom Network Failure using Apache Spark and PySpark MLlib

## Academic Project Overview

This project implements an end-to-end distributed machine learning pipeline using **Apache Spark** and **PySpark MLlib** to predict telecommunication network hardware failures 24 hours in advance.

The pipeline demonstrates core cluster computing concepts, distributed data transformations, machine learning pipelines, and decision threshold optimization using **PySpark in standalone local mode** (`local[*]`), without relying on external machine learning packages or distributed cluster infrastructure (Kafka/Hadoop).

---

## Project Structure

```
ClusterComputing/
│
├── telecom_network_failures.csv     # 5,000 synthetic telecom records (12 columns)
├── generate_dataset.py              # Synthetic dataset generator & validation suite (seed=42)
├── DATASET_README.md                # Detailed schema, physical telemetry ranges & methodology
│
├── src/
│   └── train_model.py               # Complete PySpark pipeline (ETL, Preprocessing, ML, Tuning, Evaluation)
│
├── outputs/
│   ├── model/                       # Serialized Spark MLlib Pipeline Model
│   │   └── logistic_regression_pipeline/
│   ├── predictions/                 # Predictions exported for downstream dashboard consumption
│   │   ├── test_predictions.csv     # Contains actual, predicted (optimized threshold), and probabilities
│   │   └── test_predictions_csv/
│   └── evaluation_results/          # Evaluation metrics and confusion matrices
│       ├── metrics.json             # Dual-threshold evaluation metrics in JSON
│       └── evaluation_summary.txt   # Human-readable evaluation text report
│
├── requirements.txt                 # Project dependencies (pyspark, numpy)
└── README.md                        # Documentation and execution guide
```

---

## Prerequisites & Installation

### Requirements
- **Java**: Java 17 or Java 21 (OpenJDK / JRE) configured on `$PATH`.
- **Python**: Python 3.9+

### Setup Instructions

1. Clone or navigate to the workspace directory:
   ```bash
   cd "/Users/harsh.lade/Desktop/xyz/College projects/ClusterComputing"
   ```

2. Create and activate a Python virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

---

## Running the Pipeline & Dashboard

### 1. Train the PySpark Model & Export Predictions
To execute the complete PySpark pipeline (including three-way data splitting, pipeline fitting, validation threshold optimization, dual-threshold test evaluation, and artifact export):
```bash
python3 src/train_model.py
```
*(Or with the virtual environment: `.venv/bin/python3 src/train_model.py`)*

### 2. Launch the Interactive Dashboard
To launch the interactive Streamlit dashboard:
```bash
streamlit run app.py
```
*(Or with the virtual environment: `.venv/bin/streamlit run app.py`)*

The dashboard will open locally at `http://localhost:8501`.

---

## PySpark Architecture & Machine Learning Concepts

### 1. SparkSession Management
- The pipeline initializes a local `SparkSession` configured with `master("local[*]")`, automatically utilizing all CPU cores on the local machine.
- JVM module flags (`--add-opens=...`) are configured to ensure full compatibility with modern Java runtimes (Java 17/21).

### 2. Three-Way Data Partitioning (Preventing Data Leakage & Snooping)
- The dataset is split into **Train (65.84%)**, **Validation (15.00%)**, and **Test (19.16%)** using fixed seeds (`seed=42`):
  * **Training Set (3,292 rows):** Used strictly for fitting pipeline transformers (imputation median/mode) and training the Logistic Regression model.
  * **Validation Set (750 rows):** Used exclusively to tune the probability threshold to maximize F1-score on imbalanced data.
  * **Test Set (958 rows):** Held-out and strictly untouched until final evaluation to provide unbiased performance estimates.

### 3. Missing Value Imputation
- Categorical missing values in `device_status` are imputed using the **training mode** (`'Normal'`), computed strictly from training rows.
- Numerical missing values (`signal_strength_dbm`, `packet_loss_pct`, `latency_ms`, `device_temperature_c`) are imputed using Spark MLlib's `Imputer` with the **median** strategy fitted strictly on training rows.
- `device_id` and the target label `failure_next_24h` are protected from imputation.

### 4. Categorical Encoding & Vector Assembly
- **`StringIndexer` & `OneHotEncoder`:** Machine learning algorithms operate on numerical vectors. `StringIndexer` maps distinct string labels to numeric indices, and `OneHotEncoder` converts them into binary indicator vectors to prevent artificial ordinal assumptions between device types and regions.
- **`VectorAssembler`:** Spark MLlib algorithms require all feature dimensions to be combined into a single unified `Vector` column (`features`) per row.

### 5. What is Logistic Regression?
- **Concept:** Logistic Regression is a supervised classification algorithm that models the probability of a binary outcome ($Y \in \{0, 1\}$) as a linear combination of input features passed through a logistic sigmoid function:
  $$P(\text{failure} = 1 \mid X) = \frac{1}{1 + e^{-(\mathbf{w}^T \mathbf{x} + b)}}$$
- **Interpretability:** It outputs continuous, calibrated probabilities between $0.0$ and $1.0$, allowing operators to assess failure risk gradients.

---

## Decision Threshold Optimization (Phase 2.1)

### The Problem with the Default 0.50 Threshold
In predictive maintenance and telecom anomaly detection, failure is naturally infrequent (~13.7% in our dataset). A standard classifier applying a default cutoff of **0.50** demands near certainty before issuing an alert. Consequently:
- At $\theta = 0.50$, the model flagged only **7 devices out of 958 test records**, missing **126 out of 132 actual failures** (Recall = 4.55%).

### Validation-Driven Threshold Search
To resolve this without data leakage or test set snooping:
1. Predictions and continuous failure probabilities were generated on the **validation partition (750 records)**.
2. Candidate thresholds from **0.08 to 0.50** (step 0.01) were evaluated.
3. The threshold that maximized validation F1-score was selected: **$\theta^* = 0.16$** (Validation F1 = 31.61%, Recall = 50.52%, Precision = 23.00%).

---

## Actual Execution & Comparative Evaluation Results

Evaluated on the held-out, **untouched test partition (958 records, 132 actual failures)**:

### 1. Comparative Performance Metrics Table

| Metric | Default Threshold (0.50) | Optimized Threshold (0.16) | Operational Impact |
| :--- | :---: | :---: | :--- |
| **Decision Threshold** | `0.50` | **`0.16`** | Calibrated to domain base-rate (~13.7%) |
| **Accuracy** | 86.74% | 72.34% | Lower raw accuracy, but vastly superior failure detection |
| **Precision (Positive Class)** | **85.71%** | **25.46%** | Trade-off: 1 in 4 flagged devices experiences failure |
| **Recall (Positive Class)** | **4.55%** | **52.27%** | **Over 11x increase in detected impending failures!** |
| **F1-Score (Positive Class)** | **8.63%** | **34.24%** | **Almost 4x improvement in balanced harmonic mean** |
| **ROC-AUC** | 0.6932 | 0.6932 | Identical (threshold-independent discriminative power) |
| **Predicted Failures Count** | 7 | **271** | Proactively flags at-risk devices for inspection |

### 2. Confusion Matrices Comparison

#### Default Threshold ($\theta = 0.50$):
```
                       Predicted: 0 (Healthy)   Predicted: 1 (Failure)
Actual: 0 (Healthy)    TN = 825                  FP = 1                 
Actual: 1 (Failure)    FN = 126                  TP = 6                 
```
*At $\theta = 0.50$, the model misses 126 failures to avoid false alarms.*

#### Optimized Validation Threshold ($\theta = 0.16$):
```
                       Predicted: 0 (Healthy)   Predicted: 1 (Failure)
Actual: 0 (Healthy)    TN = 624                  FP = 202               
Actual: 1 (Failure)    FN = 63                   TP = 69                
```
*At $\theta = 0.16$, the model successfully identifies **69 actual failures** in advance (up from 6), cutting missed failures in half (from 126 down to 63).*

### 3. Telecom NOC Engineering Explanation
In telecommunication networks, the operational cost of an unexpected network outage (service SLA penalties, emergency repairs, customer churn) is substantially higher than the cost of dispatching a preventive technician or running an automated diagnostic probe on a false alarm. 
Tuning the threshold from 0.50 to 0.16 transforms the model from an unusable, passive classifier into an active, proactive early-warning system that catches **over 52% of impending component failures**.

---

## Saved Artifacts

1. **Model Pipeline:** `outputs/model/logistic_regression_pipeline/`
   - Serialized Spark MLlib pipeline with fitted Imputer, StringIndexers, OneHotEncoder, VectorAssembler, and trained LogisticRegression model.
2. **Predictions File:** `outputs/predictions/test_predictions.csv`
   - Contains: `device_id`, `device_type`, `region`, `actual_failure`, `predicted_failure` (using optimized threshold 0.16), and continuous `failure_probability`.
3. **Metrics Output:** `outputs/evaluation_results/metrics.json`
   - Machine-readable JSON summary capturing both default (0.50) and optimized (0.16) metrics for dashboard rendering.
4. **Summary Text:** `outputs/evaluation_results/evaluation_summary.txt`
   - Formatted human-readable report.

---

## Limitations to Disclose in Project Presentation

1. **Synthetic Telemetry Modeling:** Telemetry distributions are mathematically generated using domain standards (ITU-T/3GPP guidelines) rather than taps on live production carrier networks.
2. **Absence of External Force Majeure Events:** Real-world carrier failures can stem from external events (physical fiber cuts, power grid outages, severe storm damage) that show no pre-failure telemetry degradation.
3. **Precision-Recall Trade-off:** Increasing recall from 4.5% to 52.3% introduces false positives ($FP = 202$). In enterprise deployments, thresholds are further calibrated against operational budget curves (technician inspection cost vs. outage downtime cost).
