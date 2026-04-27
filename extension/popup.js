let reportToDownload = "";

document.getElementById('scan-btn').addEventListener('click', async () => {
    const loader = document.getElementById('loader'), resultArea = document.getElementById('result-area');
    const card = document.getElementById('status-container'), shield = document.getElementById('shield-icon');
    
    // ניקוי סטטוס קודם לפני תחילת סריקה חדשה
    loader.classList.remove('hidden');
    resultArea.classList.add('hidden');
    card.className = 'card'; // מאפס את הצבע של המסגרת

    try {
        const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
        const inject = await chrome.scripting.executeScript({
            target: { tabId: tab.id },
            func: () => ({ 
                body: document.querySelector('.a3s')?.innerText || "", 
                subject: document.querySelector('h2.hP')?.innerText || "" 
            })
        });

        const response = await fetch('https://hookcatcher-api-34669240908.us-central1.run.app/analyze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ content: inject[0].result.body })
        });

        const data = await response.json();
        loader.classList.add('hidden');
        resultArea.classList.remove('hidden');

        document.getElementById('verdict-text').innerText = data.verdict;
        document.getElementById('full-analysis').innerText = data.analysis;
        
        reportToDownload = `HookCatcher AI - Security Report\n` +
                           `Verdict: ${data.verdict}\n` +
                           `Date: ${new Date().toLocaleString()}\n` +
                           `--------------------------\n\n` +
                           `${data.analysis}`;
                           
        // עדכון עיצוב לפי התוצאה
        if (data.verdict === 'Malicious') { 
            card.classList.add('status-danger'); 
            shield.innerText = '🛑'; 
        }
        else if (data.verdict === 'Suspicious') { 
            card.classList.add('status-warning'); 
            shield.innerText = '⚠️'; 
        }
        else { 
            card.classList.add('status-safe'); 
            shield.innerText = '🛡️'; 
        }

    } catch (e) {
        loader.classList.add('hidden');
        // הודעה ידידותית יותר במקרה של עומס
        alert("The AI is taking a short break. Please wait 10 seconds and try again.");
    }
});

document.getElementById('download-btn').addEventListener('click', () => {
    if (!reportToDownload) return;
    const blob = new Blob([reportToDownload], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'Security_Report.txt'; 
    a.click();
});

document.getElementById('details-btn').addEventListener('click', () => {
    document.getElementById('details-panel').classList.toggle('hidden');
});