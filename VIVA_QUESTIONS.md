# Viva Voce & Oral Examination Preparation Guide

**Project Title:** Predicting Telecom Network Failure Using Apache Spark and PySpark MLlib  
**Subject:** Cluster Computing / Distributed Machine Learning  
**Target Audience:** Undergraduate / Postgraduate College Evaluation

---

### Q1. What is Apache Spark, and why is it considered a cluster computing framework?
**Answer:**  
Apache Spark is an open-source, distributed computing framework designed for fast, large-scale data processing. It is called a "cluster computing" framework because it can distribute computation across a cluster of multiple worker nodes or run on multiple cores of a single machine. Spark manages worker memory, schedules parallel tasks, and provides fault tolerance through immutable distributed datasets.

---

### Q2. Why did we use Apache Spark instead of traditional Hadoop MapReduce?
**Answer:**  
1. **Speed & In-Memory Computing:** Hadoop MapReduce writes all intermediate results to physical disk between map and reduce stages, causing high disk I/O overhead. Spark processes data primarily in-memory (RAM), making iterative machine learning algorithms 10 to 100 times faster.
2. **Unified High-Level APIs:** Spark provides high-level abstractions like DataFrames, Spark SQL, and MLlib Pipelines, avoiding the complex low-level Java boilerplate of MapReduce.
3. **Execution DAG:** Spark builds an optimized Directed Acyclic Graph (DAG) of transformations before running, enabling query optimizations (Catalyst Optimizer).

---

### Q3. What is PySpark?
**Answer:**  
PySpark is the Python API for Apache Spark. It allows developers to write Python code while executing distributed data operations on the underlying Java/Scala Spark engine via Py4J. It combines Python's rich data science ecosystem with the scalability of Spark's distributed runtime.

---

### Q4. What is a Spark DataFrame, and how is it different from a Pandas DataFrame?
**Answer:**  
A Spark DataFrame is a distributed collection of data organized into named columns, partitioned across multiple nodes or threads. 
- **Pandas DataFrame:** Single-node and in-memory. If data exceeds the single machine's RAM, it crashes with an Out-Of-Memory error.
- **Spark DataFrame:** Distributed, lazy, and scalable. Operations are split into *transformations* (which build the execution plan without executing) and *actions* (which trigger distributed execution across partitions).

---

### Q5. What is Spark MLlib?
**Answer:**  
Spark MLlib is Apache Spark’s scalable machine learning library. It provides distributed implementations of common learning algorithms (classification, regression, clustering), feature transformers (`Imputer`, `StringIndexer`, `OneHotEncoder`, `VectorAssembler`), and `Pipeline` architectures that execute natively across distributed partitions.

---

### Q6. What is Logistic Regression, and how does it work?
**Answer:**  
Logistic Regression is a supervised statistical learning algorithm used for binary classification. It calculates a linear weighted sum of the input features ($\mathbf{w}^T \mathbf{x} + b$) and passes it through the logistic sigmoid function:
$$P(Y = 1 \mid X) = \frac{1}{1 + e^{-(\mathbf{w}^T \mathbf{x} + b)}}$$
The output is a continuous probability between $0.0$ and $1.0$. If this probability meets or exceeds a decision threshold, the model predicts class 1 (Failure); otherwise, it predicts class 0 (Healthy).

---

### Q7. Why is predicting telecom network failure formulated as a classification problem rather than regression?
**Answer:**  
The objective is to decide whether a network component will experience a critical outage or breakdown within the next 24 hours. Because the outcome is categorical and binary—either the device fails ($1$) or remains operational ($0$)—it is a binary classification task. Regression would predict a continuous number (such as remaining uptime hours), which requires continuous degradation sensor data that is rarely available across mixed hardware types.

---

### Q8. What is Feature Engineering, and why was it necessary here?
**Answer:**  
Feature engineering is the process of selecting, cleaning, transforming, and formatting raw data into features that machine learning algorithms can mathematically process. Raw data contains missing values, string categories, and unnormalized scales. We engineered capacity utilization ($\text{traffic} / \text{rated\_capacity}$), imputed missing sensor telemetry, converted string categories into binary vectors, and assembled all features into a unified vector.

---

### Q9. Why must we handle missing values, and how did we handle them in PySpark?
**Answer:**  
Machine learning algorithms rely on matrix algebra; rows with missing values (`NULL` or `NaN`) cause mathematical errors during vector assembly.
- For **numerical features** (`signal_strength_dbm`, `packet_loss_pct`, `latency_ms`, `device_temperature_c`), we used Spark MLlib's `Imputer` with the **median** strategy.
- For the **categorical feature** (`device_status`), we replaced missing entries with the **mode** (most frequent category, `'Normal'`), computed strictly from the training dataset.
- We strictly avoided imputing the primary key (`device_id`) and the target label (`failure_next_24h`).

---

### Q10. What is `StringIndexer`, and why is it used?
**Answer:**  
`StringIndexer` encodes string column categories into numerical category indices (from $0$ to $k-1$), ordered by category frequency. Machine learning algorithms cannot perform mathematical operations on raw text strings like `'Router'` or `'Switch'`.

---

### Q11. What is `OneHotEncoder`, and why do we use it after `StringIndexer`?
**Answer:**  
`StringIndexer` assigns arbitrary numbers (e.g., Router = 0, Switch = 1, Base_Station = 2). If fed directly into a linear model, the algorithm would incorrectly assume that `Base_Station` ($2$) has twice the mathematical magnitude of `Switch` ($1$). `OneHotEncoder` converts each index into a sparse binary vector (e.g., `[1, 0, 0]`, `[0, 1, 0]`), ensuring all categories are treated as equidistant, orthogonal features without artificial ordering.

---

### Q12. What is `VectorAssembler`, and why is it mandatory in Spark MLlib?
**Answer:**  
In Scikit-learn, models accept a 2D matrix or list of columns. In contrast, Spark MLlib requires all independent feature columns to be combined into a single, unified `Vector` column (typically named `'features'`) per record. `VectorAssembler` takes all numerical columns and one-hot vectors and concatenates them into this single vector column.

---

### Q13. Why did we split the data into three sets (Training, Validation, and Testing) instead of just two?
**Answer:**  
- **Training Set (65.84%):** Used strictly to learn the model weights and fit preprocessing transformations.
- **Validation Set (15.00%):** Used strictly to tune the classification decision threshold to maximize the F1-score on imbalanced data.
- **Testing Set (19.16%):** Held-out and strictly untouched until final evaluation to provide an unbiased, honest measurement of generalization performance.  
If we had tuned the threshold on the test set, we would have committed "data snooping" (optimistic evaluation bias).

---

### Q14. What are Precision and Recall, and which one is more critical in telecom failure prediction?
**Answer:**  
- **Precision:** Out of all devices the model predicted would fail, what fraction actually failed?  
  $$\text{Precision} = \frac{TP}{TP + FP}$$
- **Recall:** Out of all devices that genuinely experienced failure, what fraction did the model catch?  
  $$\text{Recall} = \frac{TP}{TP + FN}$$
- **Which is more critical?** In a telecom Network Operations Center (NOC), **Recall** is more critical. Missing an actual failure ($FN$) causes catastrophic network downtime, SLA financial penalties, and customer churn. A false alarm ($FP$) only results in an automated diagnostic test or technician check.

---

### Q15. What is a Confusion Matrix, and what were our project results?
**Answer:**  
A confusion matrix is a $2 \times 2$ table showing the counts of actual versus predicted classes:
- **True Negatives (TN = 624):** Healthy devices correctly predicted as healthy.
- **False Positives (FP = 202):** Healthy devices flagged as predicted failures (preventive inspection alerts).
- **False Negatives (FN = 63):** Actual failures that the model missed.
- **True Positives (TP = 69):** Imminent failures correctly identified 24 hours in advance.

---

### Q16. What is ROC-AUC, and what was our score?
**Answer:**  
ROC-AUC stands for *Receiver Operating Characteristic - Area Under the Curve*. It evaluates the model's ranking ability across all possible classification thresholds. An AUC of $0.50$ represents random guessing, while $1.0$ represents perfect separation. Our model achieved **0.6932 ($\approx 0.70$)**, indicating that the model has meaningful discriminative power in ranking high-risk devices above low-risk devices.

---

### Q17. Why was the decision threshold adjusted from 0.50 to 0.16?
**Answer:**  
The base failure rate in the dataset is naturally low (~13.78%). At the standard default threshold of 0.50, the model demanded $>50\%$ certainty, predicting only **7 failures** and missing **126 actual outages** (Recall was only **4.55%**, and F1 was **8.63%**).  
By tuning the threshold on the validation set, **$\theta = 0.16$** was selected because it maximized the validation F1-score. On the test set, this improved recall to **52.27%** (catching 69 failures) and raised the F1-score to **34.24%**, creating an actionable early-warning system.

---

### Q18. What does the F1-score represent, and why is accuracy misleading here?
**Answer:**  
Accuracy is misleading because ~86% of the devices are healthy. A dummy model that predicts "0 (Healthy)" for every single device would achieve **86% accuracy** while catching **zero failures**.  
The F1-score is the harmonic mean of Precision and Recall:
$$F1 = 2 \cdot \frac{\text{Precision} \cdot \text{Recall}}{\text{Precision} + \text{Recall}}$$
It measures how well the model balances false alarms with caught failures, providing an honest evaluation for imbalanced classification.

---

### Q19. Why did we use a synthetic dataset instead of real telecom carrier data?
**Answer:**  
Major telecom carriers (e.g., AT&T, Verizon, Cisco) treat physical failure logs, topology, and packet captures as strictly proprietary and confidential (NDA) due to national security, infrastructure protection, and user privacy laws. Public datasets either anonymize all telemetry into meaningless codes (like Telstra) or record concurrent congestion rather than future component failure. Synthetic generation allowed us to define physical units (dBm, ms, packet drop %) and model a true **24-hour predictive horizon**.

---

### Q20. What are the key limitations of this project that should be disclosed?
**Answer:**  
1. **Synthetic Nature:** Telemetry distributions are mathematically simulated rather than pulled from live production fiber/microwave taps.
2. **Absence of External Catastrophes:** Real-world carrier failures can stem from external unmonitored events (physical backhoe fiber cuts, lightning strikes, grid blackouts) that show zero pre-failure telemetry degradation.
3. **Stationarity:** The dataset is a cross-sectional snapshot that does not model seasonal holiday traffic surges or multi-year concept drift.
4. **Scope:** Evaluated in standalone local Spark mode (`local[*]`) on 5,000 records; enterprise deployment would scale across a physical multi-node Spark cluster with Kafka telemetry streaming.
