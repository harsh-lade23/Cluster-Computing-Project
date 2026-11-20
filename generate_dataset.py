"""
Telecom Network Failure Prediction Dataset Generator (Phase 1.1 Refinement)
Generates a realistic synthetic telecom monitoring dataset for PySpark MLlib.

Key Enhancements (Phase 1.1):
- Traffic load contribution: Device-type capacity utilization contributes moderately to failure risk.
- Natural variability & distribution overlap: Features exhibit realistic stochastic variations;
  healthy and failing devices have overlapping measurements rather than hard threshold separations.
- All three device status categories represented (Normal, Degraded, Critical).
- Fully reproducible via fixed random seed (seed=42).

Output: telecom_network_failures.csv (5,000 records, 12 columns)
"""

import csv
import hashlib
import math
import random
from collections import Counter

# Set fixed seed for deterministic reproducibility
RANDOM_SEED = 42
TOTAL_RECORDS = 5000

OUTPUT_FILE = "telecom_network_failures.csv"

# Categorical domain definitions
DEVICE_TYPES = ["Router", "Switch", "Base_Station", "Optical_Transponder", "Gateway"]
DEVICE_TYPE_WEIGHTS = [0.30, 0.25, 0.20, 0.10, 0.15]

# Rated line-rate capacity per device type (Mbps)
DEVICE_CAPACITY_MBPS = {
    "Optical_Transponder": 10000.0,
    "Router": 8000.0,
    "Base_Station": 5000.0,
    "Switch": 4500.0,
    "Gateway": 3500.0,
}

REGIONS = ["North", "South", "East", "West", "Central"]
REGION_WEIGHTS = [0.22, 0.20, 0.19, 0.21, 0.18]

DEVICE_STATUS_CATEGORIES = ["Normal", "Degraded", "Critical"]

# Controlled missing value rates for permitted input columns
# device_id and failure_next_24h NEVER have missing values
MISSING_RATES = {
    "signal_strength_dbm": 0.024,   # ~2.4% missing (sensor timeout)
    "packet_loss_pct": 0.020,       # ~2.0% missing (dropped telemetry)
    "latency_ms": 0.018,            # ~1.8% missing (ping timeout)
    "device_temperature_c": 0.022,  # ~2.2% missing (thermal probe read error)
    "device_status": 0.016,         # ~1.6% missing (unclassified state)
}


def sigmoid(x: float) -> float:
    """Standard logistic sigmoid function with clipping to prevent overflow."""
    return 1.0 / (1.0 + math.exp(-max(min(x, 20.0), -20.0)))


def generate_records(seed: int = RANDOM_SEED, num_records: int = TOTAL_RECORDS):
    """
    Generates synthetic telecom records with physical correlations, natural variability,
    and probabilistic label assignment.
    """
    random.seed(seed)
    records = []

    for i in range(1, num_records + 1):
        device_id = f"DEV-{1000 + i}"

        # 1. Device Type & Region
        device_type = random.choices(DEVICE_TYPES, weights=DEVICE_TYPE_WEIGHTS, k=1)[0]
        region = random.choices(REGIONS, weights=REGION_WEIGHTS, k=1)[0]

        # 2. Network Traffic & Utilization
        # Traffic generated proportionally to rated capacity with stochastic variation
        capacity = DEVICE_CAPACITY_MBPS[device_type]
        base_traffic = random.uniform(0.12 * capacity, 0.96 * capacity)
        traffic_mbps = round(max(50.0, min(10000.0, base_traffic)), 2)
        traffic_utilization = min(traffic_mbps / capacity, 1.0)

        # 3. Latency (ms): Log-normal baseline + slight traffic queueing effect + natural jitter
        latency_raw = random.lognormvariate(3.4, 0.52) + (traffic_utilization * 15.0) + random.uniform(-3.0, 3.0)
        latency_ms = round(max(5.0, min(350.0, latency_raw)), 2)

        # 4. Packet Loss (%): Skewed distribution with occasional congestion-induced loss
        pkt_roll = random.random()
        if pkt_roll < 0.72:
            pkt_raw = random.uniform(0.0, 1.2) + (traffic_utilization * 0.4)
        elif pkt_roll < 0.88:
            pkt_raw = random.uniform(1.2, 4.5) + (traffic_utilization * 0.8)
        else:
            pkt_raw = random.uniform(4.5, 14.5)
        packet_loss_pct = round(max(0.0, min(15.0, pkt_raw)), 2)

        # 5. Signal Strength (dBm): Physical transmission range [-120.0, -45.0]
        signal_raw = random.normalvariate(-76.0, 14.0) + random.uniform(-2.0, 2.0)
        signal_strength_dbm = round(max(-120.0, min(-45.0, signal_raw)), 2)

        # 6. Operating Temperature (°C): Ambient baseline + thermal load from utilization
        temp_raw = random.normalvariate(48.0, 10.0) + (traffic_utilization * 12.0) + random.uniform(-2.0, 2.0)
        device_temperature_c = round(max(25.0, min(95.0, temp_raw)), 2)

        # 7. Historical Faults Count: 0 to 12 logged incidents in prior 6 months
        fault_weights = [0.42, 0.25, 0.14, 0.08, 0.04, 0.03, 0.015, 0.01, 0.007, 0.004, 0.002, 0.001, 0.001]
        historical_faults_count = random.choices(range(13), weights=fault_weights, k=1)[0]

        # 8. Uptime Days: 1.0 to 730.0 days
        uptime_days = round(random.uniform(1.0, 730.0), 1)

        # 9. Current Device Status (Normal, Degraded, Critical)
        # Evaluated purely from CURRENT instantaneous operating conditions,
        # completely independent of the future failure label.
        condition_score = 0
        if packet_loss_pct > 6.0:
            condition_score += 3
        elif packet_loss_pct > 2.5:
            condition_score += 1

        if latency_ms > 140.0:
            condition_score += 3
        elif latency_ms > 75.0:
            condition_score += 1

        if device_temperature_c > 78.0:
            condition_score += 3
        elif device_temperature_c > 65.0:
            condition_score += 1

        if signal_strength_dbm < -105.0:
            condition_score += 3
        elif signal_strength_dbm < -92.0:
            condition_score += 1

        # Assign status with stochastic transition reflecting real-world alert debouncing
        if condition_score >= 4:
            device_status = random.choices(["Critical", "Degraded"], weights=[0.80, 0.20], k=1)[0]
        elif condition_score >= 1:
            device_status = random.choices(["Degraded", "Normal", "Critical"], weights=[0.72, 0.22, 0.06], k=1)[0]
        else:
            device_status = random.choices(["Normal", "Degraded"], weights=[0.95, 0.05], k=1)[0]

        # 10. Future Failure Label Generation: failure_next_24h (0 or 1)
        # Physical risk factors normalized to [0, 1]:
        norm_packet_loss = packet_loss_pct / 15.0
        norm_temp = (device_temperature_c - 25.0) / (95.0 - 25.0)
        norm_latency = (latency_ms - 5.0) / (350.0 - 5.0)
        norm_weak_signal = (-45.0 - signal_strength_dbm) / (-45.0 - (-120.0))
        norm_traffic_util = traffic_utilization  # High utilization increases failure risk
        norm_faults = historical_faults_count / 12.0
        norm_uptime = uptime_days / 730.0

        # Weighted risk score including traffic utilization
        risk_score = (
            2.2 * norm_packet_loss +
            1.8 * norm_temp +
            1.6 * norm_latency +
            1.5 * norm_weak_signal +
            1.4 * norm_traffic_util +   # Network traffic contribution
            1.2 * norm_faults +
            0.3 * norm_uptime
        )

        # Moderate Gaussian noise introduces realistic variability & prevents deterministic thresholds
        noise = random.normalvariate(0.0, 0.45)
        total_risk = risk_score + noise

        # Logistic sigmoid probability calibrated to yield ~13.5% failure probability
        prob_failure = sigmoid(total_risk - 5.10)
        failure_next_24h = 1 if random.random() < prob_failure else 0

        record = {
            "device_id": device_id,
            "device_type": device_type,
            "region": region,
            "network_traffic_mbps": traffic_mbps,
            "signal_strength_dbm": signal_strength_dbm,
            "packet_loss_pct": packet_loss_pct,
            "latency_ms": latency_ms,
            "device_status": device_status,
            "device_temperature_c": device_temperature_c,
            "historical_faults_count": historical_faults_count,
            "uptime_days": uptime_days,
            "failure_next_24h": failure_next_24h,
        }
        records.append(record)

    return records


def inject_missing_values(records, missing_rates=MISSING_RATES, seed: int = RANDOM_SEED + 1):
    """
    Introduces controlled missing values (empty strings) into permitted input columns.
    device_id and failure_next_24h are strictly protected from missing values.
    """
    random.seed(seed)
    modified_records = []

    for rec in records:
        rec_copy = dict(rec)
        for col, rate in missing_rates.items():
            if random.random() < rate:
                rec_copy[col] = ""  # Represents null in CSV
        modified_records.append(rec_copy)

    return modified_records


def save_to_csv(records, filename=OUTPUT_FILE):
    """Writes record dictionaries to CSV."""
    if not records:
        return
    fieldnames = list(records[0].keys())
    with open(filename, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)


def compute_file_hash(filename=OUTPUT_FILE) -> str:
    """Computes SHA-256 hash of the generated CSV file."""
    sha = hashlib.sha256()
    with open(filename, "rb") as f:
        while chunk := f.read(8192):
            sha.update(chunk)
    return sha.hexdigest()


def validate_dataset(filename=OUTPUT_FILE):
    """
    Performs full validation of the generated dataset:
    - Exactly 5,000 records
    - All 12 required columns exist
    - Target contains only 0 and 1
    - Target distribution is approximately 12–15%
    - Missing values exist only in permitted columns
    - Valid numerical ranges
    - Valid categorical members
    - Grouped feature statistics & traffic contribution verification
    - Reproducibility test
    """
    with open(filename, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        rows = list(reader)

    print("=" * 70)
    print("DATASET VALIDATION REPORT (PHASE 1.1 REFINEMENT)")
    print("=" * 70)

    # 1. Row count
    row_count = len(rows)
    print(f"Total Records: {row_count} (Expected: {TOTAL_RECORDS}) -> {'PASS' if row_count == TOTAL_RECORDS else 'FAIL'}")

    # 2. Column count and names
    expected_columns = [
        "device_id", "device_type", "region", "network_traffic_mbps",
        "signal_strength_dbm", "packet_loss_pct", "latency_ms", "device_status",
        "device_temperature_c", "historical_faults_count", "uptime_days", "failure_next_24h"
    ]
    col_match = (fieldnames == expected_columns)
    print(f"Columns Count: {len(fieldnames)} (Expected: 12) -> {'PASS' if col_match else 'FAIL'}")

    # 3. Missing values analysis
    missing_counts = {col: 0 for col in expected_columns}
    for row in rows:
        for col in expected_columns:
            if row[col] == "" or row[col] is None:
                missing_counts[col] += 1

    print("\nMissing Values per Column:")
    for col, count in missing_counts.items():
        pct = (count / row_count) * 100
        if col in ["device_id", "failure_next_24h"]:
            status = "PASS (0 missing)" if count == 0 else "VIOLATION!"
        else:
            status = f"PASS ({pct:.2f}% controlled missing)" if count > 0 else "PASS (0 missing)"
        print(f"  - {col:<26}: {count:>4} missing ({pct:>5.2f}%) [{status}]")

    # 4. Target variable validation
    target_counts = Counter(row["failure_next_24h"] for row in rows)
    zeros = target_counts.get("0", 0)
    ones = target_counts.get("1", 0)
    failure_pct = (ones / row_count) * 100
    target_valid = set(target_counts.keys()).issubset({"0", "1"})
    pct_valid = 12.0 <= failure_pct <= 15.0

    print("\nTarget Variable (failure_next_24h) Distribution:")
    print(f"  - Class 0 (Healthy / No Failure) : {zeros} ({zeros / row_count * 100:.2f}%)")
    print(f"  - Class 1 (Failure within 24h)   : {ones} ({failure_pct:.2f}%)")
    print(f"  - Target Binary Check            : {'PASS' if target_valid else 'FAIL'}")
    print(f"  - 12-15% Range Check             : {'PASS' if pct_valid else 'FAIL'}")

    # 5. Device Status Distribution
    status_counts = Counter(row["device_status"] for row in rows if row["device_status"] != "")
    status_total = sum(status_counts.values())
    all_statuses_present = all(st in status_counts for st in DEVICE_STATUS_CATEGORIES)

    print("\nDevice Status Distribution:")
    for st in DEVICE_STATUS_CATEGORIES:
        count = status_counts.get(st, 0)
        pct = (count / status_total) * 100
        print(f"  - {st:<12}: {count:>4} ({pct:>5.2f}%)")
    print(f"  - All 3 Statuses Present Check   : {'PASS' if all_statuses_present else 'FAIL'}")

    # 6. Categorical checks
    valid_device_types = set(DEVICE_TYPES)
    valid_regions = set(REGIONS)
    valid_statuses = set(DEVICE_STATUS_CATEGORIES)

    invalid_types = [r["device_type"] for r in rows if r["device_type"] not in valid_device_types]
    invalid_regions = [r["region"] for r in rows if r["region"] not in valid_regions]
    invalid_statuses = [r["device_status"] for r in rows if r["device_status"] != "" and r["device_status"] not in valid_statuses]

    print("\nCategorical Domain Validation:")
    print(f"  - device_type valid              : {'PASS' if not invalid_types else 'FAIL'}")
    print(f"  - region valid                   : {'PASS' if not invalid_regions else 'FAIL'}")
    print(f"  - device_status valid            : {'PASS' if not invalid_statuses else 'FAIL'}")

    # 7. Numerical ranges checks
    range_errors = []
    for idx, r in enumerate(rows, start=1):
        if r["network_traffic_mbps"] != "":
            val = float(r["network_traffic_mbps"])
            if not (50.0 <= val <= 10000.0):
                range_errors.append(f"Row {idx}: traffic {val} out of bounds")
        if r["signal_strength_dbm"] != "":
            val = float(r["signal_strength_dbm"])
            if not (-120.0 <= val <= -45.0):
                range_errors.append(f"Row {idx}: signal {val} out of bounds")
        if r["packet_loss_pct"] != "":
            val = float(r["packet_loss_pct"])
            if not (0.0 <= val <= 15.0):
                range_errors.append(f"Row {idx}: packet_loss {val} out of bounds")
        if r["latency_ms"] != "":
            val = float(r["latency_ms"])
            if not (5.0 <= val <= 350.0):
                range_errors.append(f"Row {idx}: latency {val} out of bounds")
        if r["device_temperature_c"] != "":
            val = float(r["device_temperature_c"])
            if not (25.0 <= val <= 95.0):
                range_errors.append(f"Row {idx}: temp {val} out of bounds")
        if r["historical_faults_count"] != "":
            val = int(r["historical_faults_count"])
            if not (0 <= val <= 12):
                range_errors.append(f"Row {idx}: faults {val} out of bounds")
        if r["uptime_days"] != "":
            val = float(r["uptime_days"])
            if not (1.0 <= val <= 730.0):
                range_errors.append(f"Row {idx}: uptime {val} out of bounds")

    print("\nNumerical Range Validation:")
    print(f"  - All numerical bounds           : {'PASS' if not range_errors else f'FAIL ({len(range_errors)} errors)'}")

    # 8. Feature Statistics Grouped by Target (Demonstrating Overlap & Correlation)
    print("\nFeature Statistics Grouped by Failure Label (Mean [Min, Max]):")
    print(f"{'Feature':<24} | {'Healthy (failure=0)':<30} | {'Failing (failure=1)':<30}")
    print("-" * 90)

    numeric_cols = [
        "network_traffic_mbps", "signal_strength_dbm", "packet_loss_pct",
        "latency_ms", "device_temperature_c", "historical_faults_count", "uptime_days"
    ]

    for col in numeric_cols:
        vals_0 = [float(r[col]) for r in rows if r["failure_next_24h"] == "0" and r[col] != ""]
        vals_1 = [float(r[col]) for r in rows if r["failure_next_24h"] == "1" and r[col] != ""]
        mean_0, min_0, max_0 = sum(vals_0) / len(vals_0), min(vals_0), max(vals_0)
        mean_1, min_1, max_1 = sum(vals_1) / len(vals_1), min(vals_1), max(vals_1)
        str_0 = f"{mean_0:>8.2f} [{min_0:>6.2f}, {max_0:>6.2f}]"
        str_1 = f"{mean_1:>8.2f} [{min_1:>6.2f}, {max_1:>6.2f}]"
        print(f"{col:<24} | {str_0:<30} | {str_1:<30}")

    # 9. Confirmation of Network Traffic Contribution
    # Check traffic and capacity utilization comparison
    util_0, util_1 = [], []
    for r in rows:
        if r["network_traffic_mbps"] != "":
            cap = DEVICE_CAPACITY_MBPS[r["device_type"]]
            util = float(r["network_traffic_mbps"]) / cap
            if r["failure_next_24h"] == "0":
                util_0.append(util)
            else:
                util_1.append(util)
    mean_util_0 = sum(util_0) / len(util_0)
    mean_util_1 = sum(util_1) / len(util_1)
    traffic_diff = mean_util_1 - mean_util_0

    print("\nNetwork Traffic Contribution Confirmation:")
    print(f"  - Mean Capacity Utilization (Healthy) : {mean_util_0 * 100:.2f}%")
    print(f"  - Mean Capacity Utilization (Failing) : {mean_util_1 * 100:.2f}%")
    print(f"  - Relative Utilization Premium        : +{traffic_diff * 100:.2f}%")
    print(f"  - Traffic Risk Contribution Check     : {'PASS (+ contribution confirmed)' if traffic_diff > 0 else 'FAIL'}")

    # 10. Reproducibility Test
    hash_original = compute_file_hash(filename)
    test_clean = generate_records(seed=RANDOM_SEED, num_records=TOTAL_RECORDS)
    test_modified = inject_missing_values(test_clean, missing_rates=MISSING_RATES, seed=RANDOM_SEED + 1)
    save_to_csv(test_modified, "test_reproducibility.csv")
    hash_reproduced = compute_file_hash("test_reproducibility.csv")
    import os
    os.remove("test_reproducibility.csv")

    reproducible = (hash_original == hash_reproduced)
    print("\nReproducibility Verification:")
    print(f"  - File SHA-256 Hash                   : {hash_original[:16]}...")
    print(f"  - Deterministic Reproducibility Check : {'PASS (100% Bit-for-Bit Identical)' if reproducible else 'FAIL'}")

    print("=" * 70)
    overall_pass = (
        row_count == TOTAL_RECORDS and
        col_match and
        missing_counts["device_id"] == 0 and
        missing_counts["failure_next_24h"] == 0 and
        target_valid and
        pct_valid and
        all_statuses_present and
        not invalid_types and
        not invalid_regions and
        not invalid_statuses and
        not range_errors and
        traffic_diff > 0 and
        reproducible
    )
    print(f"OVERALL VALIDATION STATUS: {'ALL CHECKS PASSED' if overall_pass else 'VALIDATION FAILED'}")
    print("=" * 70)
    return overall_pass


if __name__ == "__main__":
    print(f"Generating {TOTAL_RECORDS} synthetic telecom records with seed {RANDOM_SEED}...")
    clean_records = generate_records(seed=RANDOM_SEED, num_records=TOTAL_RECORDS)
    final_records = inject_missing_values(clean_records, missing_rates=MISSING_RATES, seed=RANDOM_SEED + 1)
    save_to_csv(final_records, OUTPUT_FILE)
    print(f"Dataset saved to '{OUTPUT_FILE}'.")
    validate_dataset(OUTPUT_FILE)
