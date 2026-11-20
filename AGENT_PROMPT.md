# 🤖 AI Agent Setup Prompt (1-Click Run)

If you are running an AI coding assistant (such as **Antigravity**, **Cursor**, **Claude Code**, or **Copilot Workspace**), copy and paste the prompt below directly into the chat:

---

```text
I need to set up and run this Telecom Network Failure Prediction project:
Repository: https://github.com/harsh-lade23/Cluster-Computing-Project.git

Please perform the following end-to-end setup:
1. Clone the repository into a local directory and navigate into it.
2. Check if Java (JDK 11, 17, or 21) is installed via `java -version`. PySpark requires Java. If missing, please install OpenJDK for my operating system and ensure JAVA_HOME is configured.
3. Create a clean Python virtual environment (.venv) using Python 3.9+ and activate it.
4. Install all dependencies:
   pip install -r requirements.txt
5. Verify the PySpark ML pipeline by running:
   python src/train_model.py
6. Launch the interactive Streamlit dashboard:
   streamlit run app.py
7. Provide me the local URL to access the running dashboard in my browser, and summarize the key findings or reports available in the project.
```

---

## What the Agent Will Do:
- **Environment Verification**: Verifies Java JDK installation for Apache Spark local mode.
- **Dependency Isolation**: Creates a dedicated `.venv` and installs PySpark, Streamlit, Plotly, Pandas, and NumPy.
- **Pipeline Execution**: Trains and evaluates the PySpark MLlib logistic regression pipeline.
- **Interactive UI**: Launches the Streamlit monitoring dashboard at `http://localhost:8501`.
