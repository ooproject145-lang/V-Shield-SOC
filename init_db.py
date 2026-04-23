import sqlite3

def setup_database():
    # This creates a single file that is 100% portable to any laptop
    conn = sqlite3.connect('threats.db')
    cursor = conn.cursor()
    
    # Create a table to store attacks
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS blocked_ips (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ip_address TEXT,
            username TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            status TEXT
        )
    ''')
    
    conn.commit()
    conn.close()
    print("[+] Database 'threats.db' initialized and ready for transfer.")

if __name__ == "__main__":
    setup_database()