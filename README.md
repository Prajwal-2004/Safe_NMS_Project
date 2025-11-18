## 🛡️ Safe AI-Driven Self-Healing NMS: Interactive Prototype

### Project Overview

This project demonstrates a novel **Hybrid AI** approach to network automation, designed to provide the adaptive speed of Machine Learning (ML) with the safety guarantees required by enterprise clients like Wipro.

The core innovation is a **Safety Guardrail** layer that scrutinizes and validates every AI recommendation before execution, preventing catastrophic outages caused by unreliable or untested AI policies. The result is a **Trustworthy and Explainable** self-healing system.

### Key Features

* **Hybrid Logic**: Combines a Machine Learning classifier (for proactive fault prediction) with Rule-based Governance (for safety and compliance).
* **Safety Guarantee**: Hard-coded business policies override dangerous AI suggestions (e.g., preventing a core router restart during high user load).
* **Explainability**: Every decision (Approved or Blocked) is logged with a human-readable justification.
* **Interactive Dashboard**: Uses Streamlit to visualize the full simulation and allow dynamic inspection of decisions at any time point.

***

### ⚙️ Technical Architecture

The system operates using a four-stage loop executed by the main script:

1.  **Telemetry Input:** Reads simulated network state metrics (Latency, Users, CPU).
2.  **ML Prediction:** The trained Random Forest model predicts the best action (e.g., *Restart*, *Reroute*).
3.  **Safety Governance (The Hybrid Core):** The `policy_rules.py` module checks the ML's prediction against strict safety constraints.
4.  **Action & Log:** The approved (or fallback) action is recorded, logged, and visualized on the dashboard.

***

## 🚀 Setup and Run Instructions (Start to Finish)

Follow these steps exactly to run the entire project from scratch in your VSCode terminal.

### Step 1: Install Dependencies

You must install all necessary Python libraries listed in `requirements.txt`.

```bash
# Ensure you are in the Safe_NMS_Project folder
pip install -r requirements.txt


Step 1: python data_gen.py
Step 2: python -m streamlit run interactive_dashboard.py