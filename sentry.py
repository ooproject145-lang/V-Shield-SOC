import win32evtlog
import subprocess
import sqlite3
import time
import os
import joblib  
from plyer import notification # UPGRADE 1: Modern Windows Notifications (Python 3.14 Compatible)

# 1. Path Configurations for Portability
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "..", "database", "threats.db")
MODEL_PATH = os.path.join(BASE_DIR, "..", "models", "intrusion_model.pkl")

# 2. Global State & Services
threat_monitor = {}  

def log_to_db(ip, user):
    """Saves the autonomous mitigation to the portable SQLite database"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO blocked_ips (ip_address, username, status) VALUES (?, ?, ?)", 
                       (ip, user, 'BLOCKED'))
        conn.commit()
        conn.close()
        print(f"[+] Record permanently saved to threats.db")
    except Exception as e:
        print(f"[!] Database Error: {e}")

def block_ip(ip_address, user):
    """The Autonomous Response Module: Executes Netsh Firewall Rules"""
    print(f"[!] MITIGATION: SVM confirmed threat. Neutralizing {ip_address}...")
    
    cmd = f'netsh advfirewall firewall add rule name="Block_Attacker_{ip_address}" dir=in action=block remoteip={ip_address}'
    
    try:
        subprocess.run(cmd, shell=True, check=True)
        print(f"[+] SUCCESS: Firewall rule created for {ip_address}.")
        
        # UPGRADE 1: Trigger the visual Windows notification safely
        try:
            notification.notify(
                title="🛡️ MIU Sentry Alert",
                message=f"Brute Force Blocked: {ip_address}\nTarget: {user}",
                app_name="MIU Autonomous SOC",
                timeout=5
            )
        except Exception as notify_err:
            print(f"[*] Notification suppressed: {notify_err}")
            
        log_to_db(ip_address, user)
    except subprocess.CalledProcessError:
        print("[!] ERROR: Admin privileges required to modify Firewall.")

def monitor_and_respond():
    if not os.path.exists(MODEL_PATH):
        print(f"[!] ERROR: SVM Model not found at {MODEL_PATH}. Run train_model.py first!")
        return

    clf = joblib.load(MODEL_PATH)
    server = 'localhost'
    log_type = 'Security'
    
    print("-" * 60)
    print("🛡️ SHAKUR'S AUTONOMOUS SVM DEFENSE SYSTEM: ACTIVE")
    print(f"Targeting: Windows Event ID 4625 | Response Goal: < 2.5s")
    print("-" * 60)
    
    while True:
        try:
            hand = win32evtlog.OpenEventLog(server, log_type)
            flags = win32evtlog.EVENTLOG_BACKWARDS_READ | win32evtlog.EVENTLOG_SEQUENTIAL_READ
            events = win32evtlog.ReadEventLog(hand, flags, 0)
            
            if events:
                for event in events:
                    if event.EventID == 4625:
                        user_attempted = event.StringInserts[5]
                        current_time = time.time()
                        
                        if user_attempted not in threat_monitor:
                            threat_monitor[user_attempted] = [1, current_time]
                        else:
                            count, last_time = threat_monitor[user_attempted]
                            time_gap = current_time - last_time
                            threat_monitor[user_attempted] = [count + 1, current_time]
                            
                            prediction = clf.predict([[count + 1, time_gap]])
                            
                            if prediction[0] == 1:
                                block_ip("192.168.1.100", user_attempted)
                                threat_monitor[user_attempted] = [0, current_time]
            
            win32evtlog.CloseEventLog(hand)
            
        except Exception as e:
            print(f"[!] Log Reading Error: {e}")
            
        time.sleep(5) 

if __name__ == "__main__":
    try:
        monitor_and_respond()
    except KeyboardInterrupt:
        print("\n[-] Sentry Deactivated.")