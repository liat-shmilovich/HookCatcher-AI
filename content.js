// content.js
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === "triggerShowOriginal") {
        
        // שלב 1: מציאת כפתור ה-3 נקודות
        const moreBtn = document.querySelector('.adn.ads [aria-label*="More"], .adn.ads [data-tooltip*="More"]');
        
        if (!moreBtn) {
            sendResponse({ error: "Could not find the 3-dots button." });
            return;
        }

        moreBtn.click();

        // שלב 2: מציאת הכתובת (URL) ושליחה ל-Background
        setTimeout(() => {
            const allLinks = Array.from(document.querySelectorAll('a'));
            const originalLink = allLinks.find(a => 
                (a.href && a.href.includes("view=om")) || 
                a.innerText.includes("Show original") || 
                a.innerText.includes("הצגת המקור")
            );

            if (originalLink && originalLink.href) {
                // שולח ל-background.js שיפתח את הטאב
                chrome.runtime.sendMessage({ action: "openTabDirectly", url: originalLink.href });
                sendResponse({ success: true });
            } else {
                sendResponse({ error: "Could not find 'Show original' link in the menu." });
            }
        }, 700);
    }
    return true;
});