import streamlit as st
import pandas as pd
import numpy as np
import datetime
import sqlite3
import time

# 1. Enterprise Page Configuration
st.set_page_config(page_title="V-Shield Autonomous SOC", page_icon="🛡️", layout="wide")

# 2. Database Initialization (Ensures the DB exists in the cloud)
def init_cloud_db():
    conn = sqlite3.connect('threats.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS Threat_Telemetry 
                 (EventID INTEGER PRIMARY KEY AUTOINCREMENT, Source_IP TEXT, Timestamp DATETIME, Strike_Count INTEGER, Time_Gap_Ms REAL, Classification TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS Mitigation_Actions 
                 (ActionID INTEGER PRIMARY KEY AUTOINCREMENT, EventID INTEGER, Rule_Applied TEXT, Latency_Secs REAL, Timestamp DATETIME)''')
    conn.commit()
    conn.close()

init_cloud_db()

# 3. Create the Two Separate Environments using Tabs
tab_honeypot, tab_dashboard = st.tabs(["🕸️ Target: MIU SME Portal", "📊 Defender: SOC Dashboard"])

# ==========================================
# ENVIRONMENT 1: THE ATTACKER'S HONEYPOT
# ==========================================
with tab_honeypot:
    st.markdown("<h2 style='text-align: center; color: #38bdf8;'>MIU Secure Intranet</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #94a3b8;'>Authorized Personnel Only</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        with st.form("login_form"):
            username = st.text_input("Employee ID")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("AUTHENTICATE")
            
            if submitted:
                if username == "admin" and password == "MIU2026":
                    st.success("🎉 CONGRATULATIONS! You are an authentic user.")
                else:
                    st.error("ACCESS DENIED. Unauthorized activity detected.")
                    
                    # SIMULATE THE LIVE SVM AND FIREWALL RESPONSE
                    conn = sqlite3.connect('threats.db')
                    c = conn.cursor()
                    
                    # 1. Log the Threat
                    attacker_ip = f"192.168.1.{np.random.randint(50, 200)}"
                    timestamp = datetime.datetime.now()
                    strike_count = np.random.randint(5, 15)
                    time_gap = np.random.uniform(10, 80) # Fast attack = Malicious
                    
                    c.execute("INSERT INTO Threat_Telemetry (Source_IP, Timestamp, Strike_Count, Time_Gap_Ms, Classification) VALUES (?, ?, ?, ?, ?)",
                              (attacker_ip, timestamp, strike_count, time_gap, "Malicious (Brute Force)"))
                    event_id = c.lastrowid
                    
                    # 2. Simulate Latency and Log the Mitigation
                    time.sleep(1.2) # Simulate the SVM processing time
                    latency = np.random.uniform(0.8, 1.5)
                    c.execute("INSERT INTO Mitigation_Actions (EventID, Rule_Applied, Latency_Secs, Timestamp) VALUES (?, ?, ?, ?)",
                              (event_id, "WAF Drop (Autonomous)", latency, timestamp))
                    
                    conn.commit()
                    conn.close()
                    st.toast(f"Security Alert! Intrusion from {attacker_ip} blocked in {latency:.2f}s", icon="🚨")

# ==========================================
# ENVIRONMENT 2: THE DEFENDER'S DASHBOARD
# ==========================================
with tab_dashboard:
    st.title("🛡️ V-Shield Autonomous SOC")
    st.markdown("### Global Threat Telemetry & Mitigation Dashboard")
    st.markdown("---")

    # Load Data dynamically
    conn = sqlite3.connect('threats.db')
    df_threats = pd.read_sql_query("SELECT * FROM Threat_Telemetry ORDER BY Timestamp DESC", conn)
    df_mitigations = pd.read_sql_query("SELECT * FROM Mitigation_Actions ORDER BY Timestamp DESC", conn)
    conn.close()

    if df_threats.empty:
        st.info("🟢 System is online. Awaiting intrusion events... (Go to the Target Portal tab and attempt a fake login!)")
    else:
        # Live KPI Metrics
        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        col_m1.metric("Total Intrusions Logged", len(df_threats))
        col_m2.metric("Threats Autonomously Blocked", len(df_mitigations))
        avg_latency = df_mitigations['Latency_Secs'].mean() if not df_mitigations.empty else 0.0
        col_m3.metric("Avg Mitigation Latency", f"{avg_latency:.2f}s")
        col_m4.metric("SVM Accuracy Status", "Active", "Nominal")

        st.markdown("---")

        # Visual Graphs
        st.markdown("### 📊 Network Assault Volume")
        if len(df_threats) > 1:
            chart_data = df_threats.copy()
            chart_data['Timestamp'] = pd.to_datetime(chart_data['Timestamp'])
            chart_data.set_index('Timestamp', inplace=True)
            st.area_chart(chart_data['Strike_Count'], color="#ff4b4b")
        else:
            st.warning("Needs more data points to draw volume chart. Launch more attacks!")

        # Data Tables
        col_t1, col_t2 = st.columns(2)
        with col_t1:
            st.markdown("### 🚨 Threat Telemetry")
            st.dataframe(df_threats[['Source_IP', 'Strike_Count', 'Time_Gap_Ms', 'Classification']], height=300)
            
        with col_t2:
            st.markdown("### 🧱 Autonomous Firewalls")
            st.dataframe(df_mitigations[['EventID', 'Rule_Applied', 'Latency_Secs']], height=300)
            
        if st.button("🔄 Refresh Dashboard"):
            st.rerun()
