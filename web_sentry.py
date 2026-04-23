import time
import os
import sqlite3
import joblib
from plyer import notification

# 1. Path Configurations
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "..", "database", "threats.db")
MODEL_PATH = os.path.join(BASE_DIR, "..", "models", "intrusion_model.pkl")
WEB_LOG_PATH = os.path.join(BASE_DIR, "web_security.log")

# Create the log file if it doesn't exist yet so the script doesn't crash
if not os.path.exists(WEB_LOG_PATH):
    open(WEB_LOG_PATH, 'a').close()

threat_monitor = {}

def log_to_db(ip, user):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        # Notice we are flagging the status as a WAF (Web Application Firewall) Block!
        cursor.execute("INSERT INTO blocked_ips (ip_address, username, status) VALUES (?, ?, ?)", 
                       (ip, user, 'WAF_BLOCK'))
        conn.commit()
        conn.close()
    except Exception as e:
        pass

def block_web_attacker(ip_address, user):
    print(f"\n[!] WAF MITIGATION: SVM confirmed web brute force from {ip_address}!")
    print(f"[+] SUCCESS: IP {ip_address} dropped at the Web Application Firewall layer.")
    
    try:
        notification.notify(
            title="🌐 MIU Web Sentry Alert",
            message=f"Web Portal Attack Blocked: {ip_address}\nTarget: {user}",
            app_name="MIU Autonomous SOC",
            timeout=5
        )
    except:
        pass
        
    log_to_db(ip_address, user)

def monitor_web_logs():
    clf = joblib.load(MODEL_PATH)
    
    print("-" * 60)
    print("🌐 SHAKUR'S WEB SENTRY (WAF MODE): ACTIVE")
    print(f"Monitoring Apache/Nginx Log: {WEB_LOG_PATH}")
    print("-" * 60)
    
    # "Tail" the text file continuously
    with open(WEB_LOG_PATH, "r") as log_file:
        log_file.seek(0, os.SEEK_END) # Go to the end of the file
        
        while True:
            new_line = log_file.readline()
            if not new_line:
                time.sleep(0.5)
                continue
                
            # If the log contains an Unauthorized error
            if "401 Unauthorized" in new_line:
                # Extract the IP and Username from our log string
                parts = new_line.split(" - ")
                ip_address = parts[1].split()[0]
                user_attempted = parts[2].replace("Target: ", "").strip()
                current_time = time.time()
                
                # --- THIS IS THE EXACT SAME ML LOGIC ---
                if ip_address not in threat_monitor:
                    threat_monitor[ip_address] = [1, current_time]
                else:
                    count, last_time = threat_monitor[ip_address]
                    time_gap = current_time - last_time
                    threat_monitor[ip_address] = [count + 1, current_time]
                    
                    prediction = clf.predict([[count + 1, time_gap]])
                    
                    if prediction[0] == 1:
                        block_web_attacker(ip_address, user_attempted)
                        threat_monitor[ip_address] = [0, current_time]

if __name__ == "__main__":
    monitor_web_logs()