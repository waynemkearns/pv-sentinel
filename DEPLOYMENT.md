# PV Sentinel Deployment Guide

## 🚀 Deployment Options

PV Sentinel is a **Streamlit Python application** that requires a Python runtime environment. Here are the recommended deployment options:

### Option 1: Streamlit Community Cloud ⭐ (Recommended)

**Best for:** Production deployment of Streamlit applications

**Steps:**
1. Go to [share.streamlit.io](https://share.streamlit.io/)
2. Sign in with GitHub
3. Click "New app"
4. Select your repository: `waynemkearns/pv-sentinel`
5. Set main file path: `frontend/app.py`
6. Click "Deploy"

**URL:** Your app will be available at `https://yourappname.streamlit.app`

**Benefits:**
- Native Streamlit hosting
- Automatic GitHub integration
- Free tier available
- Optimized for Streamlit apps

### Option 2: Railway 🚂

**Best for:** Python applications with custom requirements

**Steps:**
1. Go to [railway.app](https://railway.app/)
2. Sign up and connect GitHub
3. Click "Deploy from GitHub repo"
4. Select `waynemkearns/pv-sentinel`
5. Railway will automatically use the `Procfile` for deployment

**Benefits:**
- Supports Python/Streamlit natively
- Automatic deployments from GitHub
- Database add-ons available
- Generous free tier

### Option 3: Vercel (Current) ℹ️

**Status:** Currently shows informational page

**What it does:**
- Displays project information
- Explains deployment options
- Redirects to proper hosting platforms

**URL:** [pv-sentinel.vercel.app](https://pv-sentinel.vercel.app)

**Note:** Vercel is optimized for static sites and Node.js. While we've created a FastAPI wrapper for information display, the full Streamlit application requires a Python runtime.

### Option 4: Local Development 💻

**Best for:** Development and testing

**Steps:**
1. Clone the repository
2. Install requirements: `pip install -r requirements.txt`
3. Run: `streamlit run frontend/app.py`
4. Open: http://localhost:8501

## 🏥 Application Features

### Patient Safety First
- **Patient Context Preservation** - Prevents AI paraphrasing of critical patient details
- **Model Version Tracking** - Complete audit trail for regulatory compliance  
- **Voice Readback Confirmation** - Prevents transcription errors

### User Interfaces
- **Dashboard** - System status and metrics
- **Case Entry** - New adverse event recording
- **Case Review** - Multi-user review workflows
- **Documentation** - Complete user guide access

### Technical Capabilities
- Multi-user support with role-based access
- Local processing for data privacy
- Regulatory compliance (GVP, FAERS, 21 CFR Part 11)
- Complete audit trails for GAMP 5 validation

## 📋 Quick Start After Deployment

1. **Access the application** at your deployment URL
2. **Navigate to "New Case Entry"** to create your first adverse event case
3. **Use voice input** for accurate patient story capture
4. **Review patient context preservation** - ensure patient voice is maintained
5. **Generate AI narrative** with complete audit trail
6. **Access documentation** for detailed user guides

## 🛠️ Configuration

The application uses:
- **Configuration:** `config/config.yaml`
- **Streamlit settings:** `.streamlit/config.toml`
- **Requirements:** `requirements.txt`
- **Frontend:** `frontend/app.py`

## 📚 Documentation

- Complete user guide: `docs/user-guide/README.md`
- Executive summary: `docs/user-guide/01_executive_summary.md`
- Quick start guides: `docs/user-guide/02_quick_start_guides.md`
- Safety features: `docs/user-guide/13_safety_features.md`

## 🆘 Support

For deployment issues:
1. Check the platform-specific documentation
2. Verify Python requirements are met
3. Ensure all dependencies are available
4. Review the troubleshooting guide in `docs/user-guide/21_troubleshooting.md`

---

**Patient safety was prioritized throughout the development of this deployment guide. Always ensure critical safety features are operational before processing real patient data.** 