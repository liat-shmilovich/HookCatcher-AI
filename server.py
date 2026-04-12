import os
import re
import requests
import google.generativeai as genai
from flask import Flask, jsonify, request
from flask_cors import CORS
app = Flask(__name__)
CORS(app)

# מפתחות API
VT_API_KEY = os.getenv("VT_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# הגדרת Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')

def check_url_vt(url):
    """בודק קישור ב-VirusTotal ומחזיר סיכום"""
    try:
        # ב-API v3 של VT, צריך לשלוח את ה-URL בפורמט מיוחד או פשוט להשתמש ב-search
        headers = {"x-apikey": VT_API_KEY}
        # קידוד ה-URL לבדיקה
        import base64
        url_id = base64.urlsafe_b64encode(url.encode()).decode().strip("=")
        response = requests.get(f"https://www.virustotal.com/api/v3/urls/{url_id}", headers=headers)
        
        if response.status_code == 200:
            stats = response.json()['data']['attributes']['last_analysis_stats']
            return f"VirusTotal stats for {url}: Malicious: {stats['malicious']}, Suspicious: {stats['suspicious']}, Harmless: {stats['harmless']}"
    except Exception as e:
        return f"Could not scan URL {url} on VirusTotal."
    return None

@app.route('/analyze', methods=['POST'])
def analyze_content():
    try:
        data = request.get_json(force=True, silent=True) or {}
        email_content = data.get('full_content', '')
        subject = data.get('subject', 'No Subject')

        if not email_content:
            return jsonify({"error": "No content received from the extension"}), 400

        # 1. חילוץ קישורים מהטקסט שהגיע מהמסך
        urls = re.findall(r'(https?://[^\s]+)', email_content)
        vt_results = []
        if urls:
            # נסרוק רק את הקישור הראשון כדי לא לחרוג ממכסות מהר מדי
            vt_info = check_url_vt(urls[0])
            if vt_info:
                vt_results.append(vt_info)

        # 2. בניית ה-Prompt לאנליסט
        vt_report = "\n".join(vt_results) if vt_results else "No URLs found or scanned."
        
        prompt = f"""
        Act as a professional SOC Analyst. Analyze the following email content displayed on the user's screen:
        
        Subject: {subject}
        Content: 
        {email_content}
        
        Security Tools Report (VirusTotal):
        {vt_report}
        
        Provide a detailed verdict in Hebrew:
        - Risk Level (Safe/Suspicious/Malicious)
        - Detailed explanation based on content and VT results
        - Recommendations for the user
        """
        
        response = model.generate_content(prompt)
        return jsonify({"result": response.text})

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(port=5000, debug=True)