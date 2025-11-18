def check_safety(predicted_action, row_data):
    """
    Inputs:
        predicted_action (int): 0=None, 1=Reroute, 2=Restart, 3=ScaleUp
        row_data (dict): The current metrics (Users, Latency, etc.)
    Returns:
        final_action (str): The action we actually take
        reason (str): Explanation for the human operator
    """
    
    users = row_data['Active_Users']
    latency = row_data['Latency']
    
    # Map ID to Name
    action_map = {0: "Do Nothing", 1: "Reroute Traffic", 2: "Restart Router", 3: "Scale Up Resources"}
    ai_choice = action_map.get(predicted_action, "Unknown")

    # --- GUARDRAIL LOGIC ---
    
    # RULE 1: High User Traffic Safety
    # If AI wants to "Restart Router" but users > 800, BLOCK IT.
    if predicted_action == 2 and users > 800:
        return "Reroute Traffic", f"[GUARDRAIL TRIGGERED] AI wanted '{ai_choice}' but Active Users ({users}) > 800. Unsafe to restart. Fallback to 'Reroute'."

    # RULE 2: Cost Optimization
    # If AI wants to "Scale Up" (add servers) but Latency is actually fine (<50), BLOCK IT.
    if predicted_action == 3 and latency < 50:
        return "Do Nothing", f"[GUARDRAIL TRIGGERED] AI wanted '{ai_choice}' but Latency is low ({latency}ms). Scaling up is waste of money."

    # If no rules violated, approve the AI's choice
    return ai_choice, f"AI Decision '{ai_choice}' approved. Safety checks passed."