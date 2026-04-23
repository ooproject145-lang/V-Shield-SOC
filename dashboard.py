import streamlit as st
import pandas as pd
import numpy as np
import datetime
import sqlite3
import time

# 1. Enterprise Page Configuration
st.set_page_config(page_title="V-Shield Autonomous SOC", page_icon="🛡️", layout="wide", initial_sidebar_state="collapsed")

# 2. Database Initialization
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
tab_honeypot, tab_dashboard = st.tabs(["🕸️ TARGET: MIU Intranet", "🛡️ DEFENDER: SOC Command Center"])

# ==========================================
# ENVIRONMENT 1: THE ATTACKER'S HONEYPOT
# ==========================================
with tab_honeypot:
    st.markdown("<br><h1 style='text-align: center; color: #38bdf8;'>MIU Secure Intranet</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #94a3b8; font-size: 18px;'>Authorized Personnel Only</p><br>", unsafe_allow_html=True)
    
    col_left, col_mid, col_right = st.columns([1, 1.5, 1])
    
    with col_mid:
        # The Manual Login
        with st.form("login_form"):
            username = st.text_input("Employee ID", placeholder="Enter your ID...")
            password = st.text_input("Password", type="password", placeholder="Enter your password...")
            submitted = st.form_submit_button("AUTHENTICATE TO NETWORK", use_container_width=True)
            
            if submitted:
                if username == "admin" and password == "MIU2026":
                    st.success("🎉 CONGRATULATIONS! You are an authentic user.")
                else:
                    st.error("❌ ACCESS DENIED. Unauthorized activity detected and logged.")
                    
                    # Log Manual Threat
                    conn = sqlite3.connect('threats.db')
                    c = conn.cursor()
                    attacker_ip = f"192.168.1.{np.random.randint(50, 200)}"
                    ts = datetime.datetime.now()
                    c.execute("INSERT INTO Threat_Telemetry (Source_IP, Timestamp, Strike_Count, Time_Gap_Ms, Classification) VALUES (?, ?, ?, ?, ?)",
                              (attacker_ip, ts, np.random.randint(2, 5), np.random.uniform(500, 1200), "Suspicious (Manual)"))
                    event_id = c.lastrowid
                    time.sleep(0.8)
                    c.execute("INSERT INTO Mitigation_Actions (EventID, Rule_Applied, Latency_Secs, Timestamp) VALUES (?, ?, ?, ?)",
                              (event_id, "WAF Drop (Autonomous)", np.random.uniform(0.5, 1.2), ts))
                    conn.commit()
                    conn.close()
                    st.toast(f"Manual Intrusion from {attacker_ip} blocked!", icon="🚨")

        st.markdown("---")
        
        # The Advanced Attack Simulator
        with st.expander("☠️ ADVANCED: Launch Automated Attack Script"):
            st.warning("This simulates a high-speed Hydra Brute-Force attack against the portal.")
            if st.button("🚀 Execute Brute-Force Payload", type="primary", use_container_width=True):
                with st.status("Executing payload...", expanded=True) as status:
                    conn = sqlite3.connect('threats.db')
                    c = conn.cursor()
                    target_ip = f"45.33.22.{np.random.randint(10, 99)}"
                    
                    st.write(f"Initializing connection to target via {target_ip}...")
                    time.sleep(1)
                    
                    # Rapid fire 8 attacks
                    for i in range(1, 9):
                        ts = datetime.datetime.now()
                        gap = np.random.uniform(10, 45) # Super fast time gap
                        latency = np.random.uniform(0.1, 0.4) # Instant block
                        
                        st.write(f"Attempt {i}: [FAILED] - Injecting packet... Latency {gap:.2f}ms")
                        
                        c.execute("INSERT INTO Threat_Telemetry (Source_IP, Timestamp, Strike_Count, Time_Gap_Ms, Classification) VALUES (?, ?, ?, ?, ?)",
                                  (target_ip, ts, 15+i, gap, "Malicious (Automated Script)"))
                        ev_id = c.lastrowid
                        c.execute("INSERT INTO Mitigation_Actions (EventID, Rule_Applied, Latency_Secs, Timestamp) VALUES (?, ?, ?, ?)",
                                  (ev_id, "IPTables Hard Block", latency, ts))
                        time.sleep(0.3) # UI delay for visual effect
                        
                    conn.commit()
                    conn.close()
                    status.update(label="Payload execution complete. Connection terminated by target firewall.", state="complete", expanded=False)
                st.toast("Automated Attack Neutralized! Check the Dashboard.", icon="✅")

# ==========================================
# ENVIRONMENT 2: THE DEFENDER'S DASHBOARD
# ==========================================
with tab_dashboard:
    col_title, col_refresh = st.columns([4, 1])
    with col_title:
        st.title("🛡️ V-Shield Autonomous SOC")
        st.markdown("##### Global Threat Telemetry & Mitigation Dashboard")
    with col_refresh:
        st.write("") # Spacing
        if st.button("🔄 Refresh Telemetry", use_container_width=True):
            st.rerun()

    st.markdown("---")

    # Load Data dynamically
    conn = sqlite3.connect('threats.db')
    df_threats = pd.read_sql_query("SELECT * FROM Threat_Telemetry ORDER BY Timestamp DESC", conn)
    df_mitigations = pd.read_sql_query("SELECT * FROM Mitigation_Actions ORDER BY Timestamp DESC", conn)
    conn.close()

    if df_threats.empty:
        st.info("🟢 System is online. Awaiting intrusion events... (Go to the Target Portal tab and launch an attack!)")
    else:
        # Live KPI Metrics
        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        col_m1.metric("Intrusions Logged", len(df_threats), delta="Live")
        col_m2.metric("Threats Blocked", len(df_mitigations), delta="100% Success")
        avg_latency = df_mitigations['Latency_Secs'].mean() if not df_mitigations.empty else 0.0
        col_m3.metric("Avg Mitigation Latency", f"{avg_latency:.2f}s", delta="Sub-Second", delta_color="inverse")
        col_m4.metric("SVM Accuracy Status", "Active", "Nominal")

        st.markdown("---")

        # Forensic Export Feature
        csv_data = df_threats.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Forensic Incident Report (CSV)",
            data=csv_data,
            file_name=f"V-Shield_Forensics_{datetime.datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
        )
        st.write("") # Spacing

        # Data Tables
        col_t1, col_t2 = st.columns(2)
        with col_t1:
            st.markdown("### 🚨 Threat Telemetry (SVM Engine)")
            st.dataframe(df_threats[['Source_IP', 'Strike_Count', 'Time_Gap_Ms', 'Classification']], height=400, use_container_width=True)
            
        with col_t2:
            st.markdown("### 🧱 Autonomous Firewalls")
            st.dataframe(df_mitigations[['EventID', 'Rule_Applied', 'Latency_Secs']], height=400, use_container_width=True)
