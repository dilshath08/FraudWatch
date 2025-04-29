# dashboard/manual_entry_app.py

import streamlit as st
import pandas as pd
import joblib
import numpy as np

# --- Setup ---

# Load the trained model
model = joblib.load('outputs/models/fraudlock_rf_model(modified).pkl')

st.set_page_config(page_title="Manual Transaction Fraud Check", page_icon="📝", layout="centered")

# --- App Title ---

st.title("📝 Manual Transaction Fraud Check")
st.markdown("Enter a transaction manually to check if it's fraudulent in real-time. 🚀")
st.markdown("---")

# --- Layout: Input Columns ---

col1, col2 = st.columns(2)

with col1:
    amount = st.number_input('💵 Transaction Amount ($)', min_value=0.0, format="%.2f")
    oldbalanceOrg = st.number_input('🏦 Old Balance (Origin)', min_value=0.0, format="%.2f")
    newbalanceOrig = st.number_input('🏦 New Balance (Origin)', min_value=0.0, format="%.2f")

with col2:
    oldbalanceDest = st.number_input('🏦 Old Balance (Destination)', min_value=0.0, format="%.2f")
    newbalanceDest = st.number_input('🏦 New Balance (Destination)', min_value=0.0, format="%.2f")
    transaction_type = st.selectbox(
        '🔀 Transaction Type',
        ('CASH_IN', 'CASH_OUT', 'DEBIT', 'PAYMENT', 'TRANSFER')
    )

st.markdown("---")

# --- Feature Engineering Same as Training ---

errorBalanceOrig = oldbalanceOrg - newbalanceOrig - amount
errorBalanceDest = oldbalanceDest + amount - newbalanceDest

high_amount_threshold = 10000  # (adjust based on your dataset if needed)
isHighAmount = 1 if amount >= high_amount_threshold else 0
isTransferOrCashout = 1 if transaction_type in ['TRANSFER', 'CASH_OUT'] else 0

# Manual One-hot encoding
type_CASH_IN = 1 if transaction_type == 'CASH_IN' else 0
type_CASH_OUT = 1 if transaction_type == 'CASH_OUT' else 0
type_DEBIT = 1 if transaction_type == 'DEBIT' else 0
type_PAYMENT = 1 if transaction_type == 'PAYMENT' else 0
type_TRANSFER = 1 if transaction_type == 'TRANSFER' else 0

# Prepare Input DataFrame
input_data = pd.DataFrame([{
    'amount': amount,
    'oldbalanceOrg': oldbalanceOrg,
    'newbalanceOrig': newbalanceOrig,
    'oldbalanceDest': oldbalanceDest,
    'newbalanceDest': newbalanceDest,
    'isFlaggedFraud': 0,
    'errorBalanceOrig': errorBalanceOrig,
    'errorBalanceDest': errorBalanceDest,
    'isHighAmount': isHighAmount,
    'isTransferOrCashout': isTransferOrCashout,
    'type_CASH_IN': type_CASH_IN,
    'type_CASH_OUT': type_CASH_OUT,
    'type_DEBIT': type_DEBIT,
    'type_PAYMENT': type_PAYMENT,
    'type_TRANSFER': type_TRANSFER
}])

# --- Predict Button ---

if st.button('🔍 Predict Fraud or Not'):
    prediction = model.predict(input_data)[0]
    fraud_probability = model.predict_proba(input_data)[0][1]

    st.markdown("---")
    st.subheader("🔔 Prediction Result:")

    if prediction == 1:
        st.error(f"🚨 FRAUD DETECTED! (Fraud Probability: {fraud_probability*100:.2f}%)")
    else:
        st.success(f"✅ Transaction Approved (Fraud Probability: {fraud_probability*100:.2f}%)")

# --- End of App ---
