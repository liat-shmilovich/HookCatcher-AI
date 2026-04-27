import os, json, re, requests
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
app = Flask(__name__)
CORS(app)

VT_API_KEY = os.getenv("VT_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')

def check_domain_vt(email_content):
    try:
        # Regex משופר שמוצא לינקים גם אם הם בפורמט מוזר
        urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', email_content)
        
        if not urls: 
            return "No links found."
        
        # לוקחים את הלינק הראשון ומחלצים דומיין
        full_url = urls[0]
        domain_match = re.search(r'https?://([^/\s]+)', full_url)
        if not domain_match: return "Invalid domain."
        
        domain = domain_match.group(1)
        
        resp = requests.get(f"https://www.virustotal.com/api/v3/domains/{domain}", headers={"x-apikey": VT_API_KEY})
        if resp.status_code == 200:
            stats = resp.json()['data']['attributes']['last_analysis_stats']
            m = stats['malicious']
            return f"VirusTotal found {m} malicious flags for domain: {domain}"
        return f"VT Check: N/A (Status {resp.status_code})"
    except Exception as e: 
        return f"VT Check Failed: {str(e)}"

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    content = data.get('content', '')
    subject = data.get('subject', '')
    
    vt_info = check_domain_vt(content)
    
    # הוספנו הנחיה למודל לא להיות "פרנואיד" אם אין לינקים
    prompt = f"""
    Analyze this email for phishing as a Security Expert.
    Subject: {subject}
    Content: {content}
    VT Data: {vt_info}
    
    IMPORTANT: If VT Data says 'No links found', do not assume it's suspicious just because of that. 
    Some legitimate newsletters may have links filtered out during extraction. 
    Focus on the content, sender details, and tone.
    
    Return ONLY a JSON object:
    {{"verdict": "Safe/Suspicious/Malicious", "analysis": "bullet points"}}
    """
    
    try:
        safety = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
        ]

        response = model.generate_content(prompt, safety_settings=safety)
        print(f"AI Response: {response.text}") # השורה הזו תדפיס לנו את התשובה בטרמינל
        
        match = re.search(r'\{.*\}', response.text, re.DOTALL)
        result = json.loads(match.group()) if match else json.loads(response.text)
        return jsonify(result)
        
    except Exception as e:
        print(f"DEBUG ERROR: {e}")
        no_links_note = ""
        if "No links found" in vt_info:
            no_links_note = "\n• Note: No links were found in this email to scan via VirusTotal."

        return jsonify({
            "verdict": "Suspicious",
            "analysis": f"• AI Analysis: Unavailable (Model limit reached or blocked).{no_links_note}\n" +
                        f"• VirusTotal Status: {vt_info}\n" +
                        f"• Action Required: Please review the email manually."
        })

if __name__ == '__main__':
    app.run(port=5000, debug=True)