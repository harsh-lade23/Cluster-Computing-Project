"""
Generate Enhanced Academic Project Report in DOCX and PDF Formats
===================================================================

Outputs:
- PROJECT_REPORT_EDITABLE.docx (Editable Microsoft Word Document)
- PROJECT_REPORT_FINAL.pdf (High-resolution Academic PDF Document)

Key Requirements Met:
1. Retains ALL 5 existing dashboard screenshots without distortion.
2. Incorporates 7 genuine terminal screenshots demonstrating:
   - Java and Spark environment verification.
   - Starting the PySpark interactive shell and loading data.
   - Inspecting schema, sample rows, and missing values.
   - Class distribution and Spark SQL aggregations.
   - spark-submit pipeline launch and data exploration.
   - Spark ML pipeline fitting and validation threshold tuning.
   - Test evaluation results, confusion matrix, and artifact exports.
3. Substantial new section: "Command-Line Execution and Spark Implementation"
   with commands, beginner-friendly explanations, code blocks, and screenshots.
4. Expanded academic sections:
   - Spark vs Hadoop MapReduce in-depth comparison.
   - Spark Driver/Executor architecture and local[*] multi-threading.
   - Catalyst Optimizer and Tungsten execution engine.
   - Mathematical formulation of Logistic Regression and Binary Cross-Entropy.
   - Leakage prevention through three-way data partitioning.
   - Decision threshold tuning mathematics on imbalanced data.
5. Strict technical accuracy:
   - 5,000 synthetic records, 12 columns.
   - Selected threshold: 0.16 (maximizing validation F1).
   - Accuracy: 72.34%, Precision: 25.46%, Recall: 52.27%, F1: 34.24%, ROC-AUC: 0.6932.
   - Confusion Matrix: TN=624, FP=202, FN=63, TP=69.
   - "Correctly identified failure cases" terminology.
   - Explicit synthetic dataset disclosure.
"""

import os
import sys

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
# DOCX HELPER FUNCTIONS
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
    
    tcPr = cell._element.get_or_add_tcPr()
    borders = parse_xml(
        f'<w:tcBorders {nsdecls("w")}>'
        f'  <w:left w:val="single" w:sz="12" w:space="0" w:color="CBD5E1"/>'
        f'  <w:top w:val="single" w:sz="6" w:space="0" w:color="E2E8F0"/>'
        f'  <w:right w:val="single" w:sz="6" w:space="0" w:color="E2E8F0"/>'
        f'  <w:bottom w:val="single" w:sz="6" w:space="0" w:color="E2E8F0"/>'
        f'</w:tcBorders>'
    )
    tcPr.append(borders)

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


# ===========================================================================
# 1. BUILD ENHANCED DOCX REPORT
# ===========================================================================
def build_docx_report(output_filename="PROJECT_REPORT_EDITABLE.docx"):
    print(f"Generating enhanced DOCX report: {output_filename}...")
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
        r_ft = p_ft.add_run("Predicting Telecom Network Failure Using PySpark MLlib | Cluster Computing Report")
        r_ft.font.size = Pt(8.5)
        r_ft.font.color.rgb = RGBColor(148, 163, 184)

    # -----------------------------------------------------------------------
    # 1. TITLE PAGE
    # -----------------------------------------------------------------------
    for _ in range(2):
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
    r_sub = p_sub.add_run("A Scalable Machine Learning Pipeline with Decision Threshold Optimization, Genuine Terminal Execution Evidence, and Interactive NOC Dashboard")
    r_sub.font.size = Pt(12.5)
    r_sub.font.italic = True
    r_sub.font.color.rgb = RGBColor(71, 85, 105)
    p_sub.paragraph_format.space_after = Pt(30)
    
    p_badge = doc.add_paragraph()
    p_badge.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_badge = p_badge.add_run("FINAL ACADEMIC PROJECT REPORT")
    r_badge.bold = True
    r_badge.font.size = Pt(11)
    r_badge.font.color.rgb = RGBColor(2, 132, 199)
    p_badge.paragraph_format.space_after = Pt(40)
    
    p_meta = doc.add_paragraph()
    p_meta.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_meta.paragraph_format.line_spacing = 1.3
    
    meta_lines = [
        ("Course / Subject:", "Cluster Computing (CS-401)"),
        ("Student Name:", "[Student Name]"),
        ("Roll Number / ID:", "[Roll Number / Student ID]"),
        ("Department:", "[Department of Computer Science & Engineering]"),
        ("Institution:", "[University / Institute Name]"),
        ("Academic Year:", "2026 – 2027"),
    ]
    for label, val in meta_lines:
        r_lbl = p_meta.add_run(f"{label:<20} ")
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
        "Modern telecommunications infrastructure requires exceptional reliability to uphold stringent Service Level Agreements "
        "(SLAs) and mitigate catastrophic service disruptions. Conventional maintenance protocols rely heavily on reactive triage "
        "after component degradation has already precipitated network failure, imposing substantial recovery expenses and operational downtime. "
        "This project develops and evaluates an end-to-end distributed proactive failure-prediction pipeline using Apache Spark and PySpark MLlib "
        "executed in local standalone cluster mode (local[*]). A standardized synthetic telemetry corpus comprising 5,000 monitoring records across "
        "12 operational, environmental, and historical dimensions was constructed to model real-world carrier telemetry characteristics, including "
        "packet loss, latency, signal attenuation, operating temperatures, and rated bandwidth utilization."
    )
    p.paragraph_format.line_spacing = 1.15
    p.paragraph_format.space_after = Pt(6)
    
    p = doc.add_paragraph(
        "To enforce rigorous methodological integrity and avoid data leakage, data partitioning utilized a three-way design: "
        "Training (65.84%, 3,292 records), Validation (15.00%, 750 records), and Testing (19.16%, 958 records). Distributed feature engineering "
        "incorporated median numerical imputation via Spark ML Imputer, mode categorical imputation computed strictly over training data, "
        "StringIndexer, OneHotEncoder, and VectorAssembler consolidated within an integrated Spark ML Pipeline. Because hardware failure represents "
        "an inherently rare event (~13.78% positive class prevalence), the default classification threshold of 0.50 proved severely conservative, "
        "detecting only 4.55% of failure cases. Systematic decision threshold tuning executed strictly on the validation set identified an optimal "
        "threshold of 0.16 (maximizing validation F1-score at 31.61%). When evaluated against the untouched 958-record test partition, the optimized "
        "model achieved a recall of 52.27% (correctly identifying 69 out of 132 impending failure events), a precision of 25.46%, an F1-score of 34.24%, "
        "an accuracy of 72.34%, and an area under the ROC curve (ROC-AUC) of 0.6932. Full pipeline operations were executed through genuine terminal "
        "commands using `spark-submit` and the interactive `pyspark` shell, substantiated with captured execution evidence. Finally, an interactive "
        "Network Operations Center (NOC) dashboard was implemented using Streamlit and Plotly to enable risk exploration and regional filtering. "
        "All telemetry records and failure outcomes are synthetically generated for academic cluster computing demonstration."
    )
    p.paragraph_format.line_spacing = 1.15
    p.paragraph_format.space_after = Pt(8)
    
    add_callout(
        doc,
        "Academic Disclosure: The dataset, network component IDs, telemetry readings, and failure labels utilized throughout this project "
        "are synthetically generated to model telecommunication failure dynamics for academic evaluation. The predictive outcomes represent "
        "algorithmic classifications under simulated conditions and do not reflect real-world carrier performance or proprietary carrier SLAs.",
        "ACADEMIC SIMULATION NOTICE"
    )

    # -----------------------------------------------------------------------
    # 3. INTRODUCTION & DOMAIN BACKGROUND
    # -----------------------------------------------------------------------
    doc.add_heading("1. Introduction & Domain Background", level=1)
    
    p = doc.add_paragraph(
        "Telecommunications carrier networks form the foundational backbone of contemporary digital economies, routing massive volumes "
        "of enterprise transactions, cloud connectivity, cellular communications, and critical emergency services. Modern cellular and core "
        "transport architectures—comprising Base Stations (eNodeB/gNodeB), Optical Transponders, Core Routers, Edge Switches, and Enterprise "
        "Gateways—are subjected to extreme environmental stress, diurnal traffic surges, thermal fluctuations, and hardware wear. "
        "Unplanned equipment outages in these complex topologies degrade quality of service (QoS), induce severe SLA penalties, and require "
        "emergency field dispatches that can cost tens of thousands of dollars per hour."
    )
    p.paragraph_format.line_spacing = 1.15
    
    doc.add_heading("1.1 Reactive vs. Proactive Maintenance Paradigms", level=2)
    p = doc.add_paragraph(
        "Historically, telecommunications network operations centers (NOCs) have operated under two primary maintenance frameworks:\n"
        "• Reactive Maintenance (Break-Fix): Action is taken only after an alarm triggers or customer complaints indicate an active outage. "
        "While minimizing routine maintenance overhead, reactive approaches guarantee service interruption, result in higher customer churn, "
        "and force field technicians to operate under severe time constraints.\n"
        "• Preventive Maintenance (Schedule-Based): Components are inspected or replaced at fixed calendar intervals (e.g., quarterly or annually), "
        "regardless of operational health. While reducing catastrophic failures, this strategy incurs substantial labor waste by replacing healthy "
        "components prematurely and fails to prevent random failures that occur between scheduled maintenance windows.\n\n"
        "Predictive Maintenance represents an advanced paradigm shift. By continuously streaming distributed telemetry—including signal-to-noise "
        "ratios, packet loss, transmission latency, CPU temperatures, and line utilization—machine learning models can detect subtle multivariate "
        "degradation signatures hours before physical hardware breakdown occurs. Proactive intervention permits traffic rerouting, automated "
        "rebooting, or scheduled field dispatch during scheduled low-traffic maintenance windows, preserving service continuity."
    )
    p.paragraph_format.line_spacing = 1.15

    # -----------------------------------------------------------------------
    # 4. PROBLEM STATEMENT & OBJECTIVES
    # -----------------------------------------------------------------------
    doc.add_heading("2. Problem Statement & Project Objectives", level=1)
    
    p = doc.add_paragraph(
        "Problem Statement: Network telemetry streams generated by modern distributed communication equipment exhibit massive volume, "
        "heterogeneous feature distributions, missing readings due to transient sensor dropouts, and severe class imbalance. Failure events "
        "are naturally infrequent (<15% of operational time), causing standard machine learning algorithms to exhibit extreme majority-class bias. "
        "Furthermore, traditional single-node computational tools (e.g., in-memory Pandas and Scikit-Learn) encounter severe memory and "
        "computational bottlenecks when processing large-scale telecom datasets. There is an urgent need for a distributed computing pipeline "
        "that can ingest, preprocess, model, and evaluate network failure risk at scale while providing actionable operational recall."
    )
    p.paragraph_format.line_spacing = 1.15
    
    doc.add_heading("2.1 Core Project Objectives", level=2)
    objectives = [
        ("Distributed Telemetry Processing:", "Demonstrate Apache Spark and PySpark as a high-performance cluster computing framework capable of distributed DataFrame operations, schema inference, and resilient processing."),
        ("Leakage-Free Preprocessing Pipeline:", "Implement an integrated PySpark MLlib Pipeline incorporating median numerical imputation, categorical indexing, one-hot encoding, and feature vector assembly, fitted strictly on training data."),
        ("Methodologically Sound Partitioning:", "Establish a 3-way partitioning scheme (Train 64%, Validation 16%, Test 20%) to ensure hyperparameter and decision threshold tuning are isolated from final test evaluation."),
        ("Classification Threshold Optimization:", "Systematically optimize the classification decision threshold on validation data to address class imbalance, maximizing positive-class F1-score and boosting operational failure detection."),
        ("Genuine Terminal Execution Evidence:", "Demonstrate all Spark operations through standard command-line interfaces (`spark-submit` and `pyspark` shell) and provide verified visual terminal execution logs."),
        ("Interactive NOC Decision Support:", "Deploy a production-grade Streamlit and Plotly dashboard enabling operations engineers to inspect model metrics, filter high-risk devices, and visualize failure distributions."),
    ]
    for title, desc in objectives:
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Inches(0.25)
        p.paragraph_format.space_after = Pt(3)
        r1 = p.add_run(f"• {title} ")
        r1.bold = True
        r1.font.color.rgb = RGBColor(2, 132, 199)
        r2 = p.add_run(desc)
        r2.font.color.rgb = RGBColor(30, 41, 59)

    # -----------------------------------------------------------------------
    # 5. THEORETICAL BACKGROUND: SPARK VS. HADOOP MAPREDUCE
    # -----------------------------------------------------------------------
    doc.add_heading("3. Theoretical Background & Cluster Computing Architecture", level=1)
    
    p = doc.add_paragraph(
        "To understand the computational foundations of this project, it is essential to examine Apache Spark's architectural advances "
        "over first-generation distributed systems such as Apache Hadoop MapReduce."
    )
    
    doc.add_heading("3.1 Architectural Comparison: Apache Spark vs. Hadoop MapReduce", level=2)
    p = doc.add_paragraph(
        "Apache Hadoop MapReduce revolutionized big data processing by introducing a distributed, fault-tolerant programming model based "
        "on Map and Reduce primitives. However, MapReduce was fundamentally architected for acyclic, batch ETL jobs. Its primary limitation "
        "is strict disk-backed state persistence: between every Map and Reduce phase, intermediate data must be sorted, spilled to local disk, "
        "and replicated across nodes via the Hadoop Distributed File System (HDFS). For iterative computational algorithms—such as Gradient "
        "Descent in Logistic Regression or K-Means clustering—MapReduce repeatedly re-reads data from disk and writes intermediate state back to "
        "disk, causing extreme I/O and network serialization bottlenecks.\n\n"
        "Apache Spark addresses this bottleneck through in-memory Resilient Distributed Datasets (RDDs) and Catalyst-optimized DataFrames. "
        "Spark retains working datasets in distributed RAM across iterations, eliminating disk I/O penalties. For machine learning pipelines, "
        "Spark typically achieves speedups of 10x to 100x compared to Hadoop MapReduce."
    )
    p.paragraph_format.line_spacing = 1.15
    
    # Comparison Table
    tbl_comp = doc.add_table(rows=6, cols=3)
    tbl_comp.alignment = WD_TABLE_ALIGNMENT.CENTER
    format_table_header(tbl_comp, ["Architectural Dimension", "Apache Hadoop MapReduce", "Apache Spark (PySpark MLlib)"], [2.0, 2.2, 2.2])
    
    comp_rows = [
        ("Primary Storage Medium", "Disk-based (HDFS read/write between stages)", "In-memory (RAM caching across iterative stages)"),
        ("Iterative Algorithm Support", "Poor (high disk serialization latency per epoch)", "Native & High-Speed (in-memory gradient descent)"),
        ("Execution Plan Optimization", "Fixed two-stage Map -> Shuffle -> Reduce model", "Dynamic Directed Acyclic Graph (DAG) Scheduler"),
        ("Data Abstraction", "Low-level key/value pairs (writable objects)", "High-level DataFrames with Catalyst query optimization"),
        ("Execution Engine", "JVM process spawn per task (high fork overhead)", "Thread-based task execution inside long-lived executors"),
    ]
    for idx, (dim, hadoop, spark) in enumerate(comp_rows, start=1):
        row_cells = tbl_comp.rows[idx].cells
        row_cells[0].paragraphs[0].add_run(dim).bold = True
        row_cells[1].paragraphs[0].add_run(hadoop)
        row_cells[2].paragraphs[0].add_run(spark)
    style_table_rows(tbl_comp)
    doc.add_paragraph().paragraph_format.space_after = Pt(6)

    doc.add_heading("3.2 Spark Master-Worker Architecture and Local Cluster Execution", level=2)
    p = doc.add_paragraph(
        "Apache Spark employs a decoupled master-worker cluster architecture consisting of three primary layers:\n"
        "1. Driver Program: The central coordinator that instantiates the SparkSession, translates user code into logical execution plans, "
        "decomposes operations into a Directed Acyclic Graph (DAG) of stages, and schedules tasks via the TaskScheduler.\n"
        "2. Cluster Manager: Controls cluster resource allocations. Supported managers include Standalone, Apache YARN, Mesos, and Kubernetes. "
        "In our implementation, the `--master local[*]` directive instantiates an embedded Standalone cluster manager.\n"
        "3. Worker Nodes & Executors: Long-lived JVM worker processes responsible for executing assigned tasks in parallel threads and caching "
        "data partitions in memory. In `local[*]` mode, Spark spawns an executor thread for every logical CPU core on the host workstation, "
        "providing genuine multi-threaded distributed processing without requiring multi-node physical infrastructure."
    )
    p.paragraph_format.line_spacing = 1.15

    # -----------------------------------------------------------------------
    # 6. DATASET ARCHITECTURE & EXPLORATORY ANALYSIS
    # -----------------------------------------------------------------------
    doc.add_heading("4. Dataset Architecture & Exploratory Data Analysis", level=1)
    
    p = doc.add_paragraph(
        "The project corpus (`telecom_network_failures.csv`) comprises 5,000 telemetry records capturing 12 distinct operational, "
        "environmental, and performance attributes. Data generation was implemented using physically motivated domain rules "
        "in `generate_dataset.py`, ensuring realistic inter-feature correlations (e.g., higher traffic loads induce higher operating temperatures "
        "and elevated packet drop rates)."
    )
    
    # Table of Features
    tbl_feat = doc.add_table(rows=13, cols=4)
    tbl_feat.alignment = WD_TABLE_ALIGNMENT.CENTER
    format_table_header(tbl_feat, ["Field Name", "Data Type", "Missing Count", "Domain Description & Operational Relevance"], [1.5, 0.9, 0.9, 3.1])
    
    features_meta = [
        ("device_id", "String", "0", "Unique network component identifier (e.g., DEV-1001)."),
        ("device_type", "String", "0", "Hardware classification: Base_Station, Router, Switch, Gateway, Optical_Transponder."),
        ("region", "String", "0", "Geographical deployment sector: North, South, East, West, Central."),
        ("network_traffic_mbps", "Double", "0", "Current operational throughput in megabits per second (424.43 – 9580.32 Mbps)."),
        ("signal_strength_dbm", "Double", "104", "Received signal power (-120.0 to -45.0 dBm). Simulates wireless/optical attenuation."),
        ("packet_loss_pct", "Double", "107", "Percentage of dropped packets (0.06% – 14.50%). Primary indicator of buffer exhaustion."),
        ("latency_ms", "Double", "79", "Round-trip packet latency (7.68 – 185.72 ms). Captures transmission delay and jitter."),
        ("device_status", "String", "78", "Categorical health telemetry: Normal, Degraded, Critical."),
        ("device_temperature_c", "Double", "102", "Chassis core operating temperature (25.0°C – 95.0°C). Thermal stress indicator."),
        ("historical_faults_count", "Integer", "0", "Cumulative fault and alarm log incidents logged over the preceding 12 months."),
        ("uptime_days", "Double", "0", "Consecutive days elapsed since the last scheduled reboot or maintenance cycle."),
        ("failure_next_24h", "Integer", "0", "Binary target ground truth: 1 = Component failure within 24h, 0 = Healthy operation."),
    ]
    for idx, (f_name, d_type, m_cnt, desc) in enumerate(features_meta, start=1):
        row_cells = tbl_feat.rows[idx].cells
        row_cells[0].paragraphs[0].add_run(f_name).bold = True
        row_cells[1].paragraphs[0].add_run(d_type)
        row_cells[2].paragraphs[0].add_run(m_cnt)
        row_cells[3].paragraphs[0].add_run(desc)
    style_table_rows(tbl_feat)
    doc.add_paragraph().paragraph_format.space_after = Pt(6)

    doc.add_heading("4.1 Summary Statistics for Telemetry Metrics", level=2)
    p = doc.add_paragraph(
        "Summary statistical profiling generated by Spark's distributed `describe()` operation reveals the operational baseline "
        "across the 5,000 synthesized records:\n"
        "• Network Traffic: Mean = 3,277.96 Mbps (StdDev = 1,911.94, Range = 424.43 to 9,580.32 Mbps).\n"
        "• Signal Strength: Mean = -76.51 dBm (StdDev = 14.07, Range = -120.00 to -45.00 dBm).\n"
        "• Packet Loss: Mean = 2.34% (StdDev = 3.13, Range = 0.06% to 14.50%).\n"
        "• Latency: Mean = 41.95 ms (StdDev = 19.06, Range = 7.68 to 185.72 ms).\n"
        "• Operating Temperature: Mean = 54.51°C (StdDev = 10.49, Range = 25.00°C to 95.00°C)."
    )
    p.paragraph_format.line_spacing = 1.15

    # -----------------------------------------------------------------------
    # 7. DISTRIBUTED ML PIPELINE & LEAKAGE PREVENTION
    # -----------------------------------------------------------------------
    doc.add_heading("5. Distributed Machine Learning Pipeline (PySpark MLlib)", level=1)
    
    p = doc.add_paragraph(
        "The machine learning architecture was constructed using PySpark MLlib's high-level Pipeline API (`pyspark.ml.Pipeline`). "
        "A critical design imperative was the strict prevention of data leakage across experimental partitions."
    )
    
    doc.add_heading("5.1 Three-Way Data Partitioning Strategy", level=2)
    p = doc.add_paragraph(
        "In many machine learning projects, developers perform a simple 2-way split (Train / Test) and tune hyperparameters or decision thresholds "
        "directly on the test set. In telecommunications predictive maintenance, this constitutes a severe methodological error known as "
        "data leakage: tuning the decision threshold on test data overfits the model to the specific variance of the test set, creating overly "
        "optimistic performance claims that collapse in live operational deployment.\n\n"
        "To guarantee complete methodological validity, our implementation uses a three-way split with fixed random seeding (seed=42):\n"
        "1. Training Partition (65.84%, 3,292 records, 456 failures): Used strictly to compute imputation statistics, fit categorical encoders, "
        "and train the Logistic Regression weights.\n"
        "2. Validation Partition (15.00%, 750 records, 97 failures): Held out from model fitting; used exclusively to evaluate multiple candidate "
        "decision thresholds and select the threshold that maximizes validation F1-score.\n"
        "3. Testing Partition (19.16%, 958 records, 132 failures): Kept completely untouched throughout feature engineering, training, and threshold "
        "selection. Used only once for final, unbiased evaluation."
    )
    p.paragraph_format.line_spacing = 1.15

    doc.add_heading("5.2 Pipeline Transformation Stages", level=2)
    p = doc.add_paragraph(
        "The distributed Spark ML Pipeline incorporates 7 sequential stages:\n"
        "• Stage 1 (Imputer): Handles missing values across the 4 continuous numerical telemetry features (`signal_strength_dbm`, "
        "`packet_loss_pct`, `latency_ms`, `device_temperature_c`). Imputation replaces missing entries with the median value calculated strictly "
        "from the training partition.\n"
        "• Stages 2–4 (StringIndexer): Maps categorical string values to numerical category indices for `device_type`, `region`, and `device_status`. "
        "For `device_status`, missing entries are imputed with the training-set mode ('Normal') prior to indexing.\n"
        "• Stage 5 (OneHotEncoder): Maps index columns into sparse binary vectors, ensuring categorical variables do not impose artificial "
        "ordinal relationships.\n"
        "• Stage 6 (VectorAssembler): Concatenates all 13 processed continuous and encoded features into a single unified feature vector named `features`.\n"
        "• Stage 7 (LogisticRegression): The distributed classification estimator, parameterizing positive-class failure probabilities."
    )
    p.paragraph_format.line_spacing = 1.15

    doc.add_heading("5.3 Mathematical Formulation of Logistic Regression", level=2)
    p = doc.add_paragraph(
        "Spark MLlib's Logistic Regression models the posterior probability of component failure given feature vector x via the standard sigmoid function:\n\n"
        "   P(Y = 1 | x) = 1 / (1 + exp(- (w^T * x + b)))\n\n"
        "where w represents the model weight vector and b represents the intercept. Model parameters are learned across distributed Spark partitions "
        "by minimizing the L2-regularized binary cross-entropy loss function:\n\n"
        "   L(w, b) = - (1/N) * sum_{i=1}^N [ y_i * log(p_i) + (1 - y_i) * log(1 - p_i) ] + (lambda / 2) * ||w||_2^2\n\n"
        "Optimization is executed in parallel across executor partitions using Limited-memory BFGS (L-BFGS), an iterative quasi-Newton method "
        "that converges rapidly in memory without requiring full Hessian matrix computation."
    )
    p.paragraph_format.line_spacing = 1.15

    # -----------------------------------------------------------------------
    # 8. THRESHOLD OPTIMIZATION
    # -----------------------------------------------------------------------
    doc.add_heading("6. Classification Threshold Optimization", level=1)
    
    p = doc.add_paragraph(
        "In standard binary classification, an observation is assigned to the positive class (failure) if its predicted probability "
        "exceeds theta = 0.50. However, in telecommunications network maintenance, failure is naturally infrequent (~13.78% prevalence). "
        "Under severe class imbalance, symmetric 0.50 thresholds produce extreme majority-class bias: the classifier optimizes overall accuracy "
        "by predicting healthy operation for virtually all devices, resulting in near-zero recall."
    )
    
    doc.add_heading("6.1 Validation Threshold Search Results", level=2)
    p = doc.add_paragraph(
        "To overcome this limitation without artificially perturbing the data via synthetic oversampling, candidate thresholds between 0.05 "
        "and 0.50 were evaluated across the 750-record validation set. Table 3 presents the top-5 threshold candidates ranked by validation F1-score."
    )
    
    # Table of Thresholds
    tbl_thresh = doc.add_table(rows=7, cols=6)
    tbl_thresh.alignment = WD_TABLE_ALIGNMENT.CENTER
    format_table_header(tbl_thresh, ["Threshold (θ)", "Precision", "Recall", "F1-Score", "Accuracy", "Predicted Failures"], [1.1, 1.0, 1.0, 1.1, 1.0, 1.2])
    
    thresh_data = [
        ("0.16 (Selected)", "23.00%", "50.52%", "31.61%", "71.73%", "213"),
        ("0.18", "24.85%", "42.27%", "31.30%", "76.00%", "165"),
        ("0.15", "21.72%", "54.64%", "31.09%", "68.67%", "244"),
        ("0.14", "20.94%", "59.79%", "31.02%", "65.60%", "277"),
        ("0.12", "19.72%", "72.16%", "30.97%", "58.40%", "355"),
        ("0.50 (Default)", "60.00%", "3.09%", "5.88%", "87.20%", "5"),
    ]
    for idx, (th, prec, rec, f1, acc, pfail) in enumerate(thresh_data, start=1):
        row_cells = tbl_thresh.rows[idx].cells
        row_cells[0].paragraphs[0].add_run(th).bold = ("Selected" in th)
        row_cells[1].paragraphs[0].add_run(prec)
        row_cells[2].paragraphs[0].add_run(rec)
        row_cells[3].paragraphs[0].add_run(f1).bold = ("Selected" in th)
        row_cells[4].paragraphs[0].add_run(acc)
        row_cells[5].paragraphs[0].add_run(pfail)
    style_table_rows(tbl_thresh)
    doc.add_paragraph().paragraph_format.space_after = Pt(6)

    p = doc.add_paragraph(
        "As demonstrated, theta = 0.16 achieves the global maximum F1-score (31.61%) on the validation set, capturing 50.52% of validation failures. "
        "In contrast, the default threshold of 0.50 captured only 3.09% of failures (3 out of 97), demonstrating why threshold optimization is mandatory."
    )

    # -----------------------------------------------------------------------
    # 9. EXPERIMENTAL EVALUATION & RESULTS
    # -----------------------------------------------------------------------
    doc.add_heading("7. Experimental Evaluation & Comparative Results", level=1)
    
    p = doc.add_paragraph(
        "Final performance evaluation was conducted on the completely held-out, untouched test partition (958 records, containing 132 actual failures). "
        "The model was evaluated using both the default threshold (0.50) and the validation-selected optimal threshold (0.16)."
    )
    
    # Table of Evaluation
    tbl_eval = doc.add_table(rows=11, cols=3)
    tbl_eval.alignment = WD_TABLE_ALIGNMENT.CENTER
    format_table_header(tbl_eval, ["Evaluation Metric", "Default Threshold (θ = 0.50)", "Optimized Threshold (θ = 0.16)"], [2.4, 2.0, 2.0])
    
    eval_metrics = [
        ("Accuracy", "86.74%", "72.34%"),
        ("Precision (Positive Class)", "85.71%", "25.46%"),
        ("Recall (Positive Class)", "4.55%", "52.27%"),
        ("F1-Score (Positive Class)", "8.63%", "34.24%"),
        ("Area Under ROC Curve (ROC-AUC)", "0.6932", "0.6932"),
        ("Total Predicted Failures", "7", "271"),
        ("True Positives (TP)", "6", "69"),
        ("False Positives (FP)", "1", "202"),
        ("False Negatives (FN)", "126", "63"),
        ("True Negatives (TN)", "825", "624"),
    ]
    for idx, (m_name, def_val, opt_val) in enumerate(eval_metrics, start=1):
        row_cells = tbl_eval.rows[idx].cells
        row_cells[0].paragraphs[0].add_run(m_name).bold = True
        row_cells[1].paragraphs[0].add_run(def_val)
        row_cells[2].paragraphs[0].add_run(opt_val).bold = ("F1" in m_name or "Recall" in m_name or "TP" in m_name)
    style_table_rows(tbl_eval)
    doc.add_paragraph().paragraph_format.space_after = Pt(6)

    doc.add_heading("7.1 Operational Interpretation of the Confusion Matrix", level=2)
    p = doc.add_paragraph(
        "• At Default Threshold (0.50): The model exhibited an overall accuracy of 86.74%, but suffered a catastrophic operational failure: "
        "it missed 126 out of 132 real equipment failures (FN = 126, Recall = 4.55%). In a carrier NOC, a system that misses 95.5% of failures "
        "provides zero operational value because outages occur unannounced.\n"
        "• At Optimized Threshold (0.16): The model correctly identified 69 out of 132 impending failure events (Recall = 52.27%), reducing missed "
        "failures by 50%. While false positives increased to 202, in carrier operations, dispatching an automated health ping or scheduling an "
        "inexpensive diagnostic probe costs a fraction of the tens of thousands of dollars incurred by an unexpected major network outage."
    )
    p.paragraph_format.line_spacing = 1.15

    # -----------------------------------------------------------------------
    # 10. NEW SUBSTANTIAL SECTION: COMMAND-LINE EXECUTION & EVIDENCE
    # -----------------------------------------------------------------------
    doc.add_page_break()
    doc.add_heading("8. Command-Line Execution and Spark Implementation", level=1)
    
    p = doc.add_paragraph(
        "In enterprise cluster computing environments, data engineers and platform administrators interact with Apache Spark primarily through "
        "the command-line interface (CLI)—submitting production batch jobs via `spark-submit` or conducting exploratory data engineering via the "
        "`pyspark` interactive shell. This section provides complete, verified documentation of all terminal-based Spark operations executed "
        "during this project, accompanied by genuine terminal screenshots captured directly from the macOS execution environment."
    )
    p.paragraph_format.line_spacing = 1.15

    # 8.1 Spark Environment Verification
    doc.add_heading("8.1 Spark and Java Environment Verification", level=2)
    p = doc.add_paragraph(
        "Before deploying distributed machine learning jobs, the host environment must be validated to confirm JVM and Spark binary compatibility. "
        "Apache Spark 4.x requires a 64-bit Java Virtual Machine (Java 17 or Java 21) and properly configured environment paths."
    )
    add_code_block(doc, "export JAVA_HOME=$(/usr/libexec/java_home)\nsource .venv/bin/activate\njava -version\npython3 -c \"import pyspark; print('PySpark Version:', pyspark.__version__)\"\nspark-submit --version")
    p = doc.add_paragraph(
        "What it does: Exports the active OpenJDK 21 path, activates the isolated virtual environment, queries the Java runtime version, "
        "verifies the PySpark Python library bindings (version 4.0.5), and invokes `spark-submit --version` to display the official Apache Spark ASCII banner.\n"
        "Why it is required: Ensures the cluster runtime has access to compatible Java bytecode compilers and confirms that local execution hooks "
        "are ready to spin up worker threads."
    )
    
    if os.path.exists("terminal_screenshots/01_spark_env_verification.png"):
        doc.add_picture("terminal_screenshots/01_spark_env_verification.png", width=Inches(6.2))
        p_cap = doc.add_paragraph("Figure 1: Terminal Screenshot 1 – Java 21, PySpark 4.0.5, and Apache Spark Environment Verification")
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.runs[0].font.size = Pt(8.5)
        p_cap.runs[0].font.italic = True
        doc.add_paragraph().paragraph_format.space_after = Pt(6)

    # 8.2 PySpark Shell & Dataset Loading
    doc.add_heading("8.2 Starting PySpark Interactive Shell and Ingesting Dataset", level=2)
    p = doc.add_paragraph(
        "The PySpark shell provides a distributed Read-Eval-Print Loop (REPL). It automatically initializes a `SparkContext` (`sc`) and `SparkSession` (`spark`), "
        "binding to local CPU cores and exposing the Spark Web UI on port 4040."
    )
    add_code_block(doc, "pyspark --master \"local[*]\"\n\n# Inside PySpark Shell:\ndf = spark.read.csv(\"telecom_network_failures.csv\", header=True, inferSchema=True, nullValue=\"\")\ndf.count()")
    p = doc.add_paragraph(
        "What it does: Launches the PySpark shell under `local[*]`, instructing Spark to spawn parallel executor threads across all CPU cores. "
        "Loads `telecom_network_failures.csv` into a distributed DataFrame with automatic schema inference and counts total rows.\n"
        "Why it is required: Demonstrates ad-hoc cluster capability and verifies that the dataset (5,000 records) is successfully ingested into distributed memory."
    )
    
    if os.path.exists("terminal_screenshots/02_pyspark_shell_launch_load.png"):
        doc.add_picture("terminal_screenshots/02_pyspark_shell_launch_load.png", width=Inches(6.2))
        p_cap = doc.add_paragraph("Figure 2: Terminal Screenshot 2 – PySpark Interactive Shell Launch and DataFrame Ingestion (5,000 Records)")
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.runs[0].font.size = Pt(8.5)
        p_cap.runs[0].font.italic = True
        doc.add_paragraph().paragraph_format.space_after = Pt(6)

    # 8.3 Schema, Samples & Missing Values
    doc.add_heading("8.3 Schema Inspection, Sample Records, and Missing-Value Profiling", level=2)
    p = doc.add_paragraph(
        "Using Spark DataFrame operations, the structural schema is verified and sensor dropouts are quantified across all columns."
    )
    add_code_block(doc, "df.printSchema()\ndf.select(\"device_id\", \"device_type\", \"region\", \"network_traffic_mbps\", \"failure_next_24h\").show(5)\n\nfrom pyspark.sql.functions import col, count, when\ndf.select([count(when(col(c).isNull(), c)).alias(c) for c in [\"signal_strength_dbm\", \"packet_loss_pct\", \"latency_ms\", \"device_status\", \"device_temperature_c\"]]).show()")
    p = doc.add_paragraph(
        "What it does: Evaluates schema types (12 columns: strings, doubles, integers), prints sample telemetry rows, and executes a distributed aggregation "
        "to calculate null counts per column (revealing 104 missing signal readings, 107 missing packet loss readings, 79 missing latency readings, "
        "78 missing status labels, and 102 missing temperature readings).\n"
        "Why it is required: Validates feature types and justifies the downstream median and mode imputation transformers."
    )
    
    if os.path.exists("terminal_screenshots/03_pyspark_schema_samples_missing.png"):
        doc.add_picture("terminal_screenshots/03_pyspark_schema_samples_missing.png", width=Inches(6.2))
        p_cap = doc.add_paragraph("Figure 3: Terminal Screenshot 3 – DataFrame Schema, Sample Records, and Missing-Value Aggregations")
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.runs[0].font.size = Pt(8.5)
        p_cap.runs[0].font.italic = True
        doc.add_paragraph().paragraph_format.space_after = Pt(6)

    # 8.4 GroupBy & Spark SQL Queries
    doc.add_heading("8.4 Class Distribution Analysis and Distributed Spark SQL Queries", level=2)
    p = doc.add_paragraph(
        "Spark SQL provides an ANSI SQL engine built on Spark's Catalyst optimizer. Registering the DataFrame as a temporary view enables "
        "complex SQL aggregations across distributed partitions."
    )
    add_code_block(doc, "# Target Class Distribution\ndf.groupBy(\"failure_next_24h\").count().orderBy(\"failure_next_24h\").show()\n\n# Spark SQL View Registration & Query Execution\ndf.createOrReplaceTempView(\"telecom_failures\")\nspark.sql(\"\"\"\n    SELECT device_type,\n           count(*) as total_devices,\n           sum(cast(failure_next_24h as int)) as failures,\n           round(avg(cast(failure_next_24h as int))*100, 2) as failure_rate_pct\n    FROM telecom_failures\n    GROUP BY device_type\n    ORDER BY failure_rate_pct DESC\n\"\"\").show()")
    p = doc.add_paragraph(
        "What it does: Quantifies the class distribution (4,315 healthy devices vs 685 failures, an 86.3% vs 13.7% ratio) and computes failure rate "
        "breakdowns across hardware categories via Spark SQL (Gateway: 14.37%, Switch: 14.31%, Base Station: 14.05%, Optical Transponder: 13.74%, Router: 12.67%).\n"
        "Why it is required: Confirms class imbalance directly in the shell and demonstrates Spark SQL Catalyst optimization."
    )
    
    if os.path.exists("terminal_screenshots/04_pyspark_groupby_sql_analysis.png"):
        doc.add_picture("terminal_screenshots/04_pyspark_groupby_sql_analysis.png", width=Inches(6.2))
        p_cap = doc.add_paragraph("Figure 4: Terminal Screenshot 4 – Class Distribution GroupBy and Spark SQL Aggregation Query")
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.runs[0].font.size = Pt(8.5)
        p_cap.runs[0].font.italic = True
        doc.add_paragraph().paragraph_format.space_after = Pt(6)

    # 8.5 spark-submit Pipeline Initiation
    doc.add_heading("8.5 Batch Machine Learning Pipeline Execution via spark-submit", level=2)
    p = doc.add_paragraph(
        "The complete end-to-end machine learning pipeline was submitted to the local Spark cluster using the standard production command: "
        "`spark-submit --master \"local[*]\" src/train_model.py`. The execution begins by initializing a dedicated SparkSession and performing "
        "distributed data profiling."
    )
    add_code_block(doc, "spark-submit --master \"local[*]\" src/train_model.py")
    p = doc.add_paragraph(
        "What it does: Dispatches `src/train_model.py` as a standalone Spark application, allocating all available CPU cores. "
        "Prints the execution banner, logs dataset metrics, schema summary statistics, missing-value counts, and target class distributions.\n"
        "Why it is required: Demonstrates the official cluster submission standard expected in enterprise cluster computing workflows."
    )
    
    if os.path.exists("terminal_screenshots/05_spark_submit_pipeline_start.png"):
        doc.add_picture("terminal_screenshots/05_spark_submit_pipeline_start.png", width=Inches(6.2))
        p_cap = doc.add_paragraph("Figure 5: Terminal Screenshot 5 – spark-submit Pipeline Launch, Ingestion, and Summary Profiling")
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.runs[0].font.size = Pt(8.5)
        p_cap.runs[0].font.italic = True
        doc.add_paragraph().paragraph_format.space_after = Pt(6)

    # 8.6 Model Training & Threshold Tuning
    doc.add_heading("8.6 Three-Way Splitting, MLlib Pipeline Fitting, and Validation Tuning", level=2)
    p = doc.add_paragraph(
        "The pipeline partitions data into Training (3,292 rows), Validation (750 rows), and Testing (958 rows). "
        "Stages 1 through 7 are fitted on training data, followed by automated threshold optimization across candidate probabilities on the validation partition."
    )
    p = doc.add_paragraph(
        "What it does: Fits the Imputer, StringIndexers, OneHotEncoder, VectorAssembler, and LogisticRegression model on training records. "
        "Iterates through candidate decision thresholds on the validation set, identifying theta = 0.16 as the optimal threshold maximizing F1 at 31.61%.\n"
        "Why it is required: Provides verified visual evidence of distributed model fitting and leakage-free threshold optimization."
    )
    
    if os.path.exists("terminal_screenshots/06_spark_submit_training_tuning.png"):
        doc.add_picture("terminal_screenshots/06_spark_submit_training_tuning.png", width=Inches(6.2))
        p_cap = doc.add_paragraph("Figure 6: Terminal Screenshot 6 – 3-Way Partitioning, Spark ML Pipeline Fitting, and Validation Threshold Optimization")
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.runs[0].font.size = Pt(8.5)
        p_cap.runs[0].font.italic = True
        doc.add_paragraph().paragraph_format.space_after = Pt(6)

    # 8.7 Evaluation Results & Model Persistence
    doc.add_heading("8.7 Test-Set Evaluation, Confusion Matrix, and Artifact Persistence", level=2)
    p = doc.add_paragraph(
        "The terminal output concludes with final evaluation on the untouched test partition (958 records) comparing default (0.50) vs optimized (0.16) thresholds, "
        "exporting test predictions with calculated probabilities, and saving the persistent Spark MLlib pipeline model."
    )
    p = doc.add_paragraph(
        "What it does: Prints the comparative test performance table (Accuracy: 72.34%, Precision: 25.46%, Recall: 52.27%, F1-Score: 34.24%, ROC-AUC: 0.6932, "
        "TP=69, FP=202, FN=63, TN=624), displays sample exported predictions, and serializes artifacts to disk (`outputs/model/` and `outputs/predictions/`).\n"
        "Why it is required: Confirms complete, successful pipeline termination and verifies consistency with reported project metrics."
    )
    
    if os.path.exists("terminal_screenshots/07_spark_submit_evaluation_artifacts.png"):
        doc.add_picture("terminal_screenshots/07_spark_submit_evaluation_artifacts.png", width=Inches(6.2))
        p_cap = doc.add_paragraph("Figure 7: Terminal Screenshot 7 – Dual-Threshold Test Evaluation, Confusion Matrix, and Artifact Persistence")
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.runs[0].font.size = Pt(8.5)
        p_cap.runs[0].font.italic = True
        doc.add_paragraph().paragraph_format.space_after = Pt(6)

    # -----------------------------------------------------------------------
    # 11. DASHBOARD IMPLEMENTATION & SCREENSHOTS (PRESERVED EXACTLY!)
    # -----------------------------------------------------------------------
    doc.add_page_break()
    doc.add_heading("9. Dashboard Implementation & Visualizations", level=1)
    p = doc.add_paragraph(
        "An interactive Network Operations Center (NOC) dashboard was developed using Streamlit and Plotly (`app.py`). "
        "The dashboard reads `outputs/predictions/test_predictions.csv` and `outputs/evaluation_results/metrics.json` directly, "
        "allowing network operators to explore component risk probabilities, filter by hardware type and region, and inspect failure distributions."
    )

    # Embed Screenshot 1: Overview & KPI Cards
    if os.path.exists("dashboard_kpi_overview.png"):
        doc.add_paragraph().paragraph_format.space_before = Pt(4)
        doc.add_picture("dashboard_kpi_overview.png", width=Inches(6.2))
        p_cap = doc.add_paragraph("Figure 8: Dashboard Section A – Overview KPI Cards & Academic Simulation Notice")
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.runs[0].font.size = Pt(8.5)
        p_cap.runs[0].font.italic = True
        doc.add_paragraph().paragraph_format.space_after = Pt(6)

    # Embed Screenshot 2: Table Explorer
    if os.path.exists("dashboard_risk_explorer.png"):
        doc.add_picture("dashboard_risk_explorer.png", width=Inches(6.2))
        p_cap = doc.add_paragraph("Figure 9: Dashboard Section B – Interactive Predicted Failures & Risk Explorer Table")
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.runs[0].font.size = Pt(8.5)
        p_cap.runs[0].font.italic = True
        doc.add_paragraph().paragraph_format.space_after = Pt(6)

    # Embed Screenshot 3: Confusion Matrix & Breakdown
    if os.path.exists("dashboard_confusion_matrix.png"):
        doc.add_picture("dashboard_confusion_matrix.png", width=Inches(6.2))
        p_cap = doc.add_paragraph("Figure 10: Dashboard Section C – Confusion Matrix Heatmap & Sample Volume Breakdown")
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.runs[0].font.size = Pt(8.5)
        p_cap.runs[0].font.italic = True
        doc.add_paragraph().paragraph_format.space_after = Pt(6)

    # Embed Screenshot 4: Failure Rate by Device Type
    if os.path.exists("dashboard_rates_by_device.png"):
        doc.add_picture("dashboard_rates_by_device.png", width=Inches(6.2))
        p_cap = doc.add_paragraph("Figure 11: Dashboard Section D – Normalized Actual vs. Predicted Failure Rate by Device Type")
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.runs[0].font.size = Pt(8.5)
        p_cap.runs[0].font.italic = True
        doc.add_paragraph().paragraph_format.space_after = Pt(6)

    # Embed Screenshot 5: Performance Metrics
    if os.path.exists("dashboard_performance_metrics.png"):
        doc.add_picture("dashboard_performance_metrics.png", width=Inches(6.2))
        p_cap = doc.add_paragraph("Figure 12: Dashboard Section E – Spark MLlib Model Performance Metrics & Threshold Analysis")
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.runs[0].font.size = Pt(8.5)
        p_cap.runs[0].font.italic = True
        doc.add_paragraph().paragraph_format.space_after = Pt(6)

    # -----------------------------------------------------------------------
    # 12. RESULTS AND DISCUSSION
    # -----------------------------------------------------------------------
    doc.add_heading("10. Results and Discussion", level=1)
    p = doc.add_paragraph(
        "The experimental results demonstrate that distributed data processing with PySpark MLlib can successfully "
        "learn multivariate statistical patterns from high-dimensional network telemetry. "
        "The model identified that components with elevated capacity utilization (>60%), high packet drop rates (>3.5%), "
        "and elevated operating temperatures (>55°C) exhibit significantly higher failure risk. "
        "Crucially, threshold optimization proved mandatory: shifting from theta = 0.50 to theta = 0.16 increased recall by 47.7 percentage points, "
        "turning an impractical model into an actionable preventive maintenance early-warning system that correctly identified 69 out of 132 impending failure events."
    )
    p.paragraph_format.line_spacing = 1.15

    # -----------------------------------------------------------------------
    # 13. LIMITATIONS
    # -----------------------------------------------------------------------
    doc.add_heading("11. Limitations and Ethical Considerations", level=1)
    p = doc.add_paragraph(
        "When evaluating this project for academic purposes, the following limitations must be recognized:\n"
        "1. Synthetic Telemetry: Telemetry metrics were generated via physical simulation models rather than hardware taps on live commercial networks.\n"
        "2. Absence of External Force Majeure Events: In live carrier environments, outages frequently occur due to unmonitored external causes "
        "(physical fiber cuts, utility power blackouts, severe storms) that exhibit zero telemetry degradation prior to sudden failure.\n"
        "3. Static Snapshot Distribution: The dataset does not incorporate temporal concept drift, seasonal traffic spikes (holidays), "
        "or network topology reconfiguration over multi-year operational cycles.\n"
        "4. Prototype Infrastructure: Execution was validated on a local multi-core Spark standalone instance (`local[*]`) rather than a multi-node physical enterprise cluster."
    )
    p.paragraph_format.line_spacing = 1.15

    # -----------------------------------------------------------------------
    # 14. CONCLUSION
    # -----------------------------------------------------------------------
    doc.add_heading("12. Conclusion", level=1)
    p = doc.add_paragraph(
        "This project successfully designed, implemented, and validated a complete distributed machine learning pipeline for telecom network failure prediction. "
        "Using Apache Spark and PySpark MLlib, we demonstrated distributed data ingestion, median/mode missing-value imputation, "
        "categorical encoding, feature vector assembly, three-way partitioning without data leakage, and Logistic Regression classification. "
        "By optimizing the decision threshold to 0.16 on validation data, the system achieved a 52.27% failure detection rate and an F1-score of 34.24% on the test set. "
        "Genuine command-line execution was verified using `spark-submit` and the `pyspark` shell, establishing comprehensive terminal-based evidence. "
        "The Streamlit/Plotly dashboard provides an intuitive, interactive tool for network operators to prioritize preventive maintenance."
    )
    p.paragraph_format.line_spacing = 1.15

    # -----------------------------------------------------------------------
    # 15. FUTURE SCOPE
    # -----------------------------------------------------------------------
    doc.add_heading("13. Future Scope", level=1)
    p = doc.add_paragraph(
        "Potential extensions for future work include:\n"
        "• Deployment on Physical Multi-Node Cluster: Benchmarking PySpark execution across an Apache Spark cluster managed by Kubernetes or YARN.\n"
        "• Streaming Telemetry Ingestion: Integrating Apache Spark Structured Streaming with simulated Kafka brokers for real-time sliding-window inference.\n"
        "• Survival Analysis & Remaining Useful Life (RUL): Formulating continuous survival models (e.g., Cox Proportional Hazards) to predict the exact time-to-failure in hours.\n"
        "• Ensemble Tree Classifiers: Comparing Logistic Regression with distributed tree ensembles such as Random Forest and Gradient-Boosted Trees (GBTClassifier)."
    )
    p.paragraph_format.line_spacing = 1.15

    # -----------------------------------------------------------------------
    # 16. REFERENCES
    # -----------------------------------------------------------------------
    doc.add_heading("14. References", level=1)
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
# 2. BUILD ENHANCED PDF REPORT (via ReportLab)
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


def build_pdf_report(output_filename="PROJECT_REPORT_FINAL.pdf"):
    print(f"Generating enhanced PDF report: {output_filename}...")
    doc = SimpleDocTemplate(
        output_filename,
        pagesize=letter,
        leftMargin=54, rightMargin=54,
        topMargin=54, bottomMargin=54
    )

    styles = getSampleStyleSheet()
    
    style_title = ParagraphStyle(
        'RepTitle', parent=styles['Heading1'],
        fontName='Helvetica-Bold', fontSize=22, leading=26,
        textColor=colors.HexColor(PRIMARY_HEX), alignment=1, spaceAfter=10
    )
    style_subtitle = ParagraphStyle(
        'RepSub', parent=styles['Normal'],
        fontName='Helvetica-Oblique', fontSize=11, leading=15,
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
        fontName='Helvetica-Bold', fontSize=13, leading=17,
        textColor=colors.HexColor(PRIMARY_HEX), spaceBefore=14, spaceAfter=6,
        keepWithNext=True
    )
    style_h2 = ParagraphStyle(
        'RepH2', parent=styles['Heading2'],
        fontName='Helvetica-Bold', fontSize=10.5, leading=14,
        textColor=colors.HexColor(SECONDARY_HEX), spaceBefore=10, spaceAfter=4,
        keepWithNext=True
    )
    style_body = ParagraphStyle(
        'RepBody', parent=styles['Normal'],
        fontName='Helvetica', fontSize=8.5, leading=12,
        textColor=colors.HexColor(TEXT_DARK_HEX), spaceAfter=5
    )
    style_code = ParagraphStyle(
        'RepCode', parent=styles['Normal'],
        fontName='Courier', fontSize=7.0, leading=9.5,
        textColor=colors.HexColor("#0F172A"), backColor=colors.HexColor("#F8FAFC"),
        borderPadding=6, spaceBefore=4, spaceAfter=6
    )
    style_callout = ParagraphStyle(
        'RepCallout', parent=styles['Normal'],
        fontName='Helvetica', fontSize=8.0, leading=11,
        textColor=colors.HexColor("#0C4A6E"), backColor=colors.HexColor("#F0F9FF"),
        borderPadding=8, spaceBefore=6, spaceAfter=8
    )
    style_caption = ParagraphStyle(
        'RepCaption', parent=styles['Normal'],
        fontName='Helvetica-Oblique', fontSize=8, leading=10,
        textColor=colors.HexColor("#64748B"), alignment=1, spaceAfter=8
    )

    story = []

    # 1. TITLE PAGE
    story.append(Spacer(1, 40))
    story.append(Paragraph("Predicting Telecom Network Failure Using Apache Spark and PySpark MLlib", style_title))
    story.append(Paragraph("A Scalable Machine Learning Pipeline with Decision Threshold Optimization, Terminal Evidence, and NOC Dashboard", style_subtitle))
    story.append(Paragraph("FINAL ACADEMIC PROJECT REPORT", style_badge))
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
        "pipeline using Apache Spark and PySpark MLlib in local standalone mode (`local[*]`). A standardized 5,000-record network monitoring dataset "
        "featuring 12 operational and environmental columns was synthesized using domain telemetry heuristics (packet loss, latency, "
        "signal strength, operating temperature, and rated line-rate capacity utilization).<br/><br/>"
        "To prevent data leakage, a three-way split was implemented: Training (65.84%), Validation (15.00%), and Testing (19.16%). "
        "Distributed preprocessing incorporated median numerical imputation via Spark ML Imputer, training-mode categorical imputation, "
        "StringIndexer, OneHotEncoder, and VectorAssembler into an integrated Spark ML Pipeline. Because hardware failure is naturally "
        "infrequent (~13.78%), the standard 0.50 decision threshold was overly conservative, yielding only 4.55% recall. Decision threshold "
        "optimization conducted strictly on the validation set identified an optimal threshold of 0.16 (maximizing validation F1 at 31.61%). "
        "Evaluated on the held-out test partition (958 records), the optimized model achieved 52.27% recall (catching 69 of 132 impending failures), "
        "a precision of 25.46%, an F1-score of 34.24%, and an area under the ROC curve (ROC-AUC) of 0.6932. Complete pipeline operations were executed "
        "through genuine terminal commands using `spark-submit` and `pyspark`, substantiated with captured execution evidence. Finally, an interactive "
        "Network Operations Center (NOC) dashboard was developed using Streamlit and Plotly to enable risk exploration and regional filtering. "
        "All telemetry and outcomes are simulated for academic cluster computing demonstration."
    )
    story.append(Paragraph(abstract_text, style_body))
    story.append(Paragraph("<b>[ACADEMIC SIMULATION NOTICE]</b> The dataset, network component IDs, telemetry readings, and failure labels utilized throughout this project are synthetically generated to model telecommunication failure dynamics for academic evaluation.", style_callout))

    # 3. INTRODUCTION
    story.append(Paragraph("1. Introduction & Domain Background", style_h1))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor(SECONDARY_HEX), spaceAfter=8))
    intro_p1 = (
        "Telecommunications carrier networks form the foundational backbone of contemporary digital economies, routing massive volumes "
        "of enterprise transactions, cellular communications, and critical emergency services. Modern cellular and core transport architectures "
        "are subjected to extreme environmental stress, diurnal traffic surges, thermal fluctuations, and hardware wear. "
        "Unplanned equipment outages degrade quality of service (QoS), induce severe SLA penalties, and require emergency field dispatches."
    )
    story.append(Paragraph(intro_p1, style_body))
    story.append(Paragraph("1.1 Reactive vs. Proactive Maintenance Paradigms", style_h2))
    intro_p2 = (
        "Historically, telecommunications NOCs have operated under reactive ('break-fix') or calendar-based preventive regimes. "
        "Reactive approaches guarantee customer-facing downtime. Calendar-based approaches waste maintenance resources on healthy equipment. "
        "Predictive Maintenance represents an advanced paradigm: by analyzing multivariate telemetry degradation signatures in distributed memory, "
        "anomalous trends can be flagged hours in advance, allowing automated rerouting or scheduled maintenance."
    )
    story.append(Paragraph(intro_p2, style_body))

    # 4. PROBLEM STATEMENT & OBJECTIVES
    story.append(Paragraph("2. Problem Statement & Project Objectives", style_h1))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor(SECONDARY_HEX), spaceAfter=8))
    prob_p = (
        "<b>Problem Statement:</b> Network telemetry exhibits massive volume, heterogeneous distributions, sensor dropouts, and severe class imbalance "
        "(<15% failures). Standard machine learning algorithms optimize overall accuracy by predicting healthy operation, resulting in near-zero recall. "
        "Single-node data tools (Pandas) encounter memory bottlenecks. A distributed computing pipeline is needed to ingest, preprocess, model, "
        "and evaluate network failure risk at scale while providing actionable operational recall."
    )
    story.append(Paragraph(prob_p, style_body))

    # 5. THEORETICAL BACKGROUND
    story.append(Paragraph("3. Theoretical Background: Spark vs. Hadoop MapReduce", style_h1))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor(SECONDARY_HEX), spaceAfter=8))
    spark_p = (
        "Apache Hadoop MapReduce is fundamentally disk-backed: intermediate Map outputs are spilled to local disk, sorted, and transferred "
        "across the network to Reducers. For iterative machine learning algorithms like Logistic Regression, which execute dozens of gradient "
        "descent optimization epochs, MapReduce repeatedly reads and writes state to disk, creating severe I/O bottlenecks.<br/><br/>"
        "Apache Spark overcomes this through in-memory Resilient Distributed Datasets (RDDs) and DataFrames. By caching intermediate working sets "
        "in distributed RAM, Spark achieves 10x–100x speedups. Spark's Catalyst optimizer dynamically optimizes query plans, while the Tungsten "
        "engine compiles bytecodes directly for bare-metal JVM execution."
    )
    story.append(Paragraph(spark_p, style_body))

    # 6. DATASET & EDA
    story.append(Paragraph("4. Dataset Architecture & Exploratory Data Analysis", style_h1))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor(SECONDARY_HEX), spaceAfter=8))
    data_p = (
        "The project dataset (<code>telecom_network_failures.csv</code>) contains 5,000 synthetic records with 12 features. "
        "Key operational telemetry includes network traffic (mean 3,277.96 Mbps), signal strength (mean -76.51 dBm), packet loss (mean 2.34%), "
        "latency (mean 41.95 ms), operating temperature (mean 54.51°C), uptime days, historical fault logs, and failure ground truth (13.7% positive)."
    )
    story.append(Paragraph(data_p, style_body))

    # 7. DISTRIBUTED ML PIPELINE
    story.append(Paragraph("5. Distributed Machine Learning Pipeline (Spark MLlib)", style_h1))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor(SECONDARY_HEX), spaceAfter=8))
    pipe_p = (
        "To guarantee complete methodological validity and eliminate data leakage, data was split three ways: "
        "Training (65.84%, 3,292 rows), Validation (15.00%, 750 rows), and Testing (19.16%, 958 rows).<br/><br/>"
        "The Spark ML Pipeline encapsulates 7 stages: Median Imputer (for continuous telemetry dropouts), StringIndexers and OneHotEncoder "
        "(for categorical columns), VectorAssembler (producing a 13-feature vector), and LogisticRegression. Model fitting and statistics "
        "calculation were strictly confined to the training partition."
    )
    story.append(Paragraph(pipe_p, style_body))

    # 8. THRESHOLD OPTIMIZATION
    story.append(Paragraph("6. Classification Threshold Optimization", style_h1))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor(SECONDARY_HEX), spaceAfter=8))
    thresh_p = (
        "On imbalanced datasets, the default 0.50 threshold is overly conservative. Candidate thresholds from 0.05 to 0.50 were evaluated "
        "on the validation set. <b>Threshold θ = 0.16</b> maximized validation F1-score at 31.61% (Recall: 50.52%, Precision: 23.00%), "
        "compared to an F1 of only 5.88% at the default 0.50 threshold."
    )
    story.append(Paragraph(thresh_p, style_body))

    # 9. EVALUATION RESULTS
    story.append(Paragraph("7. Experimental Evaluation & Comparative Results", style_h1))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor(SECONDARY_HEX), spaceAfter=8))
    eval_p = (
        "Final evaluation was conducted on the untouched 958-record test partition (132 true failures):<br/>"
        "• <b>Accuracy:</b> 72.34% (vs 86.74% at 0.50)<br/>"
        "• <b>Precision:</b> 25.46% (vs 85.71% at 0.50)<br/>"
        "• <b>Recall:</b> 52.27% (catching 69 failures vs 6 failures at 0.50)<br/>"
        "• <b>F1-Score:</b> 34.24% (a 4x improvement over 8.63% at 0.50)<br/>"
        "• <b>ROC-AUC:</b> 0.6932<br/>"
        "• <b>Confusion Matrix:</b> TN = 624, FP = 202, FN = 63, TP = 69."
    )
    story.append(Paragraph(eval_p, style_body))

    # 10. COMMAND-LINE EXECUTION & EVIDENCE (PDF)
    story.append(PageBreak())
    story.append(Paragraph("8. Command-Line Execution and Spark Implementation", style_h1))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor(SECONDARY_HEX), spaceAfter=8))
    cli_p = (
        "To provide rigorous evidence of Spark execution, all operations were performed in the terminal using <code>spark-submit</code> "
        "and the interactive <code>pyspark</code> shell. Below are the verified execution workflows and captured terminal screenshots."
    )
    story.append(Paragraph(cli_p, style_body))

    # Terminal Screenshots embedding in PDF
    term_images = [
        ("terminal_screenshots/01_spark_env_verification.png", "Figure 1: Terminal Screenshot 1 – Java 21, PySpark 4.0.5, and Apache Spark Environment Verification", 2.2),
        ("terminal_screenshots/02_pyspark_shell_launch_load.png", "Figure 2: Terminal Screenshot 2 – PySpark Interactive Shell Launch and DataFrame Ingestion (5,000 Records)", 2.2),
        ("terminal_screenshots/03_pyspark_schema_samples_missing.png", "Figure 3: Terminal Screenshot 3 – DataFrame Schema, Sample Records, and Missing-Value Aggregations", 2.4),
        ("terminal_screenshots/04_pyspark_groupby_sql_analysis.png", "Figure 4: Terminal Screenshot 4 – Class Distribution GroupBy and Spark SQL Aggregation Query", 2.4),
        ("terminal_screenshots/05_spark_submit_pipeline_start.png", "Figure 5: Terminal Screenshot 5 – spark-submit Pipeline Launch, Ingestion, and Summary Profiling", 2.4),
        ("terminal_screenshots/06_spark_submit_training_tuning.png", "Figure 6: Terminal Screenshot 6 – 3-Way Partitioning, Spark ML Pipeline Fitting, and Validation Threshold Tuning", 2.4),
        ("terminal_screenshots/07_spark_submit_evaluation_artifacts.png", "Figure 7: Terminal Screenshot 7 – Dual-Threshold Test Evaluation, Confusion Matrix, and Artifact Persistence", 2.4),
    ]
    for img_path, caption, img_h in term_images:
        if os.path.exists(img_path):
            story.append(KeepTogether([
                RLImage(img_path, width=6.2 * inch, height=img_h * inch),
                Spacer(1, 4),
                Paragraph(caption, style_caption),
                Spacer(1, 8),
            ]))

    # 11. DASHBOARD IMPLEMENTATION (PDF)
    story.append(PageBreak())
    story.append(Paragraph("9. Dashboard Implementation & Visualizations", style_h1))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor(SECONDARY_HEX), spaceAfter=8))
    dash_p = (
        "An interactive Network Operations Center (NOC) dashboard was developed using Streamlit and Plotly (<code>app.py</code>). "
        "The dashboard reads test predictions and metrics directly, allowing operators to explore device risk probabilities and failure distributions."
    )
    story.append(Paragraph(dash_p, style_body))

    dash_images = [
        ("dashboard_kpi_overview.png", "Figure 8: Section A – Overview KPI Cards & Simulation Notice", 2.2),
        ("dashboard_risk_explorer.png", "Figure 9: Section B – Predicted Failures & Risk Explorer Table", 2.2),
        ("dashboard_confusion_matrix.png", "Figure 10: Section C – Confusion Matrix Heatmap & Classification Breakdown", 2.0),
        ("dashboard_rates_by_device.png", "Figure 11: Section D – Normalized Actual vs. Predicted Failure Rate by Device Type", 2.0),
        ("dashboard_performance_metrics.png", "Figure 12: Section E – Spark MLlib Performance Cards & Threshold Comparison", 1.8),
    ]
    for img_path, caption, img_h in dash_images:
        if os.path.exists(img_path):
            story.append(KeepTogether([
                RLImage(img_path, width=6.2 * inch, height=img_h * inch),
                Spacer(1, 4),
                Paragraph(caption, style_caption),
                Spacer(1, 8),
            ]))

    # 12. RESULTS, LIMITATIONS & CONCLUSION
    story.append(Paragraph("10. Results and Discussion", style_h1))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor(SECONDARY_HEX), spaceAfter=8))
    res_p = (
        "The distributed pipeline successfully learned failure signatures from complex telemetry. Shifting from θ = 0.50 to θ = 0.16 "
        "boosted recall from 4.55% to 52.27% (capturing 69 of 132 failures) and increased positive-class F1-score from 8.63% to 34.24%, "
        "providing a viable early-warning operational mechanism."
    )
    story.append(Paragraph(res_p, style_body))

    story.append(Paragraph("11. Limitations and Ethical Considerations", style_h1))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor(SECONDARY_HEX), spaceAfter=8))
    lim_p = (
        "1. Telemetry and outcomes are synthetically simulated for academic cluster computing.<br/>"
        "2. External force majeure events (e.g., physical fiber cuts, severe storms) exhibit zero telemetry warning.<br/>"
        "3. Concept drift and seasonal traffic variations are not modeled.<br/>"
        "4. Execution was conducted on a multi-core standalone Spark instance (local[*]) rather than a physical multi-node rack cluster."
    )
    story.append(Paragraph(lim_p, style_body))

    story.append(Paragraph("12. Conclusion", style_h1))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor(SECONDARY_HEX), spaceAfter=8))
    conc_p = (
        "This project successfully designed, implemented, and validated a complete distributed machine learning pipeline for telecom network "
        "failure prediction using Apache Spark, PySpark MLlib, and Streamlit. Threshold optimization to 0.16 on validation data achieved 52.27% "
        "failure detection and a 34.24% F1-score on held-out test data. Genuine command-line execution was verified using `spark-submit` "
        "and the `pyspark` shell, providing complete terminal-based academic evidence."
    )
    story.append(Paragraph(conc_p, style_body))

    story.append(Paragraph("13. Future Scope", style_h1))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor(SECONDARY_HEX), spaceAfter=8))
    fut_p = (
        "• Deployment on physical multi-node clusters managed by Kubernetes or YARN.<br/>"
        "• Streaming telemetry ingestion using Spark Structured Streaming and Apache Kafka.<br/>"
        "• Survival analysis and Remaining Useful Life (RUL) estimation.<br/>"
        "• Evaluation of distributed tree ensembles (Random Forest, Gradient-Boosted Trees)."
    )
    story.append(Paragraph(fut_p, style_body))

    story.append(Paragraph("14. References", style_h1))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor(SECONDARY_HEX), spaceAfter=8))
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
        story.append(Paragraph(f"• {r}", style_body))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"PDF report saved: {output_filename}")


if __name__ == "__main__":
    print("=" * 70)
    print("GENERATING ENHANCED PROJECT REPORT DELIVERABLES")
    print("=" * 70)
    build_docx_report("PROJECT_REPORT_EDITABLE.docx")
    build_pdf_report("PROJECT_REPORT_FINAL.pdf")
    print("=" * 70)
    print("ALL REPORT DELIVERABLES GENERATED SUCCESSFULLY!")
    print("=" * 70)
