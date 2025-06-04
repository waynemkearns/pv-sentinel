from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
import subprocess
import os
import sys
from pathlib import Path

app = FastAPI()

@app.get("/")
async def root():
    return HTMLResponse(content="""
    <!DOCTYPE html>
    <html>
    <head>
        <title>PV Sentinel - AI-Powered Pharmacovigilance Assistant</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 40px; border-radius: 10px; }
            .header { text-align: center; color: #1f4e79; margin-bottom: 30px; }
            .warning { background: #fff3cd; border: 1px solid #ffeaa7; padding: 20px; border-radius: 5px; margin: 20px 0; }
            .info { background: #d1ecf1; border: 1px solid #bee5eb; padding: 20px; border-radius: 5px; margin: 20px 0; }
            .button { display: inline-block; background: #2e7bcf; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; margin: 10px; }
            .button:hover { background: #1f4e79; }
            .deployment-options { margin: 30px 0; }
            .option { margin: 20px 0; padding: 20px; border: 1px solid #ddd; border-radius: 5px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1 class="header">🏥 PV Sentinel</h1>
            <h2 class="header">AI-Powered Pharmacovigilance Assistant</h2>
            
            <div class="warning">
                <h3>🚨 Deployment Notice</h3>
                <p>PV Sentinel is a <strong>Streamlit Python application</strong> that requires a Python runtime environment. 
                Vercel is optimized for static sites and Node.js applications.</p>
            </div>
            
            <div class="info">
                <h3>📋 Patient Safety Features</h3>
                <ul>
                    <li><strong>Patient Context Preservation</strong> - Prevents AI paraphrasing of critical patient details</li>
                    <li><strong>Model Version Tracking</strong> - Complete audit trail for regulatory compliance</li>
                    <li><strong>Voice Readback Confirmation</strong> - Prevents transcription errors</li>
                </ul>
            </div>
            
            <div class="deployment-options">
                <h3>🚀 Recommended Deployment Options</h3>
                
                <div class="option">
                    <h4>Option 1: Streamlit Community Cloud (Recommended)</h4>
                    <p>Native Streamlit hosting with GitHub integration.</p>
                    <ol>
                        <li>Go to <a href="https://share.streamlit.io/" target="_blank">share.streamlit.io</a></li>
                        <li>Connect your GitHub repository</li>
                        <li>Deploy with main file: <code>frontend/app.py</code></li>
                    </ol>
                </div>
                
                <div class="option">
                    <h4>Option 2: Railway</h4>
                    <p>Python-friendly deployment platform.</p>
                    <ol>
                        <li>Go to <a href="https://railway.app/" target="_blank">railway.app</a></li>
                        <li>Connect your GitHub repository</li>
                        <li>Deploy automatically using the included Procfile</li>
                    </ol>
                </div>
                
                <div class="option">
                    <h4>Option 3: Local Development</h4>
                    <p>Run locally for development and testing.</p>
                    <code>streamlit run frontend/app.py</code>
                </div>
            </div>
            
            <div class="info">
                <h3>📚 Documentation</h3>
                <p>Complete user guide available in the <code>docs/user-guide/</code> directory.</p>
                <p>See <a href="https://github.com/waynemkearns/pv-sentinel" target="_blank">GitHub Repository</a> for full documentation.</p>
            </div>
        </div>
    </body>
    </html>
    """)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "PV Sentinel", "message": "Ready for proper Streamlit deployment"}

@app.get("/docs")
async def redirect_to_docs():
    return RedirectResponse(url="https://github.com/waynemkearns/pv-sentinel/tree/main/docs/user-guide")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 