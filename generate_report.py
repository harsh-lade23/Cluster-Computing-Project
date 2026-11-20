"""
Generate Project Report in DOCX and PDF formats
================================================
Creates:
- PROJECT_REPORT.docx (using python-docx)
- PROJECT_REPORT.pdf (using reportlab)

Incorporates:
- All 17 required academic sections
- Embedded dashboard screenshots
- Formatted tables, code blocks, and callout boxes
- Exact project metrics and terminology
"""

import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage, KeepTogether, PageBreak, HRFlowable
)
from reportlab.pdfgen import canvas

# ---------------------------------------------------------------------------
# COLOR PALETTE
# ---------------------------------------------------------------------------
PRIMARY_HEX = "#0F172A"      # Slate 900
SECONDARY_HEX = "#0284C7"    # Sky 600
ACCENT_HEX = "#38BDF8"       # Sky 400
TEXT_DARK_HEX = "#1E293B"    # Slate 800
BG_LIGHT_HEX = "#F8FAFC"     # Slate 50
BORDER_HEX = "#CBD5E1"       # Slate 300


# ===========================================================================
# 1. GENERATE DOCX REPORT
# ===========================================================================
def set_cell_background(cell, fill_hex):
    """Sets background color of a docx table cell."""
    tcPr = cell._element.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)


def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    """Sets padding for a docx cell."""
    tcPr = cell._element.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)


def add_callout(doc, text, title="NOTE"):
    """Adds a callout box to docx."""
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = tbl.cell(0, 0)
    set_cell_background(cell, "F0F9FF")
    set_cell_margins(cell, top=140, bottom=140, left=200, right=180)
    
    # Border
    tcPr = cell._element.get_or_add_tcPr()
    borders = parse_xml(
        f'<w:tcBorders {nsdecls("w")}>'
        f'  <w:left w:val="single" w:sz="24" w:space="0" w:color="0284C7"/>'
        f'  <w:top w:val="none"/>'
        f'  <w:right w:val="none"/>'
        f'  <w:bottom w:val="none"/>'
        f'</w:tcBorders>'
    )
    tcPr.append(borders)
    
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(2)
    run_t = p.add_run(f"[{title}] ")
    run_t.bold = True
    run_t.font.color.rgb = RGBColor(2, 132, 199)
    run_t.font.size = Pt(10)
    
    run_txt = p.add_run(text)
    run_txt.font.size = Pt(9.5)
    run_txt.font.color.rgb = RGBColor(30, 41, 59)
    doc.add_paragraph().paragraph_format.space_after = Pt(4)


def add_code_block(doc, code_str):
    """Adds a styled code block to docx."""
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = tbl.cell(0, 0)
    set_cell_background(cell, "F8FAFC")
    set_cell_margins(cell, top=120, bottom=120, left=160, right=160)
    
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    r = p.add_run(code_str)
    r.font.name = "Courier New"
    r.font.size = Pt(8.5)
    r.font.color.rgb = RGBColor(15, 23, 42)
    doc.add_paragraph().paragraph_format.space_after = Pt(4)


def format_table_header(table, col_names, col_widths=None):
    """Formats the header row of a table."""
    hdr_cells = table.rows[0].cells
    for i, name in enumerate(col_names):
        hdr_cells[i].text = name
        set_cell_background(hdr_cells[i], "0F172A")
        set_cell_margins(hdr_cells[i], top=120, bottom=120, left=140, right=140)
        p = hdr_cells[i].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for run in p.runs:
            run.font.bold = True
            run.font.color.rgb = RGBColor(255, 255, 255)
            run.font.size = Pt(9.5)
    if col_widths:
        for row in table.rows:
            for i, w in enumerate(col_widths):
                row.cells[i].width = Inches(w)


def style_table_rows(table):
    """Alternates row shading on a table."""
    for r_idx, row in enumerate(table.rows[1:], start=1):
        bg = "F8FAFC" if r_idx % 2 == 1 else "FFFFFF"
        for cell in row.cells:
            set_cell_background(cell, bg)
            set_cell_margins(cell, top=80, bottom=80, left=120, right=120)
            p = cell.paragraphs[0]
            for run in p.runs:
                run.font.size = Pt(9)
                run.font.color.rgb = RGBColor(30, 41, 59)


def build_docx_report(output_filename="PROJECT_REPORT.docx"):
    print(f"Generating DOCX report: {output_filename}...")
    doc = docx.Document()
    
    # Page setup: 1-inch margins
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)
        section.different_first_page_header_footer = True
        
        # Header / Footer
        footer = section.footer
        p_ft = footer.paragraphs[0]
        p_ft.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        r_ft = p_ft.add_run("Predicting Telecom Network Failure Using PySpark MLlib | Academic Project Report")
        r_ft.font.size = Pt(8.5)
        r_ft.font.color.rgb = RGBColor(148, 163, 184)

    # -----------------------------------------------------------------------
    # 1. TITLE PAGE
    # -----------------------------------------------------------------------
    for _ in range(3):
        doc.add_paragraph()
        
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_title = p_title.add_run("Predicting Telecom Network Failure Using Apache Spark and PySpark MLlib")
    r_title.bold = True
    r_title.font.size = Pt(24)
    r_title.font.color.rgb = RGBColor(15, 23, 42)
    p_title.paragraph_format.space_after = Pt(12)
    
    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_sub = p_sub.add_run("A Scalable Machine Learning Pipeline with Decision Threshold Optimization and Interactive NOC Dashboard")
    r_sub.font.size = Pt(13)
    r_sub.font.italic = True
    r_sub.font.color.rgb = RGBColor(71, 85, 105)
    p_sub.paragraph_format.space_after = Pt(36)
    
    p_badge = doc.add_paragraph()
    p_badge.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_badge = p_badge.add_run("ACADEMIC PROJECT REPORT")
    r_badge.bold = True
    r_badge.font.size = Pt(11)
    r_badge.font.color.rgb = RGBColor(2, 132, 199)
    p_badge.paragraph_format.space_after = Pt(48)
    
    p_meta = doc.add_paragraph()
    p_meta.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_meta.paragraph_format.line_spacing = 1.3
    
    meta_lines = [
        ("Subject:", "Cluster Computing (CS-401)"),
        ("Student Name:", "[Student Name]"),
        ("Roll Number:", "[Roll Number / Student ID]"),
        ("Department:", "[Department of Computer Science & Engineering]"),
        ("Institution:", "[University / Institute Name]"),
        ("Academic Year:", "2026 – 2027"),
    ]
    for label, val in meta_lines:
        r_lbl = p_meta.add_run(f"{label:<18} ")
        r_lbl.bold = True
        r_lbl.font.size = Pt(10.5)
        r_lbl.font.color.rgb = RGBColor(51, 65, 85)
        
        r_v = p_meta.add_run(f"{val}\n")
        r_v.font.size = Pt(10.5)
        r_v.font.color.rgb = RGBColor(15, 23, 42)
        
    doc.add_page_break()

    # -----------------------------------------------------------------------
    # 2. ABSTRACT
    # -----------------------------------------------------------------------
    h = doc.add_heading("Abstract", level=1)
    h.paragraph_format.space_after = Pt(8)
    
    p = doc.add_paragraph(
        "Modern telecommunications infrastructure requires high reliability to maintain stringent Service Level Agreements "
        "(SLAs) and avert costly network disruptions. Traditional maintenance strategies rely heavily on reactive troubleshooting "
        "after component failure occurs, resulting in severe downtime. This project implements a distributed proactive failure-prediction "
        "pipeline using Apache Spark and PySpark MLlib in local standalone mode. A standardized 5,000-record network monitoring dataset "
        "featuring 12 operational and environmental columns was synthesized using domain telemetry heuristics (packet loss, latency, "
        "signal strength, operating temperature, and rated line-rate capacity utilization). "
    )
    p.paragraph_format.line_spacing = 1.15
    p.paragraph_format.space_after = Pt(6)
    
    p = doc.add_paragraph(
        "To prevent data leakage, a three-way split was implemented: Training (65.84%), Validation (15.00%), and Testing (19.16%). "
        "Distributed preprocessing incorporated median numerical imputation via Spark ML Imputer, training-mode categorical imputation, "
        "StringIndexer, OneHotEncoder, and VectorAssembler into an integrated Spark ML Pipeline. Because hardware failure is naturally "
        "infrequent (~13.78%), the standard 0.50 decision threshold was overly conservative, yielding only 4.55% recall. Decision threshold "
        "optimization conducted strictly on the validation set identified an optimal threshold of 0.16 (maximizing validation F1 at 31.61%). "
        "Evaluated on the held-out test partition (958 records), the optimized model achieved 52.27% recall (catching 69 of 132 impending failures), "
        "a precision of 25.46%, an F1-score of 34.24%, and an area under the ROC curve (ROC-AUC) of 0.6932. Finally, an interactive Network "
        "Operations Center (NOC) dashboard was developed using Streamlit and Plotly to enable risk exploration and regional filtering. "
        "All telemetry and outcomes are simulated for academic cluster computing demonstration."
    )
    p.paragraph_format.line_spacing = 1.15
    p.paragraph_format.space_after = Pt(12)

    # -----------------------------------------------------------------------
    # 3. INTRODUCTION
    # -----------------------------------------------------------------------
    doc.add_heading("1. Introduction", level=1)
    doc.add_paragraph(
        "Telecommunications carrier networks consist of thousands of geographically dispersed, interconnected active devices—including "
        "core routers, aggregation switches, cellular base stations, optical transponders, and customer gateways. These nodes continuously "
        "transmit massive volumes of voice, data, and multimedia traffic under changing physical and environmental conditions."
    )
    doc.add_paragraph(
        "Unplanned equipment breakdowns directly trigger service outages, packet drops, customer churn, and severe financial penalties. "
        "Historically, telecom network maintenance has adhered to two primary paradigms:\n"
        "1. Reactive Maintenance: Technicians diagnose and replace hardware only after total component failure triggers customer alarms.\n"
        "2. Preventive Maintenance: Hardware is periodically serviced or replaced according to fixed calendar intervals regardless of condition.\n\n"
        "Predictive Maintenance represents a modern paradigm shift: by continuously monitoring hardware telemetry (transmission delay, "
        "packet drops, radio signal degradation, chassis thermal load, and bandwidth utilization), machine learning models can detect "
        "subtle pre-failure degradation signatures and flag at-risk equipment hours or days in advance."
    )

    # -----------------------------------------------------------------------
    # 4. PROBLEM STATEMENT & OBJECTIVES
    # -----------------------------------------------------------------------
    doc.add_heading("2. Problem Statement", level=1)
    doc.add_paragraph(
        "Given continuous operational telemetry from network hardware components, the challenge is to formulate a distributed binary "
        "classification pipeline that predicts whether a specific component will experience an outage or critical breakdown within "
        "the upcoming 24-hour window (failure_next_24h = 1 vs. 0). "
        "This problem is complicated by three realistic operational factors:\n"
        "1. Class Imbalance: Hardware failures are relatively rare events (~13% to 14% base rate), causing standard classifiers to bias toward the majority healthy class.\n"
        "2. Missing Telemetry: Physical sensor timeouts, transmission glitches, and unclassified warning states introduce missing values.\n"
        "3. Distributed Computation: Modern telecom monitoring generates streaming telemetry that single-node architectures cannot scale to process without distributed engines like Apache Spark."
    )

    doc.add_heading("3. Project Objectives", level=1)
    doc.add_paragraph(
        "The primary academic and technical objectives of this project are:\n"
        "• Distributed Pipeline Implementation: Construct an end-to-end distributed ML pipeline using Apache Spark and PySpark MLlib in local cluster mode.\n"
        "• Data Leakage Prevention: Enforce a strict three-way partitioning methodology (Train, Validation, Test) where all imputation, encoding, and tuning parameters are learned strictly from training data.\n"
        "• Imbalanced Threshold Optimization: Systematically sweep candidate probability thresholds on validation predictions to maximize positive-class F1-score rather than blindly accepting the default 0.50 cutoff.\n"
        "• Rigorous Evaluation: Compute positive-class Precision, Recall, F1-score, ROC-AUC, and Confusion Matrix metrics on the untouched test partition without fabricating performance.\n"
        "• NOC Operational Dashboard: Build an interactive Streamlit and Plotly monitoring interface to visualize component risk scores, confusion matrices, and device failure distributions."
    )

    # -----------------------------------------------------------------------
    # 5. SCOPE & TECHNOLOGIES USED
    # -----------------------------------------------------------------------
    doc.add_heading("4. Scope of the Project", level=1)
    doc.add_paragraph(
        "The scope encompasses offline batch machine learning processing on a local standalone Apache Spark instance (`master('local[*]')`). "
        "The system processes 5,000 synthetic records capturing cross-sectional telemetry. Real-time streaming brokers (Kafka), "
        "distributed file systems (HDFS/Hadoop), and external distributed cluster managers (YARN/Kubernetes) are deliberately excluded "
        "to maintain architectural simplicity and educational explainability suitable for an undergraduate cluster computing project."
    )

    doc.add_heading("5. Technologies Used", level=1)
    tech_table = doc.add_table(rows=1, cols=3)
    tech_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    format_table_header(tech_table, ["Technology / Framework", "Version / Mode", "Role in Project Architecture"], [1.8, 1.4, 3.3])
    
    tech_rows = [
        ("Python", "3.9.6", "Core programming language for scripts, pipeline orchestration, and dashboard."),
        ("Apache Spark", "4.0.5", "Distributed cluster computing engine running in standalone local multi-threaded mode."),
        ("PySpark", "4.0.5", "Python API exposing Spark DataFrame transformations, actions, and SparkSession."),
        ("Spark MLlib", "4.0.5", "Distributed machine learning library providing Imputer, Indexers, Assembler, and LogisticRegression."),
        ("Logistic Regression", "MLlib (L2 reg=0.01)", "Supervised binary classification algorithm estimating continuous failure probabilities."),
        ("Streamlit", "1.50.0", "Web application framework powering the interactive Network Operations Center dashboard."),
        ("Plotly", "7.1.0", "Interactive data visualization library rendering confusion matrix heatmaps and grouped rate charts."),
        ("Pandas", "2.3.3", "Used strictly for dashboard data presentation and tabular rendering (excluded from ML pipeline)."),
    ]
    for row in tech_rows:
        r_cells = tech_table.add_row().cells
        for i, val in enumerate(row):
            r_cells[i].text = val
    style_table_rows(tech_table)
    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    # -----------------------------------------------------------------------
    # 6. SYSTEM ARCHITECTURE
    # -----------------------------------------------------------------------
    doc.add_heading("6. System Architecture & Workflow", level=1)
    doc.add_paragraph(
        "The project follows a linear, modular distributed data flow structured across six stages:\n"
        "1. Dataset Generation: `generate_dataset.py` creates `telecom_network_failures.csv` with physical telemetry, traffic capacity utilization, and controlled missing values.\n"
        "2. Distributed Ingestion: PySpark reads the CSV into a distributed DataFrame with automatic schema inference and empty-string null mapping.\n"
        "3. Three-Way Split: Data is partitioned into Train (65.84%), Validation (15.00%), and Test (19.16%) subsets.\n"
        "4. Spark ML Pipeline: Transformations are fitted on the training partition: median Imputer for numerical columns, mode imputation for categorical status, StringIndexer and OneHotEncoder for categoricals, and VectorAssembler.\n"
        "5. Threshold Tuning: Logistic Regression outputs are evaluated across thresholds [0.08 to 0.50] on the validation partition to select the F1-maximizing threshold (0.16).\n"
        "6. Final Evaluation & Dashboard: Test data is scored at both default (0.50) and optimal (0.16) thresholds, exporting metrics to JSON and predictions to CSV for the Streamlit dashboard."
    )

    add_code_block(doc, 
        "+-----------------------------------------------------------------------------------+\n"
        "|                             SYSTEM WORKFLOW DIAGRAM                               |\n"
        "+-----------------------------------------------------------------------------------+\n"
        "|  [1. Dataset Generation] -> telecom_network_failures.csv (5,000 rows, 12 cols)    |\n"
        "|                                     |                                             |\n"
        "|  [2. PySpark Data Ingestion] ------> Spark DataFrame (Schema Inference, nullValue) |\n"
        "|                                     |                                             |\n"
        "|  [3. Three-Way Split] -------------> Train (65.8%) | Validation (15%) | Test (19.2%)|\n"
        "|                                     |                                             |\n"
        "|  [4. Preprocessing Pipeline] ------> Imputer -> StringIndexer -> OneHot -> Assembler|\n"
        "|                                     |                                             |\n"
        "|  [5. Model Training] --------------> LogisticRegression.fit(train_df)            |\n"
        "|                                     |                                             |\n"
        "|  [6. Threshold Optimization] ------> Validation Grid Search -> Threshold = 0.16  |\n"
        "|                                     |                                             |\n"
        "|  [7. Test Evaluation] -------------> Dual-Threshold Metrics (Recall: 52.3%, F1:34%)|\n"
        "|                                     |                                             |\n"
        "|  [8. Web Dashboard] ---------------> Streamlit & Plotly NOC Interface (Port 8501) |\n"
        "+-----------------------------------------------------------------------------------+"
    )

    # -----------------------------------------------------------------------
    # 7. DATASET DESCRIPTION
    # -----------------------------------------------------------------------
    doc.add_heading("7. Dataset Description & Simulation Methodology", level=1)
    
    add_callout(doc, 
        "Academic Simulation Disclosure: Due to telecommunications carrier confidentiality agreements (NDAs) "
        "and physical network security laws, live production carrier telemetry is strictly proprietary. "
        "This project utilizes a synthetic dataset generated with physically sound parameters inspired by "
        "typical telecommunication engineering heuristics. Model performance validates the PySpark distributed "
        "architecture and machine learning concepts; it does not claim real-world carrier accuracy.",
        title="SIMULATED DATASET NOTICE"
    )

    doc.add_paragraph(
        "The dataset (`telecom_network_failures.csv`) consists of exactly 5,000 records and 12 columns. "
        "A fixed random seed (`seed=42`) ensures 100% deterministic reproducibility across multiple runs."
    )

    ds_table = doc.add_table(rows=1, cols=4)
    ds_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    format_table_header(ds_table, ["Column Name", "Type", "Domain / Realistic Range", "Description & Controlled Nulls"], [1.8, 1.0, 1.8, 2.0])
    
    ds_rows = [
        ("device_id", "String", "DEV-1001 to DEV-6000", "Unique equipment identifier. Never contains missing values."),
        ("device_type", "String", "Router, Switch, Base_Station, Optical_Transponder, Gateway", "Hardware classification within the network topology. 0% missing."),
        ("region", "String", "North, South, East, West, Central", "Geographical operational network zone. 0% missing."),
        ("network_traffic_mbps", "Double", "50.00 to 10,000.00 Mbps", "Throughput volume passing through node. 0% missing."),
        ("signal_strength_dbm", "Double", "-120.00 to -45.00 dBm", "Received signal strength (RSSI/RSRP). 2.08% missing (sensor timeout)."),
        ("packet_loss_pct", "Double", "0.00% to 15.00%", "Percentage of dropped packets. 2.14% missing (telemetry drop)."),
        ("latency_ms", "Double", "5.00 to 350.00 ms", "Round-trip transmission delay. 1.58% missing (ping timeout)."),
        ("device_status", "String", "Normal, Degraded, Critical", "Current instantaneous monitoring trap status. 1.56% missing."),
        ("device_temperature_c", "Double", "25.00 to 95.00 °C", "Internal chassis operating temperature. 2.04% missing (probe error)."),
        ("historical_faults_count", "Integer", "0 to 12 incidents", "Logged incidents in prior 6 months. 0% missing."),
        ("uptime_days", "Double", "1.0 to 730.0 days", "Continuous operational uptime without reboot. 0% missing."),
        ("failure_next_24h", "Integer", "0 (Healthy), 1 (Failure)", "Target Label: Component fails in next 24 hours. 0% missing."),
    ]
    for row in ds_rows:
        r_cells = ds_table.add_row().cells
        for i, val in enumerate(row):
            r_cells[i].text = val
    style_table_rows(ds_table)
    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    doc.add_paragraph(
        "Label Generation Methodology:\n"
        "To model a true 24-hour predictive horizon without fixed rule-based thresholds, a composite Network Operational Stress Score (R) was formulated:\n"
        "R = 2.2(norm_packet_loss) + 1.8(norm_temp) + 1.6(norm_latency) + 1.5(norm_weak_signal) + 1.4(traffic_utilization) + 1.2(norm_faults) + 0.3(norm_uptime) + ε\n\n"
        "Where each telemetry feature is normalized to [0, 1], capacity utilization is computed relative to rated line rates "
        "(e.g., Optical Transponder: 10,000 Mbps; Router: 8,000 Mbps; Base Station: 5,000 Mbps; Switch: 4,500 Mbps; Gateway: 3,500 Mbps), "
        "and ε ~ N(0, 0.45) injects stochastic noise simulating unmonitored hardware fatigue. "
        "The continuous probability is evaluated via logistic sigmoid: P(failure) = 1 / (1 + e^{-(R - 5.10)}), "
        "and the binary label is assigned via a Bernoulli trial, producing exactly 13.70% failures across the 5,000 records."
    )

    # -----------------------------------------------------------------------
    # 8. IMPLEMENTATION METHODOLOGY
    # -----------------------------------------------------------------------
    doc.add_heading("8. Implementation Methodology in PySpark", level=1)
    
    doc.add_paragraph(
        "8.1 Data Ingestion & Leakage Prevention:\n"
        "The CSV dataset was loaded into a Spark DataFrame using `nullValue=''` to ensure empty strings are treated as true nulls. "
        "The three-way split was performed immediately to prevent information leakage:"
    )
    add_code_block(doc,
        "# Three-way partition to prevent leakage and snooping\n"
        "train_val_df, test_df = df.randomSplit([0.8, 0.2], seed=42)\n"
        "train_df, val_df = train_val_df.randomSplit([0.8, 0.2], seed=42)\n\n"
        "# Training Mode computed strictly on train_df\n"
        "status_mode = train_df.filter(col('device_status').isNotNull()) \\\n"
        "                      .groupBy('device_status').count() \\\n"
        "                      .orderBy(col('count').desc()).first()['device_status']\n"
        "train_df = train_df.fillna({'device_status': status_mode})\n"
        "val_df   = val_df.fillna({'device_status': status_mode})\n"
        "test_df  = test_df.fillna({'device_status': status_mode})"
    )

    doc.add_paragraph(
        "8.2 Feature Engineering Pipeline Stages:\n"
        "• Numerical Imputation: Spark MLlib's `Imputer` computes median statistics on training rows for `signal_strength_dbm`, `packet_loss_pct`, `latency_ms`, and `device_temperature_c`.\n"
        "• Categorical Indexing: `StringIndexer` converts string categories into numerical indices.\n"
        "• One-Hot Encoding: `OneHotEncoder` transforms indices into sparse orthogonal binary vectors to prevent artificial numeric ordering.\n"
        "• Vector Assembly: `VectorAssembler` merges all 4 imputed telemetry columns, 3 raw numerical features (`network_traffic_mbps`, `historical_faults_count`, `uptime_days`), and 3 one-hot encoded vector columns into a single unified `features` vector column.\n"
        "• Classification: `LogisticRegression(featuresCol='features', labelCol='label', maxIter=100, regParam=0.01)` fits the model."
    )

    add_code_block(doc,
        "# Spark ML Pipeline Assembly\n"
        "pipeline = Pipeline(stages=[imputer] + string_indexers + [one_hot_encoder, vector_assembler, lr])\n"
        "pipeline_model = pipeline.fit(train_df)"
    )

    doc.add_paragraph(
        "8.3 Classification Threshold Optimization:\n"
        "Standard classification algorithms default to a 0.50 probability threshold. When the target class represents only ~13.7% of the data, "
        "this default cutoff demands >50% certainty before flagging an alert, resulting in severe false negatives. "
        "We performed a validation grid search over candidate thresholds [0.08 to 0.50] in steps of 0.01 on the validation partition (750 records). "
        "The threshold maximizing validation F1-score was selected at θ = 0.16 (Validation F1 = 31.61%, Recall = 50.52%). "
        "The held-out test partition remained strictly untouched during this search."
    )

    # -----------------------------------------------------------------------
    # 9. MODEL EVALUATION & RESULTS
    # -----------------------------------------------------------------------
    doc.add_heading("9. Model Evaluation & Comparative Analysis", level=1)
    
    doc.add_paragraph(
        "The fitted PySpark MLlib model was evaluated on the held-out test partition (958 records, containing 132 actual failure cases). "
        "The table below contrasts performance at the default threshold (0.50) versus the validation-selected optimal threshold (0.16):"
    )

    eval_table = doc.add_table(rows=1, cols=4)
    eval_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    format_table_header(eval_table, ["Evaluation Metric", "Default Threshold (0.50)", "Optimized Threshold (0.16)", "Operational Significance"], [1.8, 1.4, 1.5, 1.8])
    
    eval_rows = [
        ("Accuracy", "86.74%", "72.34%", "Default accuracy is inflated by majority healthy class."),
        ("Precision (Positive Class)", "85.71%", "25.46%", "1 in 4 alerts results in an actual component failure."),
        ("Recall (Positive Class)", "4.55%", "52.27%", "Failure detection jumped from 6 to 69 cases (11x boost)."),
        ("F1-Score (Positive Class)", "8.63%", "34.24%", "Harmonic mean improved nearly 4-fold."),
        ("ROC-AUC", "0.6932", "0.6932", "Identical (threshold-independent ranking power)."),
        ("Predicted Failures Count", "7", "271", "Proactively identifies 271 at-risk components."),
        ("True Positives (TP)", "6", "69", "Imminent failures successfully caught in advance."),
        ("False Positives (FP)", "1", "202", "Preventive inspections / false alarms."),
        ("False Negatives (FN)", "126", "63", "Undetected failures halved (from 126 down to 63)."),
        ("True Negatives (TN)", "825", "624", "Correctly identified healthy components."),
    ]
    for row in eval_rows:
        r_cells = eval_table.add_row().cells
        for i, val in enumerate(row):
            r_cells[i].text = val
    style_table_rows(eval_table)
    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    doc.add_paragraph(
        "Confusion Matrix Explanation:\n"
        "• At Default Threshold (0.50): The model missed 126 out of 132 failures (FN = 126), catching only 6 (Recall = 4.55%). In a telecom NOC, this model is practically useless because catastrophic outages occur unannounced.\n"
        "• At Optimized Threshold (0.16): The model catches 69 failures (Recall = 52.27%), reducing missed failures to 63. Although false alarms increased to 202, the operational cost of running an automated diagnostic ping or scheduling a preventive inspection is vastly lower than the cost of an unexpected network outage."
    )

    # -----------------------------------------------------------------------
    # 10. DASHBOARD IMPLEMENTATION & SCREENSHOTS
    # -----------------------------------------------------------------------
    doc.add_heading("10. Dashboard Implementation & Visualizations", level=1)
    doc.add_paragraph(
        "An interactive Network Operations Center (NOC) dashboard was developed using Streamlit and Plotly (`app.py`). "
        "The dashboard reads `outputs/predictions/test_predictions.csv` and `outputs/evaluation_results/metrics.json` directly, "
        "allowing network operators to explore component risk probabilities, filter by hardware type and region, and inspect failure distributions."
    )

    # Embed Screenshot 1: Overview & KPI Cards
    if os.path.exists("dashboard_kpi_overview.png"):
        doc.add_paragraph().paragraph_format.space_before = Pt(4)
        doc.add_picture("dashboard_kpi_overview.png", width=Inches(6.2))
        p_cap = doc.add_paragraph("Figure 1: Dashboard Section A – Overview KPI Cards & Academic Simulation Notice")
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.runs[0].font.size = Pt(8.5)
        p_cap.runs[0].font.italic = True
        doc.add_paragraph().paragraph_format.space_after = Pt(6)

    # Embed Screenshot 2: Table Explorer
    if os.path.exists("dashboard_risk_explorer.png"):
        doc.add_picture("dashboard_risk_explorer.png", width=Inches(6.2))
        p_cap = doc.add_paragraph("Figure 2: Dashboard Section B – Interactive Predicted Failures & Risk Explorer Table")
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.runs[0].font.size = Pt(8.5)
        p_cap.runs[0].font.italic = True
        doc.add_paragraph().paragraph_format.space_after = Pt(6)

    # Embed Screenshot 3: Confusion Matrix & Breakdown
    if os.path.exists("dashboard_confusion_matrix.png"):
        doc.add_picture("dashboard_confusion_matrix.png", width=Inches(6.2))
        p_cap = doc.add_paragraph("Figure 3: Dashboard Section C – Confusion Matrix Heatmap & Sample Volume Breakdown")
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.runs[0].font.size = Pt(8.5)
        p_cap.runs[0].font.italic = True
        doc.add_paragraph().paragraph_format.space_after = Pt(6)

    # Embed Screenshot 4: Failure Rate by Device Type
    if os.path.exists("dashboard_rates_by_device.png"):
        doc.add_picture("dashboard_rates_by_device.png", width=Inches(6.2))
        p_cap = doc.add_paragraph("Figure 4: Dashboard Section D – Normalized Actual vs. Predicted Failure Rate by Device Type")
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.runs[0].font.size = Pt(8.5)
        p_cap.runs[0].font.italic = True
        doc.add_paragraph().paragraph_format.space_after = Pt(6)

    # Embed Screenshot 5: Performance Metrics
    if os.path.exists("dashboard_performance_metrics.png"):
        doc.add_picture("dashboard_performance_metrics.png", width=Inches(6.2))
        p_cap = doc.add_paragraph("Figure 5: Dashboard Section E – Spark MLlib Model Performance Metrics & Threshold Analysis")
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.runs[0].font.size = Pt(8.5)
        p_cap.runs[0].font.italic = True
        doc.add_paragraph().paragraph_format.space_after = Pt(6)

    # -----------------------------------------------------------------------
    # 11. RESULTS, LIMITATIONS & CONCLUSION
    # -----------------------------------------------------------------------
    doc.add_heading("11. Results and Discussion", level=1)
    doc.add_paragraph(
        "The experimental results demonstrate that distributed data processing with PySpark MLlib can successfully "
        "learn multivariate statistical patterns from high-dimensional network telemetry. "
        "The model identified that components with elevated capacity utilization (>60%), high packet drop rates (>3.5%), "
        "and elevated operating temperatures (>55°C) exhibit significantly higher failure risk. "
        "Crucially, threshold optimization proved mandatory: shifting from θ = 0.50 to θ = 0.16 increased recall by 47.7 percentage points, "
        "turning an impractical model into an actionable preventive maintenance early-warning system."
    )

    doc.add_heading("12. Limitations", level=1)
    doc.add_paragraph(
        "When evaluating this project for academic purposes, the following limitations must be recognized:\n"
        "1. Synthetic Telemetry: Telemetry metrics were generated via physical simulation models rather than hardware taps on live commercial networks.\n"
        "2. Absence of External Force Majeure Events: In live carrier environments, outages frequently occur due to unmonitored external causes (physical fiber cuts, utility power blackouts, severe storms) that exhibit zero telemetry degradation prior to sudden failure.\n"
        "3. Static Snapshot Distribution: The dataset does not incorporate temporal concept drift, seasonal traffic spikes (holidays), or network topology reconfiguration over multi-year operational cycles.\n"
        "4. Prototype Infrastructure: Execution was validated on a local multi-core Spark standalone instance rather than a multi-node physical enterprise cluster."
    )

    doc.add_heading("13. Conclusion", level=1)
    doc.add_paragraph(
        "This project successfully designed, implemented, and validated a complete distributed machine learning pipeline for telecom network failure prediction. "
        "Using Apache Spark and PySpark MLlib, we demonstrated distributed data ingestion, median/mode missing-value imputation, "
        "categorical encoding, feature vector assembly, three-way partitioning without data leakage, and Logistic Regression classification. "
        "By optimizing the decision threshold to 0.16 on validation data, the system achieved a 52.27% failure detection rate and an F1-score of 34.24% on the test set. "
        "The Streamlit/Plotly dashboard provides an intuitive, interactive tool for network operators to prioritize preventive maintenance."
    )

    doc.add_heading("14. Future Scope", level=1)
    doc.add_paragraph(
        "Potential extensions for future work include:\n"
        "• Deployment on Physical Multi-Node Cluster: Benchmarking PySpark execution across an Apache Spark cluster managed by Kubernetes or YARN.\n"
        "• Streaming Telemetry Ingestion: Integrating Apache Spark Structured Streaming with simulated Kafka brokers for real-time sliding-window inference.\n"
        "• Survival Analysis & Remaining Useful Life (RUL): Formulating continuous survival models (e.g., Cox Proportional Hazards) to predict the exact time-to-failure in hours.\n"
        "• Ensemble Tree Classifiers: Comparing Logistic Regression with distributed tree ensembles such as Random Forest and Gradient-Boosted Trees (GBTClassifier)."
    )

    doc.add_heading("15. References", level=1)
    refs = [
        "Zaharia, M., et al. (2016). Apache Spark: A Unified Engine for Big Data Processing. Communications of the ACM, 59(11), 56-65.",
        "Meng, X., et al. (2016). MLlib: Machine Learning in Apache Spark. Journal of Machine Learning Research, 17(34), 1-7.",
        "Hastie, T., Tibshirani, R., & Friedman, J. (2009). The Elements of Statistical Learning: Data Mining, Inference, and Prediction. Springer.",
        "ITU-T Recommendation Y.1541 (2011). Network Performance Objectives for IP-Based Services. International Telecommunication Union.",
        "Chawla, N. V., et al. (2002). SMOTE: Synthetic Minority Over-sampling Technique. Journal of Artificial Intelligence Research, 16, 321-357.",
        "Provost, F., & Fawcett, T. (2013). Data Science for Business: What You Need to Know about Data Mining and Data-Analytic Thinking. O'Reilly Media.",
        "Streamlit Documentation (2024). Build and share data apps. Streamlit Inc. https://docs.streamlit.io/"
    ]
    for r in refs:
        p_ref = doc.add_paragraph(r)
        p_ref.paragraph_format.left_indent = Inches(0.4)
        p_ref.paragraph_format.first_line_indent = Inches(-0.4)
        p_ref.paragraph_format.space_after = Pt(4)

    doc.save(output_filename)
    print(f"DOCX report saved: {output_filename}")


# ===========================================================================
# 2. GENERATE PDF REPORT (via ReportLab)
# ===========================================================================
class NumberedCanvas(canvas.Canvas):
    """Adds running footer with page numbers to PDF."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            if self._pageNumber > 1:  # Suppress page number on title page
                self.setFont("Helvetica", 8)
                self.setFillColor(colors.HexColor("#64748B"))
                self.drawString(54, 36, "Predicting Telecom Network Failure Using Apache Spark & PySpark MLlib")
                page_str = f"Page {self._pageNumber} of {num_pages}"
                self.drawRightString(612 - 54, 36, page_str)
                self.setStrokeColor(colors.HexColor("#CBD5E1"))
                self.setLineWidth(0.5)
                self.line(54, 48, 612 - 54, 48)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)


def build_pdf_report(output_filename="PROJECT_REPORT.pdf"):
    print(f"Generating PDF report: {output_filename}...")
    doc = SimpleDocTemplate(
        output_filename,
        pagesize=letter,
        leftMargin=54, rightMargin=54,
        topMargin=54, bottomMargin=54
    )

    styles = getSampleStyleSheet()
    
    # Custom styles
    style_title = ParagraphStyle(
        'RepTitle', parent=styles['Heading1'],
        fontName='Helvetica-Bold', fontSize=22, leading=26,
        textColor=colors.HexColor(PRIMARY_HEX), alignment=1, spaceAfter=10
    )
    style_subtitle = ParagraphStyle(
        'RepSub', parent=styles['Normal'],
        fontName='Helvetica-Oblique', fontSize=12, leading=16,
        textColor=colors.HexColor("#475569"), alignment=1, spaceAfter=25
    )
    style_badge = ParagraphStyle(
        'RepBadge', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=10, leading=14,
        textColor=colors.HexColor(SECONDARY_HEX), alignment=1, spaceAfter=30
    )
    style_meta = ParagraphStyle(
        'RepMeta', parent=styles['Normal'],
        fontName='Helvetica', fontSize=10, leading=16,
        textColor=colors.HexColor(TEXT_DARK_HEX), alignment=1
    )
    style_h1 = ParagraphStyle(
        'RepH1', parent=styles['Heading1'],
        fontName='Helvetica-Bold', fontSize=14, leading=18,
        textColor=colors.HexColor(PRIMARY_HEX), spaceBefore=14, spaceAfter=6,
        keepWithNext=True
    )
    style_h2 = ParagraphStyle(
        'RepH2', parent=styles['Heading2'],
        fontName='Helvetica-Bold', fontSize=11, leading=15,
        textColor=colors.HexColor(SECONDARY_HEX), spaceBefore=10, spaceAfter=4,
        keepWithNext=True
    )
    style_body = ParagraphStyle(
        'RepBody', parent=styles['Normal'],
        fontName='Helvetica', fontSize=9, leading=13,
        textColor=colors.HexColor(TEXT_DARK_HEX), spaceAfter=6
    )
    style_code = ParagraphStyle(
        'RepCode', parent=styles['Normal'],
        fontName='Courier', fontSize=7.5, leading=10,
        textColor=colors.HexColor("#0F172A"), backColor=colors.HexColor("#F8FAFC"),
        borderPadding=6, spaceBefore=4, spaceAfter=6
    )
    style_callout = ParagraphStyle(
        'RepCallout', parent=styles['Normal'],
        fontName='Helvetica', fontSize=8.5, leading=12,
        textColor=colors.HexColor("#0C4A6E"), backColor=colors.HexColor("#F0F9FF"),
        borderPadding=8, spaceBefore=6, spaceAfter=8
    )
    style_caption = ParagraphStyle(
        'RepCaption', parent=styles['Normal'],
        fontName='Helvetica-Oblique', fontSize=8, leading=11,
        textColor=colors.HexColor("#64748B"), alignment=1, spaceAfter=8
    )

    story = []

    # 1. TITLE PAGE
    story.append(Spacer(1, 40))
    story.append(Paragraph("Predicting Telecom Network Failure Using Apache Spark and PySpark MLlib", style_title))
    story.append(Paragraph("A Scalable Machine Learning Pipeline with Decision Threshold Optimization and Interactive NOC Dashboard", style_subtitle))
    story.append(Paragraph("ACADEMIC PROJECT REPORT", style_badge))
    story.append(Spacer(1, 40))

    meta_text = (
        "<b>Subject:</b> Cluster Computing (CS-401)<br/>"
        "<b>Student Name:</b> [Student Name]<br/>"
        "<b>Roll Number:</b> [Roll Number / Student ID]<br/>"
        "<b>Department:</b> [Department of Computer Science & Engineering]<br/>"
        "<b>Institution:</b> [University / Institute Name]<br/>"
        "<b>Academic Year:</b> 2026 – 2027"
    )
    story.append(Paragraph(meta_text, style_meta))
    story.append(PageBreak())

    # 2. ABSTRACT
    story.append(Paragraph("Abstract", style_h1))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor(SECONDARY_HEX), spaceAfter=8))
    abstract_text = (
        "Modern telecommunications infrastructure requires high reliability to maintain stringent Service Level Agreements "
        "(SLAs) and avert costly network disruptions. Traditional maintenance strategies rely heavily on reactive troubleshooting "
        "after component failure occurs, resulting in severe downtime. This project implements a distributed proactive failure-prediction "
        "pipeline using Apache Spark and PySpark MLlib in local standalone mode. A standardized 5,000-record network monitoring dataset "
        "featuring 12 operational and environmental columns was synthesized using domain telemetry heuristics (packet loss, latency, "
        "signal strength, operating temperature, and rated line-rate capacity utilization).<br/><br/>"
        "To prevent data leakage, a three-way split was implemented: Training (65.84%), Validation (15.00%), and Testing (19.16%). "
        "Distributed preprocessing incorporated median numerical imputation via Spark ML Imputer, training-mode categorical imputation, "
        "StringIndexer, OneHotEncoder, and VectorAssembler into an integrated Spark ML Pipeline. Because hardware failure is naturally "
        "infrequent (~13.78%), the standard 0.50 decision threshold was overly conservative, yielding only 4.55% recall. Decision threshold "
        "optimization conducted strictly on the validation set identified an optimal threshold of 0.16 (maximizing validation F1 at 31.61%). "
        "Evaluated on the held-out test partition (958 records), the optimized model achieved 52.27% recall (catching 69 of 132 impending failures), "
        "a precision of 25.46%, an F1-score of 34.24%, and an area under the ROC curve (ROC-AUC) of 0.6932. Finally, an interactive Network "
        "Operations Center (NOC) dashboard was developed using Streamlit and Plotly to enable risk exploration and regional filtering. "
        "All telemetry and outcomes are simulated for academic cluster computing demonstration."
    )
    story.append(Paragraph(abstract_text, style_body))
    story.append(Spacer(1, 10))

    # 3. INTRODUCTION & OBJECTIVES
    story.append(Paragraph("1. Introduction & Background", style_h1))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor(SECONDARY_HEX), spaceAfter=8))
    intro_p = (
        "Telecommunications carrier networks consist of thousands of geographically dispersed, interconnected active devices—including "
        "core routers, aggregation switches, cellular base stations, optical transponders, and customer gateways. These nodes continuously "
        "transmit massive volumes of voice, data, and multimedia traffic under changing physical and environmental conditions.<br/><br/>"
        "Predictive Maintenance represents an operational paradigm shift: by continuously monitoring hardware telemetry (transmission delay, "
        "packet drops, radio signal degradation, chassis thermal load, and bandwidth utilization), machine learning models can detect "
        "subtle pre-failure degradation signatures and flag at-risk equipment hours or days in advance."
    )
    story.append(Paragraph(intro_p, style_body))

    story.append(Paragraph("2. Problem Statement & Objectives", style_h1))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor(SECONDARY_HEX), spaceAfter=8))
    prob_p = (
        "<b>Problem Statement:</b> Given continuous operational telemetry, formulate a distributed binary classification pipeline to predict "
        "whether a network component will experience an outage within 24 hours (failure_next_24h = 1 vs. 0). The problem involves severe class "
        "imbalance (~13.7% failure rate), missing telemetry values, and the need for scalable distributed processing.<br/><br/>"
        "<b>Core Objectives:</b><br/>"
        "• Implement an end-to-end distributed ML pipeline using Apache Spark and PySpark MLlib in standalone local mode.<br/>"
        "• Enforce strict three-way partitioning (Train, Validation, Test) to eliminate data leakage and optimistic snooping.<br/>"
        "• Optimize the classification decision threshold on validation data to maximize the F1-score on imbalanced telemetry.<br/>"
        "• Evaluate test metrics honestly without fabricating scores or claiming unrealistic perfection.<br/>"
        "• Deploy an interactive Streamlit and Plotly Network Operations Center (NOC) dashboard for operational monitoring."
    )
    story.append(Paragraph(prob_p, style_body))

    # 4. TECHNOLOGIES & ARCHITECTURE
    story.append(Paragraph("3. Technologies Used & Architecture", style_h1))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor(SECONDARY_HEX), spaceAfter=8))
    
    t_data = [
        ["Technology", "Version", "Role in Architecture"],
        ["Apache Spark", "4.0.5", "Distributed cluster computing engine (local standalone multi-threaded mode)."],
        ["PySpark & MLlib", "4.0.5", "Python API exposing DataFrames, Imputer, Indexers, Assembler, and Logistic Regression."],
        ["Streamlit", "1.50.0", "Web application framework hosting the interactive NOC dashboard."],
        ["Plotly", "7.1.0", "Interactive charting library rendering confusion matrix heatmaps and grouped rate bars."],
        ["Pandas & NumPy", "Standard", "Tabular presentation on dashboard (Pandas) and vector math array backing (NumPy)."],
    ]
    t_tab = Table(t_data, colWidths=[1.4 * inch, 1.0 * inch, 4.6 * inch])
    t_tab.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(PRIMARY_HEX)),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 8.5),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 5),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor("#F8FAFC"), colors.white]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor(BORDER_HEX)),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(t_tab)
    story.append(Spacer(1, 10))

    # 5. DATASET & METHODOLOGY
    story.append(Paragraph("4. Dataset Description & Simulation Heuristics", style_h1))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor(SECONDARY_HEX), spaceAfter=8))
    story.append(Paragraph(
        "<b>Notice:</b> Telemetry is generated via mathematical simulation models inspired by standard telecom networking parameters. "
        "The dataset (`telecom_network_failures.csv`) contains 5,000 records across 12 columns:", style_callout
    ))

    ds_data = [
        ["Column Name", "Type", "Domain / Range", "Controlled Nulls & Role"],
        ["device_id", "String", "DEV-1001 to DEV-6000", "0% missing. Primary hardware identifier."],
        ["device_type", "String", "Router, Switch, Base_Station, Optical, Gateway", "0% missing. Architecture node classification."],
        ["region", "String", "North, South, East, West, Central", "0% missing. Regional operational deployment zone."],
        ["network_traffic_mbps", "Double", "50.0 to 10,000.0 Mbps", "0% missing. Node throughput volume."],
        ["signal_strength_dbm", "Double", "-120.0 to -45.0 dBm", "2.08% missing (sensor timeout). RSSI/RSRP level."],
        ["packet_loss_pct", "Double", "0.0% to 15.0%", "2.14% missing (telemetry drop). Transmission loss."],
        ["latency_ms", "Double", "5.0 to 350.0 ms", "1.58% missing (ping timeout). Round-trip delay."],
        ["device_status", "String", "Normal, Degraded, Critical", "1.56% missing. Instantaneous monitoring trap state."],
        ["device_temperature_c", "Double", "25.0 to 95.0 °C", "2.04% missing (probe error). Chassis temperature."],
        ["historical_faults_count", "Integer", "0 to 12 incidents", "0% missing. Incident history in prior 6 months."],
        ["uptime_days", "Double", "1.0 to 730.0 days", "0% missing. Operational days without reboot."],
        ["failure_next_24h", "Integer", "0 (Healthy), 1 (Failure)", "0% missing. Target Label: failure in next 24 hours."],
    ]
    ds_tab = Table(ds_data, colWidths=[1.5 * inch, 0.7 * inch, 2.3 * inch, 2.5 * inch])
    ds_tab.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(PRIMARY_HEX)),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 8),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor("#F8FAFC"), colors.white]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor(BORDER_HEX)),
        ('FONTSIZE', (0, 1), (-1, -1), 7.5),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(ds_tab)
    story.append(Spacer(1, 10))

    # 6. IMPLEMENTATION & PIPELINE
    story.append(Paragraph("5. PySpark MLlib Pipeline Implementation", style_h1))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor(SECONDARY_HEX), spaceAfter=8))
    pipe_text = (
        "<b>Leakage Prevention & Pipeline Stages:</b><br/>"
        "• <b>Three-Way Partition:</b> Train (3,292 rows, 65.84%), Validation (750 rows, 15.00%), Test (958 rows, 19.16%).<br/>"
        "• <b>Categorical Imputation:</b> Missing entries in `device_status` were imputed using the training mode (`'Normal'`).<br/>"
        "• <b>Numerical Imputer:</b> Spark ML Imputer with median strategy fitted on training telemetry.<br/>"
        "• <b>Encoding & Assembly:</b> StringIndexer -> OneHotEncoder -> VectorAssembler combining all 10 feature representations into a single `features` vector.<br/>"
        "• <b>Logistic Regression:</b> Fitted on training data with L2 regularization (regParam=0.01)."
    )
    story.append(Paragraph(pipe_text, style_body))

    # 7. MODEL EVALUATION
    story.append(Paragraph("6. Model Evaluation & Threshold Tuning", style_h1))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor(SECONDARY_HEX), spaceAfter=8))
    story.append(Paragraph(
        "<b>Threshold Optimization:</b> Grid search over thresholds [0.08, 0.50] on validation predictions identified "
        "<b>θ = 0.16</b> as the F1-maximizing threshold (Validation F1 = 31.61%). "
        "The comparison below reports test set results (958 records, 132 actual failures):", style_body
    ))

    ev_data = [
        ["Metric", "Default (θ = 0.50)", "Optimized (θ = 0.16)", "Operational Insight"],
        ["Accuracy", "86.74%", "72.34%", "Default accuracy is inflated by majority healthy class (86%)."],
        ["Precision (Positive)", "85.71%", "25.46%", "1 in 4 alerts results in an outage (viable NOC ratio)."],
        ["Recall (Positive)", "4.55%", "52.27%", "Failure detection jumped from 6 to 69 cases (11x boost)."],
        ["F1-Score", "8.63%", "34.24%", "Harmonic mean improved nearly 4-fold."],
        ["ROC-AUC", "0.6932", "0.6932", "Identical (threshold-independent ranking capability)."],
        ["Predicted Failures", "7", "271", "Proactively identifies 271 at-risk components."],
        ["True Positives (TP)", "6", "69", "Imminent failures successfully caught in advance."],
        ["False Positives (FP)", "1", "202", "Preventive inspections / false alarms."],
        ["False Negatives (FN)", "126", "63", "Undetected failures halved (from 126 down to 63)."],
        ["True Negatives (TN)", "825", "624", "Correctly identified healthy components."],
    ]
    ev_tab = Table(ev_data, colWidths=[1.6 * inch, 1.2 * inch, 1.3 * inch, 2.9 * inch])
    ev_tab.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(PRIMARY_HEX)),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 8),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor("#F8FAFC"), colors.white]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor(BORDER_HEX)),
        ('FONTSIZE', (0, 1), (-1, -1), 7.5),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(ev_tab)
    story.append(Spacer(1, 10))

    # 8. DASHBOARD DEMONSTRATION & SCREENSHOTS
    story.append(PageBreak())
    story.append(Paragraph("7. Streamlit Dashboard Demonstration", style_h1))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor(SECONDARY_HEX), spaceAfter=8))
    story.append(Paragraph(
        "An interactive Network Operations Center (NOC) dashboard was developed with Streamlit and Plotly (`app.py`), "
        "running at `http://localhost:8501`. Actual captured dashboard views are presented below:", style_body
    ))

    img_captions = [
        ("dashboard_kpi_overview.png", "Figure 1: Section A – Overview KPI Cards & Simulation Notice", 2.2),
        ("dashboard_risk_explorer.png", "Figure 2: Section B – Predicted Failures & Risk Explorer Table", 2.2),
        ("dashboard_confusion_matrix.png", "Figure 3: Section C – Confusion Matrix Heatmap & Classification Breakdown", 2.0),
        ("dashboard_rates_by_device.png", "Figure 4: Section D – Normalized Actual vs. Predicted Failure Rate by Device Type", 2.0),
        ("dashboard_performance_metrics.png", "Figure 5: Section E – Spark MLlib Performance Cards & Threshold Comparison", 1.8),
    ]

    for img_file, cap, h_in in img_captions:
        if os.path.exists(img_file):
            story.append(KeepTogether([
                RLImage(img_file, width=6.5 * inch, height=h_in * inch),
                Paragraph(cap, style_caption)
            ]))
            story.append(Spacer(1, 4))

    # 9. LIMITATIONS, CONCLUSION & REFERENCES
    story.append(PageBreak())
    story.append(Paragraph("8. Limitations, Conclusion & References", style_h1))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor(SECONDARY_HEX), spaceAfter=8))
    
    lim_text = (
        "<b>Academic Disclosures & Limitations:</b><br/>"
        "1. <i>Synthetic Origin:</i> Telemetry is mathematically modeled rather than captured from physical commercial taps.<br/>"
        "2. <i>External Outages:</i> Real carrier failures often stem from external force majeure events (fiber cuts, grid blackouts) with no pre-failure degradation.<br/>"
        "3. <i>Stationarity:</i> Cross-sectional snapshot without multi-year concept drift or firmware upgrade anomalies.<br/><br/>"
        "<b>Conclusion:</b><br/>"
        "The project demonstrates that PySpark MLlib can successfully power a distributed predictive maintenance pipeline. "
        "By addressing class imbalance through validation threshold optimization (θ = 0.16), the model achieved 52.27% recall and a 34.24% F1-score, "
        "integrated cleanly with an interactive Streamlit NOC dashboard.<br/><br/>"
        "<b>Selected References:</b><br/>"
        "• Zaharia, M., et al. (2016). Apache Spark: A Unified Engine for Big Data Processing. <i>CACM</i>, 59(11).<br/>"
        "• Meng, X., et al. (2016). MLlib: Machine Learning in Apache Spark. <i>JMLR</i>, 17(34).<br/>"
        "• Hastie, T., Tibshirani, R., & Friedman, J. (2009). <i>The Elements of Statistical Learning</i>. Springer.<br/>"
        "• Chawla, N. V., et al. (2002). SMOTE: Synthetic Minority Over-sampling Technique. <i>JAIR</i>, 16."
    )
    story.append(Paragraph(lim_text, style_body))

    # Build document
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"PDF report saved: {output_filename}")


if __name__ == "__main__":
    build_docx_report("PROJECT_REPORT.docx")
    build_pdf_report("PROJECT_REPORT.pdf")
