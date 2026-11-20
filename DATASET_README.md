# Telecom Network Failure Prediction Dataset Documentation (Phase 1.1 Refinement)

**Project Title:** Predicting Telecom Network Failure using Apache Spark and PySpark MLlib  
**Dataset File:** `telecom_network_failures.csv`  
**Generator Script:** `generate_dataset.py`  
**Total Records:** 5,000  
**Total Columns:** 12  
**Target Variable:** `failure_next_24h` (Binary: `0` = Healthy / No failure expected, `1` = Failure expected within 24 hours)  
**Positive Failure Rate:** 13.70% (685 failures / 5,000 records)  
**Random Seed:** `42` (Deterministic reproducibility)

---

## 1. Column Dictionary & Schema

The dataset includes 12 columns covering equipment identification, categorical attributes, telemetry signals, environmental metrics, historical logs, and a prospective failure label.

| # | Column Name | PySpark Data Type | Measurement Unit | Domain / Expected Range | Description | Controlled Missing % |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | `device_id` | `StringType` | Identifier | `DEV-1001` – `DEV-6000` | Unique equipment hardware identifier. Never contains missing values. | 0.00% |
| 2 | `device_type` | `StringType` | Category | `Router`, `Switch`, `Base_Station`, `Optical_Transponder`, `Gateway` | Hardware classification within the telecom architecture. | 0.00% |
| 3 | `region` | `StringType` | Category | `North`, `South`, `East`, `West`, `Central` | Geographical network deployment operational zone. | 0.00% |
| 4 | `network_traffic_mbps` | `DoubleType` | Mbps | `50.00` – `10000.00` | Average data throughput volume passing through the node. | 0.00% |
| 5 | `signal_strength_dbm` | `DoubleType` | dBm | `-120.00` – `-45.00` | Received signal strength indicator (RSSI/RSRP). Typical safe: > -85 dBm; Critical: < -105 dBm. | 2.08% |
| 6 | `packet_loss_pct` | `DoubleType` | % (Percentage) | `0.00` – `15.00` | Percentage of transmitted packets dropped or unacknowledged. Safe: < 1.0%; Degraded: > 4.0%. | 2.14% |
| 7 | `latency_ms` | `DoubleType` | Milliseconds | `5.00` – `350.00` | Round-trip transmission delay time. Normal: 15–50 ms; Degraded: > 100 ms. | 1.58% |
| 8 | `device_status` | `StringType` | Category | `Normal`, `Degraded`, `Critical` | Current instantaneous operating state. Generated independently of the future failure label. | 1.56% |
| 9 | `device_temperature_c` | `DoubleType` | °C (Celsius) | `25.00` – `95.00` | Internal hardware operating temperature. Safe: < 65°C; Severe thermal stress: > 80°C. | 2.04% |
| 10 | `historical_faults_count`| `IntegerType`| Integer count | `0` – `12` | Total logged hardware/link incidents over the preceding 6-month operational period. | 0.00% |
| 11 | `uptime_days` | `DoubleType` | Days | `1.0` – `730.0` | Continuous operational runtime without reboot (up to 2 years). | 0.00% |
| 12 | `failure_next_24h` | `IntegerType` | Binary flag | `0` or `1` | **Target label**: Whether the component will experience a critical failure in the next 24 hours. | 0.00% |

---

## 2. Hardware Classification & Capacity Utilization

In telecommunication architectures, raw traffic in Mbps is only meaningful when contextualized by the hardware's rated line-rate capacity. A core optical transponder carrying 4,000 Mbps operates well within safe limits, whereas an access gateway handling 3,200 Mbps is near saturation.

The dataset models this via rated capacity benchmarks per device type:

| Device Type | Population Weight | Rated Capacity (Mbps) | Operating Traffic Range |
| :--- | :--- | :--- | :--- |
| `Optical_Transponder` | 10% | 10,000 Mbps | 2,000 – 9,500 Mbps |
| `Router` | 30% | 8,000 Mbps | 500 – 7,500 Mbps |
| `Base_Station` | 20% | 5,000 Mbps | 300 – 5,000 Mbps |
| `Switch` | 25% | 4,500 Mbps | 150 – 4,500 Mbps |
| `Gateway` | 15% | 3,500 Mbps | 100 – 3,500 Mbps |

**Capacity Utilization:**
$$\text{traffic\_utilization} = \min\left(\frac{\text{network\_traffic\_mbps}}{\text{rated\_capacity}}, 1.0\right)$$

High utilization increases queueing latency, packet drop rates, and thermal dissipation, contributing directly to operational failure probability.

---

## 3. How Randomness and Natural Variability Are Introduced

To avoid an artificial, rule-based toy dataset, natural variability is injected at multiple stages:

1. **Continuous Telemetry Jitter:**
   - **Latency:** Modeled using a log-normal distribution ($\mu = 3.4, \sigma = 0.52$) plus utilization queueing delay and Gaussian jitter ($\pm 3\text{ ms}$).
   - **Packet Loss:** Uses a multi-tiered skewed distribution with stochastic burst rolls and utilization correlation.
   - **Signal Strength:** Continuous normal distribution ($\mu = -76\text{ dBm}, \sigma = 14.0\text{ dBm}$) with RF fading noise.
   - **Temperature:** Ambient thermal baseline ($48^\circ\text{C} \pm 10^\circ\text{C}$) coupled with electrical heat dissipation ($\propto \text{traffic\_utilization} \times 12^\circ\text{C}$) plus thermal sensor fluctuations.

2. **Stochastic Risk Noise ($\epsilon$):**
   - A zero-mean Gaussian perturbation $\epsilon \sim \mathcal{N}(0, 0.45)$ is added to the operational risk score. This represents real-world, unmonitored anomalies such as voltage fluctuations, micro-fractures in solder joints, localized cooling fan degradation, or transient line interference.

3. **Probabilistic Label Assignment (Bernoulli Trial):**
   - Rather than cutting off at an arbitrary deterministic threshold (e.g., `if risk > 4.5: failure = 1`), failure labels are drawn as independent Bernoulli trials based on a continuous probability curve $P(\text{failure}) \in (0, 1)$.

---

## 4. Failure Label Generation Methodology (`failure_next_24h`)

The prediction target represents a **true proactive maintenance problem**: predicting component failure within the upcoming 24-hour window from current telemetry.

### Risk Formulation
A normalized composite Network Operational Stress Score ($R$) is computed:

$$R = 2.2 \cdot \widetilde{L}_{\text{packet\_loss}} + 1.8 \cdot \widetilde{T}_{\text{temp}} + 1.6 \cdot \widetilde{D}_{\text{latency}} + 1.5 \cdot \widetilde{S}_{\text{weak\_signal}} + 1.4 \cdot \widetilde{U}_{\text{traffic\_util}} + 1.2 \cdot \widetilde{F}_{\text{faults}} + 0.3 \cdot \widetilde{T}_{\text{uptime}} + \epsilon$$

Where each normalized feature $\widetilde{X}$ is scaled to $[0, 1]$:
* $\widetilde{L}_{\text{packet\_loss}} = \frac{\text{packet\_loss\_pct}}{15.0}$
* $\widetilde{T}_{\text{temp}} = \frac{\text{device\_temperature\_c} - 25.0}{95.0 - 25.0}$
* $\widetilde{D}_{\text{latency}} = \frac{\text{latency\_ms} - 5.0}{350.0 - 5.0}$
* $\widetilde{S}_{\text{weak\_signal}} = \frac{-45.0 - \text{signal\_strength\_dbm}}{-45.0 - (-120.0)}$ (lower dBm yields higher risk)
* $\widetilde{U}_{\text{traffic\_util}} = \text{traffic\_utilization}$ (utilization relative to device capacity)
* $\widetilde{F}_{\text{faults}} = \frac{\text{historical\_faults\_count}}{12.0}$
* $\widetilde{T}_{\text{uptime}} = \frac{\text{uptime\_days}}{730.0}$
* $\epsilon \sim \mathcal{N}(0, 0.45)$

### Logistic Sigmoid Transformation
The total score is mapped to a probability via the logistic sigmoid function:

$$P(\text{failure}) = \frac{1}{1 + e^{-(R - 5.10)}}$$

The final target label is assigned via:
$$\text{failure\_next\_24h} \sim \text{Bernoulli}(P(\text{failure}))$$

This calibrated offset yields exactly **13.70% positive failures** (685 failing vs. 4,315 healthy), matching the 12–15% requirement.

---

## 5. Why Healthy and Failing Records Have Overlapping Measurements

In real production telecom networks, machine learning models do not encounter perfectly separable clusters:

1. **Resilience & Survivability (Degraded without Failing):**
   - A router experiencing high latency (e.g., $120\text{ ms}$) and moderate packet loss ($4\%$) may have $P(\text{failure}) \approx 35\%$. In roughly 65% of such cases, the device **does not fail** within 24 hours because the traffic spike abates or the buffer recovers.
2. **Latent / Unmonitored Failures (Healthy-Looking Devices Failing):**
   - An optical switch operating with nominal latency ($25\text{ ms}$) and zero packet loss still has a baseline background failure probability ($P \approx 2\% - 4\%$). Across thousands of operational devices, some of these nominally healthy units **will fail** due to sudden memory corruption, power supply failure, or hardware component fatigue.
3. **Statistical Overlap:**
   - Both classes span wide minimum and maximum ranges across all telemetry metrics (e.g., packet loss for healthy devices spans $0.06\%$ to $14.48\%$, while for failing devices it spans $0.07\%$ to $14.50\%$).
   - However, the **conditional expectations (means)** clearly distinguish the classes: failing devices exhibit higher mean packet loss ($3.81\%$ vs. $2.11\%$), higher mean temperature ($57.8^\circ\text{C}$ vs. $54.0^\circ\text{C}$), weaker mean signal ($-80.1\text{ dBm}$ vs. $-75.9\text{ dBm}$), and higher capacity utilization ($61.7\%$ vs. $52.8\%$).
   - This realistic overlap ensures PySpark MLlib classifiers must learn non-trivial multi-dimensional probabilistic decision boundaries rather than trivial single-variable cutoffs.

---

## 6. Current Device Status Generation (Independence from Target)

The column `device_status` (`Normal`, `Degraded`, `Critical`) represents instantaneous monitoring alarms (such as SNMP/Syslog traps) displayed on an operations center console:

- It is computed purely from **current operational violations** (packet loss $> 2.5\%$, latency $> 75\text{ ms}$, temperature $> 65^\circ\text{C}$, signal strength $< -92\text{ dBm}$).
- Nodes with multiple severe violations transition to `Critical` or `Degraded`.
- Stochastics ensure realistic alert dampening.
- **Distribution in dataset:**
  - `Normal`: 2,916 records (59.24%)
  - `Degraded`: 1,706 records (34.66%)
  - `Critical`: 300 records (6.10%)
- **Data leakage prevention:** `device_status` is generated completely independently of `failure_next_24h`.

---

## 7. Controlled Missing Values for PySpark Data Cleaning

To support practicing PySpark missing-value imputation in Phase 2, controlled nulls (empty CSV strings `""`) were injected into 5 input columns:

- `packet_loss_pct`: 2.14% missing (107 rows)
- `signal_strength_dbm`: 2.08% missing (104 rows)
- `device_temperature_c`: 2.04% missing (102 rows)
- `latency_ms`: 1.58% missing (79 rows)
- `device_status`: 1.56% missing (78 rows)

**Zero Missing Values Guaranteed In:**
- `device_id`: 0.00% missing (Primary Key)
- `failure_next_24h`: 0.00% missing (Target Label)
- `device_type`, `region`, `network_traffic_mbps`, `historical_faults_count`, `uptime_days`: 0.00% missing

---

## 8. Limitations of Synthetic Data to Disclose in the Academic Report

When presenting this project, disclose the following academic constraints:

1. **Synthetic Telemetry Origin:** The telemetry values are mathematically generated based on domain heuristics rather than physical probes attached to live carrier infrastructure.
2. **Absence of External Force Majeure Events:** Real-world telecom outages frequently stem from external events (physical fiber cuts, utility grid power loss, severe weather destroying physical towers) that exhibit zero telemetry degradation prior to instantaneous failure.
3. **No Drift / Stationary Sampling:** Real networks experience temporal concept drift (e.g., seasonal peak holidays, firmware upgrade bugs, topological re-routing) which are not present in this cross-sectional snapshot.
4. **Model Performance Interpretation:** High evaluation scores (e.g., AUC or F1) on synthetic data validate that the PySpark distributed pipeline and MLlib algorithms correctly learn the underlying multi-variable statistical patterns; they do **not** imply equivalent operational accuracy on uncalibrated real-world production networks.
