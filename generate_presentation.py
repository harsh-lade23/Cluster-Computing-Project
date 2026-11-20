"""
Generate Project Presentation (PROJECT_PRESENTATION.pptx)
=========================================================
Creates a professional 12-slide academic presentation for:
'Predicting Telecom Network Failure Using Apache Spark and PySpark MLlib'

Using python-pptx with 16:9 widescreen layout, custom styling,
metric callout cards, and embedded dashboard screenshots.
"""

import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

# ---------------------------------------------------------------------------
# COLOR PALETTE
# ---------------------------------------------------------------------------
NAVY = RGBColor(15, 23, 42)       # #0F172A
SKY_BLUE = RGBColor(2, 132, 199)  # #0284C7
LIGHT_BLUE = RGBColor(224, 242, 254) # #E0F2FE
DARK_TEXT = RGBColor(30, 41, 59)  # #1E293B
MUTED_TEXT = RGBColor(100, 116, 139) # #64748B
WHITE = RGBColor(255, 255, 255)
CARD_BG = RGBColor(248, 250, 252) # #F8FAFC
CARD_BORDER = RGBColor(203, 213, 225) # #CBD5E1
RED_ALERT = RGBColor(220, 38, 38)
GREEN_OK = RGBColor(22, 163, 74)


def _add_run(paragraph, text):
    """Helper for python-pptx 1.0+ where add_run() takes no text arg."""
    run = paragraph.add_run()
    run.text = text
    return run


def create_presentation(output_filename="PROJECT_PRESENTATION.pptx"):
    print(f"Generating PPTX presentation: {output_filename}...")
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    def add_header(slide, title_text, category_text="CLUSTER COMPUTING ACADEMIC PROJECT"):
        """Adds a standardized academic slide banner."""
        # Top accent bar
        bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(0.12))
        bar.fill.solid()
        bar.fill.fore_color.rgb = SKY_BLUE
        bar.line.fill.background()

        # Category tracker
        cat_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.35), Inches(11.7), Inches(0.35))
        tf_cat = cat_box.text_frame
        tf_cat.word_wrap = True
        p_cat = tf_cat.paragraphs[0]
        p_cat.text = category_text.upper()
        p_cat.font.name = "Arial"
        p_cat.font.size = Pt(10)
        p_cat.font.bold = True
        p_cat.font.color.rgb = SKY_BLUE

        # Title
        title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.65), Inches(11.7), Inches(0.7))
        tf_title = title_box.text_frame
        tf_title.word_wrap = True
        p_title = tf_title.paragraphs[0]
        p_title.text = title_text
        p_title.font.name = "Arial"
        p_title.font.size = Pt(22)
        p_title.font.bold = True
        p_title.font.color.rgb = NAVY

    def add_card(slide, left, top, width, height, bg_color=CARD_BG, border_color=CARD_BORDER):
        """Adds a subtle container card."""
        shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        shape.fill.solid()
        shape.fill.fore_color.rgb = bg_color
        shape.line.color.rgb = border_color
        shape.line.width = Pt(1)
        return shape

    # =======================================================================
    # SLIDE 1: TITLE SLIDE
    # =======================================================================
    slide1 = prs.slides.add_slide(blank_layout)
    # Background card
    bg = slide1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(7.5))
    bg.fill.solid()
    bg.fill.fore_color.rgb = NAVY
    bg.line.fill.background()

    # Top line accent
    top_bar = slide1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(0.18))
    top_bar.fill.solid()
    top_bar.fill.fore_color.rgb = SKY_BLUE
    top_bar.line.fill.background()

    # Subject badge
    b_box = slide1.shapes.add_textbox(Inches(1.0), Inches(1.2), Inches(11.3), Inches(0.5))
    p_b = b_box.text_frame.paragraphs[0]
    p_b.text = "CLUSTER COMPUTING (CS-401) • CAPSTONE PROJECT"
    p_b.font.size = Pt(12)
    p_b.font.bold = True
    p_b.font.color.rgb = SKY_BLUE

    # Title
    t_box = slide1.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(11.3), Inches(1.8))
    tf_t = t_box.text_frame
    tf_t.word_wrap = True
    p_t = tf_t.paragraphs[0]
    p_t.text = "Predicting Telecom Network Failure\nUsing Apache Spark & PySpark MLlib"
    p_t.font.size = Pt(32)
    p_t.font.bold = True
    p_t.font.color.rgb = WHITE

    # Subtitle
    sub_box = slide1.shapes.add_textbox(Inches(1.0), Inches(3.8), Inches(11.3), Inches(0.8))
    tf_sub = sub_box.text_frame
    p_sub = tf_sub.paragraphs[0]
    p_sub.text = "A Scalable Distributed Machine Learning Pipeline with Decision Threshold Optimization & Interactive NOC Dashboard"
    p_sub.font.size = Pt(14)
    p_sub.font.italic = True
    p_sub.font.color.rgb = RGBColor(148, 163, 184)

    # Metadata card
    meta_card = add_card(slide1, Inches(1.0), Inches(4.8), Inches(11.333), Inches(1.8), bg_color=RGBColor(30, 41, 59), border_color=RGBColor(51, 65, 85))
    m_box = slide1.shapes.add_textbox(Inches(1.3), Inches(5.0), Inches(10.7), Inches(1.4))
    tf_m = m_box.text_frame
    tf_m.word_wrap = True

    p1 = tf_m.paragraphs[0]
    p1.text = "Author / Candidate: [Student Name]  |  Roll Number: [Roll Number / Student ID]"
    p1.font.size = Pt(13)
    p1.font.bold = True
    p1.font.color.rgb = WHITE

    p2 = tf_m.add_paragraph()
    p2.text = "Department: [Department of Computer Science & Engineering]"
    p2.font.size = Pt(12)
    p2.font.color.rgb = RGBColor(203, 213, 225)

    p3 = tf_m.add_paragraph()
    p3.text = "Institution: [University / Institute Name]  •  Academic Year: 2026 – 2027"
    p3.font.size = Pt(12)
    p3.font.color.rgb = RGBColor(203, 213, 225)

    # =======================================================================
    # SLIDE 2: INTRODUCTION & PROBLEM STATEMENT
    # =======================================================================
    slide2 = prs.slides.add_slide(blank_layout)
    add_header(slide2, "Introduction & Problem Statement")

    # Left Card: Operational Context
    add_card(slide2, Inches(0.8), Inches(1.6), Inches(5.6), Inches(5.2))
    tb_l = slide2.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(5.2), Inches(4.8))
    tf_l = tb_l.text_frame
    tf_l.word_wrap = True

    p = tf_l.paragraphs[0]
    p.text = "Operational Context in Telecom Networks"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = NAVY

    points_l = [
        ("Massive Infrastructure:", "Modern carriers deploy thousands of distributed routers, base stations, switches, and optical transponders."),
        ("Reactive Maintenance Bottleneck:", "Traditional operations wait for hardware alarms after outages occur, causing severe SLA penalties."),
        ("Predictive Paradigm Shift:", "Using continuous telemetry (packet loss, latency, temperature, throughput) to forecast failures 24 hours in advance."),
        ("Cluster Computing Necessity:", "Carrier telemetry generates high-volume streams requiring scalable distributed computing architectures.")
    ]
    for title, desc in points_l:
        p = tf_l.add_paragraph()
        p.space_before = Pt(10)
        r1 = _add_run(p, f"• {title} ")
        r1.bold = True
        r1.font.color.rgb = SKY_BLUE
        r1.font.size = Pt(12)
        r2 = _add_run(p, desc)
        r2.font.color.rgb = DARK_TEXT
        r2.font.size = Pt(12)

    # Right Card: The Core Challenge
    add_card(slide2, Inches(6.8), Inches(1.6), Inches(5.7), Inches(5.2))
    tb_r = slide2.shapes.add_textbox(Inches(7.0), Inches(1.8), Inches(5.3), Inches(4.8))
    tf_r = tb_r.text_frame
    tf_r.word_wrap = True

    p = tf_r.paragraphs[0]
    p.text = "Core Technical Challenges Addressed"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = NAVY

    points_r = [
        ("Severe Class Imbalance:", "Network component failures are rare events (~13.7% in our dataset). Standard classifiers default to predicting 'Healthy'."),
        ("Sensor Telemetry Gaps:", "Telemetry feeds suffer from intermittent probe timeouts and missing readings that crash matrix operations."),
        ("Overly Conservative Thresholds:", "Default 0.50 probability cutoffs miss >95% of real failures, rendering models useless in live operations."),
        ("Data Leakage Risks:", "Imputing statistics or tuning decision thresholds across combined data introduces optimistic evaluation bias.")
    ]
    for title, desc in points_r:
        p = tf_r.add_paragraph()
        p.space_before = Pt(10)
        r1 = _add_run(p, f"• {title} ")
        r1.bold = True
        r1.font.color.rgb = RED_ALERT
        r1.font.size = Pt(12)
        r2 = _add_run(p, desc)
        r2.font.color.rgb = DARK_TEXT
        r2.font.size = Pt(12)

    # =======================================================================
    # SLIDE 3: PROJECT OBJECTIVES & SCOPE
    # =======================================================================
    slide3 = prs.slides.add_slide(blank_layout)
    add_header(slide3, "Project Objectives & Technical Scope")

    cards_data = [
        ("1. Distributed PySpark Pipeline", "Build an end-to-end distributed ML pipeline using Apache Spark and PySpark MLlib in local cluster mode without external ML libraries.", SKY_BLUE),
        ("2. Leakage-Free 3-Way Partitioning", "Split data into Train (65.8%), Validation (15.0%), and Test (19.2%). Fit all imputation and encoding transformers strictly on training rows.", NAVY),
        ("3. Validation Threshold Optimization", "Sweep candidate probability cutoffs [0.08–0.50] on validation data to maximize F1-score rather than blindly accepting the default 0.50 threshold.", SKY_BLUE),
        ("4. Truthful Unbiased Evaluation", "Evaluate Precision, Recall, F1, and ROC-AUC on the held-out test partition without fabricating performance or cherry-picking metrics.", NAVY),
        ("5. Interactive Web NOC Dashboard", "Deploy a responsive Streamlit and Plotly operations dashboard enabling real-time risk filtering, confusion matrix inspection, and device rate analysis.", SKY_BLUE),
        ("6. Academic Transparency", "Explicitly disclose the synthetic nature of the dataset and clarify that outcomes validate cluster computing pipelines rather than live commercial carrier reliability.", NAVY),
    ]

    for i, (title, text, col_accent) in enumerate(cards_data):
        row = i // 3
        col = i % 3
        l = Inches(0.8 + col * 4.0)
        t = Inches(1.6 + row * 2.7)
        w = Inches(3.7)
        h = Inches(2.4)

        add_card(slide3, l, t, w, h)
        # Accent top bar on card
        top_c = slide3.shapes.add_shape(MSO_SHAPE.RECTANGLE, l, t, w, Inches(0.1))
        top_c.fill.solid()
        top_c.fill.fore_color.rgb = col_accent
        top_c.line.fill.background()

        tb = slide3.shapes.add_textbox(l + Inches(0.2), t + Inches(0.2), w - Inches(0.4), h - Inches(0.3))
        tf = tb.text_frame
        tf.word_wrap = True

        p1 = tf.paragraphs[0]
        p1.text = title
        p1.font.size = Pt(13)
        p1.font.bold = True
        p1.font.color.rgb = NAVY

        p2 = tf.add_paragraph()
        p2.space_before = Pt(6)
        p2.text = text
        p2.font.size = Pt(11)
        p2.font.color.rgb = DARK_TEXT

    # =======================================================================
    # SLIDE 4: TECHNOLOGY STACK & ARCHITECTURE
    # =======================================================================
    slide4 = prs.slides.add_slide(blank_layout)
    add_header(slide4, "Technology Stack & Architecture Flow")

    # Workflow diagram card
    add_card(slide4, Inches(0.8), Inches(1.6), Inches(11.7), Inches(5.2))
    tb_wf = slide4.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(11.3), Inches(4.8))
    tf_wf = tb_wf.text_frame
    tf_wf.word_wrap = True

    p = tf_wf.paragraphs[0]
    p.text = "Modular Distributed Architecture Pipeline"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = NAVY

    flow_stages = [
        ("Stage 1: Telemetry Simulation", "generate_dataset.py generates 5,000 records with 12 features, capacity utilization, and controlled missing values (seed=42)."),
        ("Stage 2: PySpark Distributed Ingestion", "Local SparkSession (master='local[*]') reads CSV into Spark DataFrame with schema inference and nullValue mapping."),
        ("Stage 3: 3-Way Leakage-Free Splitting", "Data partitioned into Train (65.84%), Validation (15.00%), and Test (19.16%). Test partition strictly isolated."),
        ("Stage 4: Spark MLlib Pipeline Fitting", "Fitted strictly on train data: Imputer (median) + StringIndexer + OneHotEncoder + VectorAssembler -> features vector."),
        ("Stage 5: Logistic Regression & Threshold Tuning", "LogisticRegression model trained on train_df; threshold swept across [0.08–0.50] on validation_df to select θ = 0.16."),
        ("Stage 6: Test Evaluation & Artifact Export", "Held-out test partition scored at θ = 0.16; predictions exported to CSV and metrics to JSON for dashboard rendering."),
        ("Stage 7: Streamlit & Plotly NOC Dashboard", "Interactive web application visualizes test predictions, confusion matrix heatmap, and failure rates by hardware type.")
    ]
    for num, desc in flow_stages:
        p = tf_wf.add_paragraph()
        p.space_before = Pt(6)
        r1 = _add_run(p, f"• {num}: ")
        r1.bold = True
        r1.font.color.rgb = SKY_BLUE
        r1.font.size = Pt(11.5)
        r2 = _add_run(p, desc)
        r2.font.color.rgb = DARK_TEXT
        r2.font.size = Pt(11.5)

    # =======================================================================
    # SLIDE 5: DATASET DESCRIPTION & SIMULATION METHODOLOGY
    # =======================================================================
    slide5 = prs.slides.add_slide(blank_layout)
    add_header(slide5, "Dataset Description & Simulation Heuristics")

    # Callout banner
    add_card(slide5, Inches(0.8), Inches(1.5), Inches(11.7), Inches(0.6), bg_color=LIGHT_BLUE, border_color=SKY_BLUE)
    tb_c = slide5.shapes.add_textbox(Inches(1.0), Inches(1.55), Inches(11.3), Inches(0.5))
    p = tb_c.text_frame.paragraphs[0]
    p.text = "ℹ️ Academic Simulation Notice: Carrier telemetry modeled via domain heuristics inspired by standard networking parameters."
    p.font.size = Pt(10.5)
    p.font.bold = True
    p.font.color.rgb = RGBColor(12, 74, 110)

    # Left: 12 Columns Overview
    add_card(slide5, Inches(0.8), Inches(2.2), Inches(5.7), Inches(4.7))
    tb_dl = slide5.shapes.add_textbox(Inches(1.0), Inches(2.3), Inches(5.3), Inches(4.4))
    tf_dl = tb_dl.text_frame
    tf_dl.word_wrap = True

    p = tf_dl.paragraphs[0]
    p.text = "The 12 Dataset Columns"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = NAVY

    cols_desc = [
        ("device_id", "Unique string identifier (DEV-1001 to DEV-6000)"),
        ("device_type", "Router, Switch, Base_Station, Optical, Gateway"),
        ("region", "North, South, East, West, Central"),
        ("network_traffic_mbps", "Throughput volume (50.0 to 10,000.0 Mbps)"),
        ("signal_strength_dbm", "RSSI/RSRP level (-120.0 to -45.0 dBm; 2.08% null)"),
        ("packet_loss_pct", "Packet drop percentage (0.0% to 15.0%; 2.14% null)"),
        ("latency_ms", "Round-trip delay (5.0 to 350.0 ms; 1.58% null)"),
        ("device_status", "Instantaneous alarm: Normal, Degraded, Critical"),
        ("device_temperature_c", "Internal operating temp (25 to 95 °C; 2.04% null)"),
        ("historical_faults_count", "Logged faults in prior 6 months (0 to 12)"),
        ("uptime_days", "Continuous runtime (1.0 to 730.0 days)"),
        ("failure_next_24h", "Target Label: 0 (Healthy), 1 (Failure in 24h)")
    ]
    for c_name, c_info in cols_desc:
        p = tf_dl.add_paragraph()
        p.space_before = Pt(2)
        r = _add_run(p, f"• {c_name}: ")
        r.bold = True
        r.font.size = Pt(9.5)
        r.font.color.rgb = SKY_BLUE
        r2 = _add_run(p, c_info)
        r2.font.size = Pt(9.5)
        r2.font.color.rgb = DARK_TEXT

    # Right: Label Generation & Utilization Math
    add_card(slide5, Inches(6.8), Inches(2.2), Inches(5.7), Inches(4.7))
    tb_dr = slide5.shapes.add_textbox(Inches(7.0), Inches(2.3), Inches(5.3), Inches(4.4))
    tf_dr = tb_dr.text_frame
    tf_dr.word_wrap = True

    p = tf_dr.paragraphs[0]
    p.text = "Mathematical Simulation Logic"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = NAVY

    right_points = [
        ("Rated Line-Rate Capacities:", "Traffic utilization evaluated against rated limits: Optical Transponder (10G), Router (8G), Base Station (5G), Switch (4.5G), Gateway (3.5G)."),
        ("Operational Stress Score (R):", "Weighted composite: 2.2(packet_loss) + 1.8(temp) + 1.6(latency) + 1.5(weak_signal) + 1.4(traffic_util) + 1.2(faults) + 0.3(uptime) + ε."),
        ("Stochastic Risk Noise (ε):", "Gaussian noise ε ~ N(0, 0.45) added to prevent deterministic thresholds and simulate unmonitored hardware fatigue."),
        ("Logistic Sigmoid Probability:", "P(failure) = 1 / (1 + e^{-(R - 5.10)})."),
        ("Realistic Imbalanced Distribution:", "Bernoulli trial generates exactly 685 failures (13.70%), within the realistic 12–15% telecom domain range.")
    ]
    for t_r, d_r in right_points:
        p = tf_dr.add_paragraph()
        p.space_before = Pt(6)
        r = _add_run(p, f"• {t_r} ")
        r.bold = True
        r.font.size = Pt(10.5)
        r.font.color.rgb = NAVY
        r2 = _add_run(p, d_r)
        r2.font.size = Pt(10)
        r2.font.color.rgb = DARK_TEXT

    # =======================================================================
    # SLIDE 6: DATA PREPROCESSING USING PYSPARK
    # =======================================================================
    slide6 = prs.slides.add_slide(blank_layout)
    add_header(slide6, "Data Preprocessing Using PySpark MLlib")

    stages_info = [
        ("1. Imputer (Median Strategy)", "Fitted strictly on training data for numerical telemetry:\n• signal_strength_dbm\n• packet_loss_pct\n• latency_ms\n• device_temperature_c\nPrevents data leakage from test rows.", SKY_BLUE),
        ("2. Training Mode Imputation", "Missing entries in categorical 'device_status' are imputed using the most frequent training category ('Normal').\nGuarantees zero nulls before categorical indexing.", NAVY),
        ("3. StringIndexer", "Encodes distinct string categories into numerical indices (0 to k-1):\n• device_type (5 categories)\n• region (5 categories)\n• device_status (3 categories)\nhandleInvalid='keep' handles unseen labels.", SKY_BLUE),
        ("4. OneHotEncoder", "Converts numerical category indices into orthogonal sparse binary vectors.\nPrevents the linear model from assuming false ordinal ranking between device types.", NAVY),
        ("5. VectorAssembler", "Combines all 4 imputed telemetry columns, 3 raw numerical columns, and 3 one-hot vector representations into a single unified 'features' vector column mandatory for Spark MLlib.", SKY_BLUE),
        ("6. Pipeline Encapsulation", "All feature transformers and the Logistic Regression estimator are bundled into a single Spark ML Pipeline, enabling unified fitting and atomic model serialization.", NAVY),
    ]

    for i, (st_t, st_d, col_a) in enumerate(stages_info):
        row = i // 3
        col = i % 3
        l = Inches(0.8 + col * 4.0)
        t = Inches(1.6 + row * 2.7)
        w = Inches(3.7)
        h = Inches(2.4)

        add_card(slide6, l, t, w, h)
        tb = slide6.shapes.add_textbox(l + Inches(0.2), t + Inches(0.2), w - Inches(0.4), h - Inches(0.3))
        tf = tb.text_frame
        tf.word_wrap = True

        p1 = tf.paragraphs[0]
        p1.text = st_t
        p1.font.size = Pt(13)
        p1.font.bold = True
        p1.font.color.rgb = col_a

        p2 = tf.add_paragraph()
        p2.space_before = Pt(6)
        p2.text = st_d
        p2.font.size = Pt(10.5)
        p2.font.color.rgb = DARK_TEXT

    # =======================================================================
    # SLIDE 7: LOGISTIC REGRESSION CLASSIFIER
    # =======================================================================
    slide7 = prs.slides.add_slide(blank_layout)
    add_header(slide7, "Logistic Regression in Spark MLlib")

    # Left: Mathematical Principles
    add_card(slide7, Inches(0.8), Inches(1.6), Inches(5.6), Inches(5.2))
    tb_l = slide7.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(5.2), Inches(4.8))
    tf_l = tb_l.text_frame
    tf_l.word_wrap = True

    p = tf_l.paragraphs[0]
    p.text = "Mathematical Formulation"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = NAVY

    math_points = [
        ("Log-Odds Formulation:", "Models the log-odds of failure as a linear combination of features:\nln(P / (1 - P)) = w^T x + b"),
        ("Calibrated Probability Output:", "Applies the logistic sigmoid transformation to output a continuous risk score P in [0.0, 1.0]."),
        ("L2 Regularization (Ridge):", "Applies mild weight shrinkage (regParam = 0.01) to penalize excessive coefficient magnitudes and avoid collinear overfitting."),
        ("Iterative Optimization:", "Spark uses the L-BFGS distributed optimization algorithm to converge weights over up to 100 iterations."),
        ("Vectorized Execution:", "Executes distributed matrix operations natively across CPU cores using local standalone partitioning.")
    ]
    for title, desc in math_points:
        p = tf_l.add_paragraph()
        p.space_before = Pt(8)
        r = _add_run(p, f"• {title} ")
        r.bold = True
        r.font.size = Pt(11.5)
        r.font.color.rgb = SKY_BLUE
        r2 = _add_run(p, desc)
        r2.font.size = Pt(11)
        r2.font.color.rgb = DARK_TEXT

    # Right: Why Logistic Regression is Ideal
    add_card(slide7, Inches(6.8), Inches(1.6), Inches(5.7), Inches(5.2))
    tb_r = slide7.shapes.add_textbox(Inches(7.0), Inches(1.8), Inches(5.3), Inches(4.8))
    tf_r = tb_r.text_frame
    tf_r.word_wrap = True

    p = tf_r.paragraphs[0]
    p.text = "Why Logistic Regression for this Problem?"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = NAVY

    why_points = [
        ("Continuous Risk Gradients:", "Unlike hard decision tree cutoffs, Logistic Regression outputs well-calibrated probabilities essential for priority ranking in NOC consoles."),
        ("Direct Interpretability:", "Each feature coefficient reveals the direction and magnitude of risk contribution (e.g., positive weights for packet loss and temperature)."),
        ("Computational Efficiency:", "Fast distributed training and low memory footprint in Spark standalone mode."),
        ("Seamless Threshold Tuning:", "Continuous output allows flexible post-hoc decision threshold optimization without modifying or retraining the underlying model.")
    ]
    for title, desc in why_points:
        p = tf_r.add_paragraph()
        p.space_before = Pt(10)
        r = _add_run(p, f"• {title} ")
        r.bold = True
        r.font.size = Pt(11.5)
        r.font.color.rgb = NAVY
        r2 = _add_run(p, desc)
        r2.font.size = Pt(11)
        r2.font.color.rgb = DARK_TEXT

    # =======================================================================
    # SLIDE 8: CLASSIFICATION THRESHOLD OPTIMIZATION
    # =======================================================================
    slide8 = prs.slides.add_slide(blank_layout)
    add_header(slide8, "Classification Threshold Optimization (Phase 2.1)")

    # Top summary card
    add_card(slide8, Inches(0.8), Inches(1.5), Inches(11.7), Inches(1.5), bg_color=LIGHT_BLUE, border_color=SKY_BLUE)
    tb_ts = slide8.shapes.add_textbox(Inches(1.0), Inches(1.6), Inches(11.3), Inches(1.3))
    tf_ts = tb_ts.text_frame
    tf_ts.word_wrap = True

    p = tf_ts.paragraphs[0]
    p.text = "Why Default 0.50 Threshold Failed & How 0.16 Was Selected"
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = NAVY

    p2 = tf_ts.add_paragraph()
    p2.space_before = Pt(4)
    p2.text = (
        "In imbalanced problems (~13.7% failure rate), a default 0.50 cutoff demands >50% certainty before flagging an alert. "
        "At 0.50, the model missed 126 out of 132 failures (Recall = 4.55%). "
        "We tuned the decision threshold strictly on the validation partition (750 records) by sweeping candidate cutoffs [0.08–0.50]. "
        "Threshold θ = 0.16 was selected because it achieved the maximum validation F1-score (31.61%)."
    )
    p2.font.size = Pt(11)
    p2.font.color.rgb = DARK_TEXT

    # Comparison Table Card
    add_card(slide8, Inches(0.8), Inches(3.2), Inches(11.7), Inches(3.8))
    tb_tbl = slide8.shapes.add_textbox(Inches(1.0), Inches(3.4), Inches(11.3), Inches(3.4))
    tf_tbl = tb_tbl.text_frame
    tf_tbl.word_wrap = True

    p = tf_tbl.paragraphs[0]
    p.text = "Side-by-Side Performance Comparison (Untouched Test Set: 958 Records)"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = NAVY

    comp_items = [
        ("Decision Threshold", "0.50 (Standard Default)", "0.16 (Validation F1 Tuned)", "Calibrated to base failure rate (~13.7%)"),
        ("Failure Detection Rate (Recall)", "4.55% (Only 6 caught)", "52.27% (69 caught)", "Over 11x increase in detected impending outages"),
        ("Positive Precision", "85.71% (1 false alarm)", "25.46% (202 false alarms)", "1 in 4 alerts results in an outage (viable NOC ratio)"),
        ("Balanced F1-Score", "8.63%", "34.24%", "Nearly 4-fold improvement in harmonic trade-off"),
        ("Overall Accuracy", "86.74%", "72.34%", "Lower raw accuracy as model proactively flags risk"),
        ("ROC-AUC Score", "0.6932", "0.6932", "Identical (threshold-independent ranking capability)")
    ]
    for metric, def_val, opt_val, notes in comp_items:
        p = tf_tbl.add_paragraph()
        p.space_before = Pt(4)
        r = _add_run(p, f"• {metric:<30} ")
        r.bold = True
        r.font.size = Pt(10.5)
        r.font.color.rgb = SKY_BLUE
        r2 = _add_run(p, f"| Default: {def_val:<22} | Optimal: {opt_val:<22} | {notes}")
        r2.font.size = Pt(10)
        r2.font.color.rgb = DARK_TEXT

    # =======================================================================
    # SLIDE 9: MODEL EVALUATION & CONFUSION MATRIX
    # =======================================================================
    slide9 = prs.slides.add_slide(blank_layout)
    add_header(slide9, "Model Evaluation & Confusion Matrix Analysis")

    # Left: Confusion Matrix Box
    add_card(slide9, Inches(0.8), Inches(1.6), Inches(5.6), Inches(5.2))
    tb_cml = slide9.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(5.2), Inches(4.8))
    tf_cml = tb_cml.text_frame
    tf_cml.word_wrap = True

    p = tf_cml.paragraphs[0]
    p.text = "Test Confusion Matrix (Threshold = 0.16)"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = NAVY

    # Grid breakdown
    cm_items = [
        ("True Negatives (TN = 624):", "Correctly identified healthy components.", GREEN_OK),
        ("False Positives (FP = 202):", "Preventive inspection alerts (false alarms).", RGBColor(234, 88, 12)),
        ("False Negatives (FN = 63):", "Undetected failures (halved from 126 at θ=0.50).", RED_ALERT),
        ("True Positives (TP = 69):", "Imminent failures successfully caught 24h in advance.", SKY_BLUE),
    ]
    for title, desc, col_c in cm_items:
        p = tf_cml.add_paragraph()
        p.space_before = Pt(8)
        r = _add_run(p, f"• {title} ")
        r.bold = True
        r.font.size = Pt(12)
        r.font.color.rgb = col_c
        r2 = _add_run(p, desc)
        r2.font.size = Pt(11)
        r2.font.color.rgb = DARK_TEXT

    p_summary = tf_cml.add_paragraph()
    p_summary.space_before = Pt(16)
    p_summary.text = "Operational Impact:\nMissing an actual failure costs $10,000+ in SLA penalties and emergency repairs. A false alarm costs <$100 in automated diagnostic pings. Catching 69 failures justifies 202 preventive checks."
    p_summary.font.size = Pt(10.5)
    p_summary.font.italic = True
    p_summary.font.color.rgb = MUTED_TEXT

    # Right: Embedded Confusion Matrix Image
    if os.path.exists("dashboard_confusion_matrix.png"):
        slide9.shapes.add_picture("dashboard_confusion_matrix.png", Inches(6.8), Inches(1.8), width=Inches(5.7))

    # =======================================================================
    # SLIDE 10: INTERACTIVE DASHBOARD DEMONSTRATION
    # =======================================================================
    slide10 = prs.slides.add_slide(blank_layout)
    add_header(slide10, "Interactive Streamlit NOC Dashboard (Phase 3)")

    # Left: Embedded KPI overview screenshot
    if os.path.exists("dashboard_kpi_overview.png"):
        slide10.shapes.add_picture("dashboard_kpi_overview.png", Inches(0.8), Inches(1.6), width=Inches(5.7))

    # Right: Embedded Table explorer screenshot
    if os.path.exists("dashboard_risk_explorer.png"):
        slide10.shapes.add_picture("dashboard_risk_explorer.png", Inches(6.8), Inches(1.6), width=Inches(5.7))

    # Bottom caption card
    add_card(slide10, Inches(0.8), Inches(5.6), Inches(11.7), Inches(1.4))
    tb_db = slide10.shapes.add_textbox(Inches(1.0), Inches(5.7), Inches(11.3), Inches(1.2))
    tf_db = tb_db.text_frame
    tf_db.word_wrap = True

    p = tf_db.paragraphs[0]
    p.text = "NOC Operations Features (Running at http://localhost:8501):"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = NAVY

    p2 = tf_db.add_paragraph()
    p2.space_before = Pt(2)
    p2.text = (
        "• Real-Time Risk Ranking: Components sorted by continuous failure probability; visual badges highlight Critical (≥35%) and Elevated (≥16%) risk.\n"
        "• Multivariable Filtering: Operators dynamically isolate specific hardware categories (e.g. Optical Transponders) and regional zones.\n"
        "• Normalized Failure Rates: Calculates exact percentage failure frequencies per device type to pinpoint vulnerable infrastructure."
    )
    p2.font.size = Pt(10)
    p2.font.color.rgb = DARK_TEXT

    # =======================================================================
    # SLIDE 11: RESULTS, LIMITATIONS & FUTURE SCOPE
    # =======================================================================
    slide11 = prs.slides.add_slide(blank_layout)
    add_header(slide11, "Results, Limitations & Future Scope")

    # Left Card: Limitations
    add_card(slide11, Inches(0.8), Inches(1.6), Inches(5.6), Inches(5.2))
    tb_lim = slide11.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(5.2), Inches(4.8))
    tf_lim = tb_lim.text_frame
    tf_lim.word_wrap = True

    p = tf_lim.paragraphs[0]
    p.text = "Academic Limitations Disclosed"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = RED_ALERT

    lims = [
        ("Simulated Telemetry Origin:", "Data was mathematically modeled rather than collected from live carrier switch physical taps."),
        ("No External Catastrophes:", "Real-world outages often stem from external force majeure events (fiber cuts, utility grid loss) with zero telemetry degradation."),
        ("Stationary Data Snapshot:", "Does not model seasonal concept drift, holiday traffic spikes, or firmware upgrade anomalies."),
        ("Single-Node Standalone:", "Evaluated on a local multi-threaded Spark instance rather than a physical multi-server cluster.")
    ]
    for title, desc in lims:
        p = tf_lim.add_paragraph()
        p.space_before = Pt(10)
        r = _add_run(p, f"• {title} ")
        r.bold = True
        r.font.size = Pt(11.5)
        r.font.color.rgb = RED_ALERT
        r2 = _add_run(p, desc)
        r2.font.size = Pt(11)
        r2.font.color.rgb = DARK_TEXT

    # Right Card: Future Scope
    add_card(slide11, Inches(6.8), Inches(1.6), Inches(5.7), Inches(5.2))
    tb_fut = slide11.shapes.add_textbox(Inches(7.0), Inches(1.8), Inches(5.3), Inches(4.8))
    tf_fut = tb_fut.text_frame
    tf_fut.word_wrap = True

    p = tf_fut.paragraphs[0]
    p.text = "Future Research & Expansion Scope"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = SKY_BLUE

    futs = [
        ("Physical Cluster Deployment:", "Benchmark PySpark scalability on an Apache Spark cluster managed by Kubernetes or Apache YARN."),
        ("Streaming Telemetry (Spark Streaming):", "Integrate Apache Kafka and Spark Structured Streaming for continuous micro-batch sliding-window scoring."),
        ("Survival Analysis (RUL Modeling):", "Predict exact Remaining Useful Life (RUL) in hours using Cox Proportional Hazards regression."),
        ("Ensemble Tree Comparisons:", "Benchmark Logistic Regression against Spark MLlib's RandomForestClassifier and GBTClassifier.")
    ]
    for title, desc in futs:
        p = tf_fut.add_paragraph()
        p.space_before = Pt(10)
        r = _add_run(p, f"• {title} ")
        r.bold = True
        r.font.size = Pt(11.5)
        r.font.color.rgb = SKY_BLUE
        r2 = _add_run(p, desc)
        r2.font.size = Pt(11)
        r2.font.color.rgb = DARK_TEXT

    # =======================================================================
    # SLIDE 12: CONCLUSION
    # =======================================================================
    slide12 = prs.slides.add_slide(blank_layout)
    add_header(slide12, "Conclusion & Project Summary")

    add_card(slide12, Inches(0.8), Inches(1.6), Inches(11.7), Inches(5.2))
    tb_con = slide12.shapes.add_textbox(Inches(1.1), Inches(1.9), Inches(11.1), Inches(4.6))
    tf_con = tb_con.text_frame
    tf_con.word_wrap = True

    p = tf_con.paragraphs[0]
    p.text = "Summary of Key Project Achievements"
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = NAVY

    concs = [
        ("End-to-End PySpark Implementation:", "Successfully implemented distributed data loading, missing-value imputation (median/mode), categorical encoding (StringIndexer + OneHotEncoder), and feature vector assembly using native Spark MLlib."),
        ("Leakage Prevention Architecture:", "Enforced strict three-way partitioning (Train, Validation, Test), ensuring preprocessing statistics and decision thresholds were learned strictly from training data."),
        ("Operational Threshold Optimization:", "Demonstrated that tuning the classification threshold from 0.50 to 0.16 increased failure recall from 4.55% to 52.27% and boosted F1-score from 8.63% to 34.24%, creating an actionable early-warning system."),
        ("Production-Style NOC Dashboard:", "Developed an interactive Streamlit and Plotly dashboard enabling operations engineers to inspect component risk levels, view confusion matrices, and filter predictions dynamically."),
        ("Academic Rigor & Honesty:", "Maintained complete transparency regarding synthetic simulation constraints without fabricating evaluation scores.")
    ]
    for title, desc in concs:
        p = tf_con.add_paragraph()
        p.space_before = Pt(10)
        r = _add_run(p, f"✓ {title} ")
        r.bold = True
        r.font.size = Pt(12)
        r.font.color.rgb = GREEN_OK
        r2 = _add_run(p, desc)
        r2.font.size = Pt(11.5)
        r2.font.color.rgb = DARK_TEXT

    prs.save(output_filename)
    print(f"Presentation saved successfully: {output_filename}")


if __name__ == "__main__":
    create_presentation("PROJECT_PRESENTATION.pptx")
