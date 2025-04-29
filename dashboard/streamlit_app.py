# dashboard/streamlit_app.py

import streamlit as st
import pandas as pd
import joblib
import time
import numpy as np

# --- Setup ---

# Load the trained model
model = joblib.load('outputs/models/fraudlock_rf_model(modified).pkl')

st.set_page_config(page_title="FraudLock Real-Time Dashboard", page_icon="🚀", layout="wide")

# --- Load the Full Dataset ---

df = pd.read_csv('data/processed/processed_fraudlock_data.csv')

# Remove sampling: use all rows
X_stream = df.drop('isFraud', axis=1)
y_stream = df['isFraud']

# --- App Layout ---

st.title('🚀 FraudLock: Real-Time Fraud Detection Dashboard')
st.markdown("Real-time fraud detection system for instant payments 🔥")

transaction_placeholder = st.empty()
summary_placeholder = st.empty()
fraud_list_placeholder = st.empty()
fraud_counter_placeholder = st.empty()

st.markdown("---")
st.header("🔎 Live Transaction Monitoring")

# Create log lists
results_log = []
fraud_transactions_log = []

fraud_count = 0
total_transactions = 0

# --- Real-Time Simulation ---

for idx, transaction in X_stream.iterrows():
    transaction_reshaped = transaction.values.reshape(1, -1)
    prediction = model.predict(transaction_reshaped)[0]
    prob = model.predict_proba(transaction_reshaped)[0][1]

    # Fake streaming delay (adjust to control speed)
    time.sleep(0.05)   # 50ms delay = ~20 transactions per second

    total_transactions += 1

    # --- Display live transaction alert ---
    with transaction_placeholder.container():
        st.metric(label="Current Transaction ID", value=str(idx))
        st.metric(label="Fraud Probability (%)", value=f"{prob*100:.2f}%")

        if prediction == 1:
            st.error(f"🚨 FRAUD DETECTED! Transaction ID {idx} → LOCKED 🔒")
        else:
            st.success(f"✅ Transaction ID {idx} → Approved")
        
        st.markdown("---")

    # --- Record into logs ---
    results_log.append({
        'Transaction ID': idx,
        'Fraud Probability (%)': round(prob * 100, 2),
        'Predicted Label': 'Fraud' if prediction == 1 else 'Not Fraud'
    })

    if prediction == 1:
        fraud_transactions_log.append({
            'Transaction ID': idx,
            'Fraud Probability (%)': round(prob * 100, 2)
        })
        fraud_count += 1

    # --- Update Summary Table ---
    log_df = pd.DataFrame(results_log)

    with summary_placeholder.container():
        st.header("📄 Live Transaction Summary Table")
        st.dataframe(log_df, use_container_width=True)

    # --- Update Live Fraud Table ---
    fraud_df = pd.DataFrame(fraud_transactions_log)

    with fraud_list_placeholder.container():
        st.header("🚨 Live Detected Frauds")
        if not fraud_df.empty:
            st.dataframe(fraud_df, use_container_width=True)
        else:
            st.info("✅ No frauds detected yet.")

    # --- Update Fraud Counter ---
    with fraud_counter_placeholder.container():
        st.header("📊 Fraud Detection Stats")
        st.metric(label="Total Transactions Processed", value=total_transactions)
        st.metric(label="🚨 Frauds Detected", value=fraud_count)
        fraud_rate = (fraud_count / total_transactions) * 100
        st.metric(label="Fraud Rate (%)", value=f"{fraud_rate:.2f}%")

    # --- Optional Stop for Testing ---
    if total_transactions >= 500:
        st.success("✅ Real-Time Simulation Completed (500 transactions)!")
        break

# --- End of App ---
