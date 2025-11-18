import pandas as pd
import numpy as np
import random

def generate_data(num_samples=1000, is_training=True):
    data = []
    
    # Columns: Latency(ms), CPU_Load(%), Active_Users, Packet_Loss(%)
    for _ in range(num_samples):
        latency = np.random.randint(10, 500)
        cpu = np.random.randint(10, 100)
        users = np.random.randint(50, 1500)
        pkt_loss = np.random.uniform(0, 5.0)
        
        # Determine the "Correct" action based on logic (Logic we want ML to learn)
        # 0 = Do Nothing, 1 = Reroute Traffic, 2 = Restart Router, 3 = Scale Up
        action = 0 
        
        if cpu > 85:
            action = 3 # Scale Up
        elif latency > 200 or pkt_loss > 2.0:
            action = 2 # Restart (The aggressive fix)
        elif latency > 100:
            action = 1 # Reroute (The gentle fix)
        else:
            action = 0 # Normal
            
        data.append([latency, cpu, users, pkt_loss, action])

    cols = ['Latency', 'CPU_Load', 'Active_Users', 'Packet_Loss', 'Recommended_Action']
    df = pd.DataFrame(data, columns=cols)
    
    # If it's live data, we don't need the 'Recommended_Action' column (ML will predict it)
    if not is_training:
        return df.drop(columns=['Recommended_Action'])
    return df

# Generate and Save
print("Generating Training Data...")
df_train = generate_data(1000, is_training=True)
df_train.to_csv('train_data.csv', index=False)

print("Generating Live Simulation Data...")
df_live = generate_data(20, is_training=False) # 20 minutes of live data
df_live.to_csv('live_data.csv', index=False)

print("✅ Data Generation Complete. Files 'train_data.csv' and 'live_data.csv' created.")