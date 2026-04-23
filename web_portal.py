from flask import Flask, request, render_template_string
import logging

app = Flask(__name__)

# 1. Configure the Web Server to log attacks to a text file
logging.basicConfig(filename='web_security.log', level=logging.INFO, 
                    format='%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

# 2. The sleek HTML/CSS for the SME Login Page with the new Success View
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>MIU SME Portal</title>
    <style>
        body { background-color: #0f172a; color: white; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
        .login-box { background-color: #1e293b; padding: 40px; border-radius: 12px; box-shadow: 0 10px 30px rgba(0,0,0,0.8); text-align: center; border: 1px solid #38bdf8; width: 350px; }
        input { display: block; width: 90%; margin: 15px auto; padding: 12px; border-radius: 6px; border: none; background: #0f172a; color: white; border: 1px solid #334155; }
        button { background: linear-gradient(90deg, #0284c7 0%, #38bdf8 100%); color: white; padding: 12px 24px; border: none; border-radius: 6px; font-weight: bold; cursor: pointer; width: 98%; margin-top: 10px; }
        button:hover { opacity: 0.9; }
        .success-text { color: #10b981; margin-top: 20px; font-size: 1.5rem; font-weight: bold; letter-spacing: 1px;}
    </style>
</head>
<body>
    <div class="login-box">
        {% if success %}
            <svg width="120" height="120" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" style="margin-bottom: 10px;">
                <path d="M14 9V5a3 3 0 0 0-3-3l-4 9v11h11.28a2 2 0 0 0 2-1.7l1.38-9a2 2 0 0 0-2-2.3zM7 22H4a2 2 0 0 1-2-2v-7a2 2 0 0 1 2-2h3"></path>
            </svg>
            <div class="success-text">🎉 CONGRATULATIONS! 🎉</div>
            <p style="color: #cbd5e1; font-size: 1.1rem; line-height: 1.5;">You are an authentic user.<br>Welcome to the secure MIU test environment! 😊</p>
            <button onclick="window.location.href='/'" style="margin-top: 25px; background: #334155;">Return to Login</button>
        {% else %}
            <h2 style="color: #38bdf8;">MIU Secure Intranet</h2>
            <p style="color: #94a3b8; font-size: 14px;">Authorized Personnel Only</p>
            {% if error %}<p style="color: #ef4444; font-weight: bold;">{{ error }}</p>{% endif %}
            <form method="POST">
                <input type="text" name="username" placeholder="Employee ID" required>
                <input type="password" name="password" placeholder="Password" required>
                <button type="submit">AUTHENTICATE</button>
            </form>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def login():
    error = None
    success = False
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        client_ip = request.remote_addr # Capture the attacker's IP

        # Legitimate User Check
        if username == 'admin' and password == 'MIU2026':
            success = True
        else:
            # Failed User Check - Trigger the Sentry!
            error = "ACCESS DENIED. Activity Logged."
            # Write the HTTP 401 Error to the web_security.log file
            app.logger.info(f"{client_ip} HTTP/1.1 401 Unauthorized - Target: {username}")

    return render_template_string(HTML_TEMPLATE, error=error, success=success)

if __name__ == '__main__':
    print("[+] STARTING MIU VULNERABLE WEB PORTAL ON http://127.0.0.1:5000")
    app.run(port=5000, debug=False)