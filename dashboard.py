import streamlit as st
import sqlite3
import pandas as pd

# 1. Page Configuration
st.set_page_config(page_title="V-Shield Telemetry", page_icon="🛡️", layout="wide")

st.title("🛡️ V-Shield Autonomous SOC")
st.subheader("Global Telemetry & Mitigation Dashboard")
st.markdown("---")

# 2. Database Connection Function
def load_data(query):
    try:
        # Connects to the SQLite database you uploaded to GitHub
        conn = sqlite3.connect('threats.db')
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    except Exception as e:
        return pd.DataFrame() # Returns empty if the table doesn't exist yet

# 3. Load Data based on Chapter 3 Schemas
df_threats = load_data("SELECT * FROM Threat_Telemetry ORDER BY Timestamp DESC")
df_mitigations = load_data("SELECT * FROM Mitigation_Actions ORDER BY Timestamp DESC")

# 4. Dashboard UI Rendering
if df_threats.empty:
    st.info("🟢 System is online. Monitoring for threats... (No data in database yet)")
else:
    # Top KPI Metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Threats Detected", len(df_threats))
        
    with col2:
        mitigation_count = len(df_mitigations) if not df_mitigations.empty else 0
        st.metric("Threats Autonomously Blocked", mitigation_count)
        
    with col3:
        avg_latency = df_mitigations['Latency_Secs'].mean() if not df_mitigations.empty else 0.0
        st.metric("Avg Mitigation Latency", f"{avg_latency:.2f} seconds")

    st.markdown("---")

    # Visual Graph
    st.markdown("### 📊 Attack Frequency by IP Address")
    ip_counts = df_threats['Source_IP'].value_counts()
    st.bar_chart(ip_counts)

    # Data Tables
    st.markdown("### 🚨 Live Threat Telemetry (Event Logs)")
    st.dataframe(df_threats, use_container_width=True)

    st.markdown("### 🧱 Autonomous Mitigation Actions (Firewall Drops)")
    if not df_mitigations.empty:
        st.dataframe(df_mitigations, use_container_width=True)
    else:
        st.warning("No mitigation actions have been logged yet.")
