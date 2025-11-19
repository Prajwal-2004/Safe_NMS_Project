# --- policy_rules.py ---

def check_safety(predicted_id, metrics):
    """
    Checks the AI's predicted action against hard-coded safety rules.
    Returns: (final_action, explanation, decision_source)
    """
    
    # Mapping the AI's numerical prediction to an action
    action_map = {
        0: "Do Nothing",
        1: "Reroute Traffic",
        2: "Restart Router",
        3: "Scale Up Capacity"
    }
    
    predicted_action = action_map.get(predicted_id, "Unknown Action")
    
    # --- SAFETY GUARDRAIL RULES ---
    
    # RULE 1: BLOCK high-risk 'Restart Router' action during high user load
    if predicted_action == "Restart Router" and metrics['Active_Users'] > 800:
        final_action = "Reroute Traffic" # Safer fallback action
        explanation = "[GUARDRAIL TRIGGERED] Cannot restart router; Active Users exceed 800. Fallback to safer Reroute."
        decision_source = "Runbook Override" # Source is the rulebook
        return final_action, explanation, decision_source

    # RULE 2: BLOCK unnecessary 'Scale Up Capacity' if current latency is low
    if predicted_action == "Scale Up Capacity" and metrics['Latency'] < 150:
        final_action = "Do Nothing" # Safest fallback: save resources
        explanation = "[GUARDRAIL TRIGGERED] Latency is below 150ms; Scale Up is unnecessary. Saving resources."
        decision_source = "Runbook Override" # Source is the rulebook
        return final_action, explanation, decision_source

    # --- ACTION APPROVED ---
    # If no rule blocks the action, the AI's decision is approved.
    if predicted_action != "Do Nothing":
        explanation = f"[APPROVED] AI recommendation confirmed safe. Latency: {int(metrics['Latency'])}ms."
        decision_source = "AI + Runbook Confirmation" # Source is both working together
    else:
        # If the AI predicts 'Do Nothing', it's always safe
        explanation = "Network stable, monitoring continues."
        decision_source = "AI-Driven Monitoring"
        
    return predicted_action, explanation, decision_source
