document.addEventListener('DOMContentLoaded', function () {
    const analyzeBtn = document.getElementById('analyzeBtn');
    const statusDiv = document.getElementById('status');

    if (analyzeBtn) {
        analyzeBtn.addEventListener('click', async () => {
            statusDiv.innerText = "Scanning screen content... Please wait";
            statusDiv.style.color = "#3498db";

            try {
                let [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

                // הזרקת קוד לחילוץ טקסט מהדף
                const results = await chrome.scripting.executeScript({
                    target: { tabId: tab.id },
                    func: () => {
                        // חילוץ גוף המייל ונושא המייל מה-DOM של Gmail
                        const bodyElement = document.querySelector('.a3s.aiL') || document.querySelector('.ii.gt');
                        const subjectElement = document.querySelector('h2.hP');
                        
                        return { 
                            body: bodyElement ? bodyElement.innerText : document.body.innerText, 
                            subject: subjectElement ? subjectElement.innerText : "No Subject Found" 
                        };
                    }
                });

                const { body, subject } = results[0].result;

                // שליחה לשרת
                const response = await fetch('http://127.0.0.1:5000/analyze', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ 
                        full_content: body, 
                        subject: subject 
                    })
                });

                const data = await response.json();
                
                if (data.result) {
                    statusDiv.innerText = data.result;
                    statusDiv.style.color = "#2c3e50";
                } else {
                    statusDiv.innerText = "Error: " + (data.error || "Server issue");
                }

            } catch (error) {
                console.error(error);
                statusDiv.innerText = "Error: Make sure the server is running and the email is open.";
                statusDiv.style.color = "#e74c3c";
            }
        });
    }
});