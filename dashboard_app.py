import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestClassifier
from policy_rules import check_safety 
from matplotlib.lines import Line2D 

# --- 1. SETUP & MODEL TRAINING (Executed once) ---
st.set_page_config(layout="wide")
st.title("🛡️ Safe Self-Healing NMS: Interactive Prototype")
st.markdown("---")

# Load Data
try:
    train_df = pd.read_csv('train_data.csv')
    live_df_raw = pd.read_csv('live_data.csv') 
except FileNotFoundError:
    st.error("Error: Please run `python data_gen.py` first in the terminal.")
    st.stop() 

# Train Model
st.info("System Initializing: Training AI Model...")
X = train_df[['Latency', 'CPU_Load', 'Active_Users', 'Packet_Loss']]
y = train_df['Recommended_Action']
clf = RandomForestClassifier(n_estimators=10, random_state=42)
clf.fit(X, y)
st.success("AI Model Trained. Ready for Simulation.")

# --- 2. RUN FULL SIMULATION LOOP (Generate data for the full graph) ---
results_latency = []
log_history = [] 
live_df_sim = live_df_raw.copy()

for index, row in live_df_sim.iterrows():
    current_metrics = row.values.reshape(1, -1)
    prediction_id = clf.predict(current_metrics)[0]
    row_dict = row.to_dict()
    
    # Capture the new 'decision_source' return value
    final_action, explanation, decision_source = check_safety(prediction_id, row_dict) 
    
    results_latency.append(row['Latency'])
    log_history.append({
        'index': index, 
        'latency': row['Latency'],
        'action': final_action,
        'reason': explanation,
        'metrics': row_dict,
        'source': decision_source 
    })
    
    # Simulate 'fixing' the network for the NEXT step's visual data
    if "Restart Router" in final_action or "Reroute Traffic" in final_action or "Scale Up" in final_action:
         if index < len(live_df_sim) - 1:
             live_df_sim.at[index+1, 'Latency'] = max(20, live_df_sim.at[index+1, 'Latency'] * 0.2)
             live_df_sim.at[index+1, 'CPU_Load'] = max(25, live_df_sim.at[index+1, 'CPU_Load'] * 0.5)

# --- 3. INTERACTIVE SLIDER & SELECTION ---

max_minutes = len(log_history) - 1
minute_to_check = st.slider(
    "Select Simulation Minute (T+): Drag the slider to review the decision for that moment.", 
    0, max_minutes, max_minutes
)

selected_log = log_history[minute_to_check]
is_blocked = "[GUARDRAIL TRIGGERED]" in selected_log['reason']

# --- 4. EXPLAINABLE METRICS & DECISION (Display all four metrics and source) ---
st.markdown("---")
st.subheader(f"Decision Inputs and Final Action at T+{minute_to_check} min")

# Use 5 columns for the input metrics and action
col1, col2, col3, col4, col5 = st.columns(5)

# Display all four input metrics
col1.metric("Latency (ms)", f"{int(selected_log['metrics']['Latency'])}")
col2.metric("CPU Load (%)", f"{int(selected_log['metrics']['CPU_Load'])}")
col3.metric("Packet Loss (%)", f"{selected_log['metrics']['Packet_Loss']:.2f}")
col4.metric("Active Users", f"{int(selected_log['metrics']['Active_Users'])}")
col5.metric("Action Taken", selected_log['action'])

st.markdown("---") # Separator line

# Display the source of the final decision
st.metric(
    label="Decision Source",
    value=selected_log['source'],
    delta_color="off"
)

# Display the safety status and rationale
if is_blocked:
    st.markdown("<h3 style='color: red;'>⚠️ Safety Status: Override Applied</h3>", unsafe_allow_html=True)
    st.warning(f"**Safety Rationale:** {selected_log['reason']}")
else:
    st.markdown("<h3 style='color: green;'>✅ Safety Status: Action Approved</h3>", unsafe_allow_html=True)
    st.success(f"**Decision Rationale:** {selected_log['reason']}")

st.markdown("---")


# --- 5. MATPLOTLIB VISUALIZATION (Full Annotated Graph) ---
st.subheader("Network Latency with All Interventions Highlighted")

fig, ax = plt.subplots(figsize=(12, 7))

ax.plot(results_latency, marker='o', linestyle='-', color='b', label='Observed Latency')

# Highlight the selected minute on the graph
ax.axvline(x=minute_to_check, color='purple', linestyle='--', label=f'Selected Minute (T+{minute_to_check})')


# ANNOTATION LOGIC (Anti-Overlap)
vertical_offset_multiplier = 25 
offset_counter = 0 

for log in log_history:
    if log['action'] != "Do Nothing":
        
        is_blocked = "[GUARDRAIL TRIGGERED]" in log['reason']
        color = 'red' if is_blocked else 'green'
        symbol = 'X' if is_blocked else 'o'
        
        vertical_offset = vertical_offset_multiplier * (offset_counter % 2 + 1)
        offset_counter += 1
            
        ax.scatter(log['index'], log['latency'], color=color, marker=symbol, s=150, zorder=5)

        status_text = "BLOCKED" if is_blocked else "APPROVED"
        annotation_text = f"Action: {log['action']}\nStatus: {status_text}"
        
        ax.annotate(
            annotation_text, 
            (log['index'], log['latency']), 
            xytext=(log['index'] + 0.1, log['latency'] + vertical_offset),
            fontsize=8,
            color='black',
            bbox=dict(boxstyle="round,pad=0.3", fc="white", alpha=0.7),
            arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=.2", color='gray')
        )

# GRAPH STYLING
ax.set_title("Safe Self-Healing Network Performance vs. Time (Interventions Highlighted)", fontsize=14)
ax.set_xlabel("Time (minutes)", fontsize=12)
ax.set_ylabel("Latency (ms)", fontsize=12)
ax.grid(True, linestyle='--', alpha=0.6)

# Custom legend
custom_lines = [
    Line2D([0], [0], color='blue', lw=2, label='Observed Latency'),
    Line2D([0], [0], color='purple', linestyle='--', label='Selected Time Point'),
    Line2D([0], [0], marker='o', color='w', markerfacecolor='green', markersize=10, label='Hybrid Action Taken (Approved)'),
    Line2D([0], [0], marker='X', color='w', markerfacecolor='red', markersize=10, label='AI Action BLOCKED (Guardrail Override)')
]
ax.legend(handles=custom_lines, loc='lower right') 

st.pyplot(fig)
