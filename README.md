# HookCatcher AI 🛡️

**HookCatcher AI** is an advanced Gmail security extension designed to detect phishing attempts and malicious content using AI-driven analysis.

## Key Features
- **AI Verdicts:** Uses Gemini 2.5 Flash to analyze email context and language.
- **Link Scanning:** Integrates with VirusTotal API to verify suspicious URLs.
- **SOC-Grade Insights:** Provides clear, actionable security reports directly in your browser.

## Tech Stack
- **Frontend:** JavaScript (Chrome Extension API), HTML/CSS.
- **Backend:** Python (Flask), Google Gmail API, Google Generative AI.

## How it Works
The extension captures the email content, sends it to a secure Python backend, which then queries security databases and AI models to provide a final safety score.

## Status
Extension is currently under review in the Chrome Web Store. Backend is deployed on Google Cloud Run.