# PV Sentinel MVP
## Local AI Assistant for Pharmacovigilance Case Processing and Narrative Generation

![PV Sentinel Logo](docs/logo.png)

**Version:** 1.0.0-MVP  
**License:** Open Core (Base features free, Enterprise features licensed)  
**Compliance:** GxP-ready, GAMP 5 aligned, GVP VI/IX compliant

---

## 🎯 Overview

PV Sentinel is a locally deployable, privacy-first AI tool designed to support pharmacovigilance (PV) professionals in drafting adverse event (AE) narratives, structuring case reports, and ensuring compliance with GVP and FDA reporting standards. Built on open-source, resource-efficient models, it supports regulatory workflows without cloud reliance.

### 🔑 Key Features

- **🛡️ Patient-Centric Safety**: Advanced patient context preservation ensures no loss of critical safety information
- **🔍 Model Transparency**: Complete audit trail with model version tracking and prompt locking
- **🎙️ Voice Confirmation**: Smart readback system prevents transcription errors
- **👥 Multi-User Workflows**: Role-based access for collaborative safety assessments
- **📋 GxP Compliance**: GAMP 5 aligned with IQ/OQ/PQ validation protocols
- **🔒 Privacy-First**: 100% local processing - no cloud dependencies

---

## 🚨 Critical Safety Features (P0)

Based on our comprehensive multi-perspective assessment, these features are **CRITICAL** for patient safety:

### 1. Patient Context Preservation
- **Risk Addressed**: AI paraphrasing erasing critical patient nuance
- **Solution**: Dedicated patient voice preservation with validation flags
- **Implementation**: `backend/patient_context.py`

### 2. Model Version Tracking  
- **Risk Addressed**: Cannot reproduce or audit AI-generated content
- **Solution**: Complete model and prompt versioning with hash tracking
- **Implementation**: `backend/model_tracking.py`

### 3. Voice Readback Confirmation
- **Risk Addressed**: Voice capture errors going undetected
- **Solution**: Intelligent readback triggering for safety-critical content
- **Implementation**: `backend/readback.py`

---

## 👥 Multi-Perspective Design

PV Sentinel is designed to meet the needs of all pharmacovigilance stakeholders:

| Persona | Key Benefits | Success Metrics |
|---------|-------------|----------------|
| **PV Officer** | 95% narrative accuracy, edit tracking | 50% time reduction |
| **Regulatory Affairs** | GVP/FAERS compliance, audit trails | 100% submission readiness |
| **Data Privacy** | Local-only processing, GDPR compliance | 0% data breaches |
| **Clinical Ops** | Multi-user workflows, case triage | 75% efficiency gain |
| **QA/Validation** | GAMP 5 alignment, complete audit logs | 100% audit readiness |
| **End Users (HCPs)** | Voice input, readback confirmation | 80% time savings |
| **Patient Advocates** | Voice preservation, context validation | 100% context retention |

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- 8GB RAM minimum (16GB recommended)
- 10GB disk space for models
- Windows 10/11, macOS, or Linux

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-org/pv-sentinel.git
   cd pv-sentinel
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Initialize configuration**
   ```bash
   cp config/config.yaml.example config/config.yaml
   # Edit config.yaml for your environment
   ```

4. **Download models** (First run only)
   ```bash
   python scripts/download_models.py
   ```

5. **Run initial setup**
   ```bash
   python setup.py install
   ```

6. **Start PV Sentinel**
   ```bash
   streamlit run frontend/app.py
   ```

7. **Access the application**
   - Open your browser to `http://localhost:8501`
   - Default login: admin / password123 (change immediately)

---

## 📁 Project Structure

```
pv-sentinel/
├── backend/                 # Core business logic
│   ├── main.py             # Main engine integration
│   ├── patient_context.py  # P0: Patient voice preservation
│   ├── model_tracking.py   # P0: Model version tracking
│   ├── readback.py         # P0: Voice confirmation
│   ├── users.py            # P1: Multi-user support
│   └── triage.py           # P1: Case management
├── frontend/               # Streamlit UI
│   ├── app.py              # Main application
│   ├── components/         # UI components
│   └── pages/              # Application pages
├── config/                 # Configuration
│   └── config.yaml         # Main configuration file
├── prompts/                # Clinical prompt templates
│   ├── narrative_template_anaphylaxis.txt
│   ├── narrative_template_skin_rash.txt
│   └── narrative_template_hepatic_injury.txt
├── models/                 # AI models (downloaded separately)
├── storage/                # Local database and files
├── validation/             # IQ/OQ/PQ protocols
├── tests/                  # Unit and integration tests
├── docs/                   # Documentation
└── requirements.txt        # Python dependencies
```

---

## 🔧 Configuration

The main configuration file is `config/config.yaml`. Key sections:

### Patient Safety Settings (Critical)
```yaml
patient_safety:
  context_preservation: true    # NEVER disable
  voice_confirmation: true      # Recommended for voice input
  narrative_comparison: true    # Compare drafts vs finals
```

### Model Configuration
```yaml
models:
  primary_model: "mistral-7b-instruct"
  model_path: "models/mistral-7b-instruct-v0.1.Q4_K_M.gguf"
  model_hash_tracking: true     # Required for GxP
```

### User Management
```yaml
users:
  multi_user_support: true
  role_based_access: true
  roles: [drafter, reviewer, auditor, admin]
```

---

## 👥 User Roles & Permissions

| Role | Create Cases | Review | Audit | Export | Admin |
|------|-------------|--------|-------|--------|-------|
| **Drafter** | ✅ | ❌ | ❌ | ✅ | ❌ |
| **Reviewer** | ✅ | ✅ | ❌ | ✅ | ❌ |
| **Auditor** | ❌ | ✅ | ✅ | ✅ | ❌ |
| **Admin** | ✅ | ✅ | ✅ | ✅ | ✅ |

---

## 🔍 Validation & Compliance

### GAMP 5 Validation

PV Sentinel includes complete validation protocols:

- **IQ (Installation Qualification)**: `validation/IQ_protocol.md`
- **OQ (Operational Qualification)**: `validation/OQ_protocol.md`  
- **PQ (Performance Qualification)**: `validation/PQ_protocol.md`

### GxP Compliance Features

- ✅ Audit trail for all user actions
- ✅ Electronic signatures (planned)
- ✅ Change control documentation
- ✅ User access controls
- ✅ Data integrity measures
- ✅ Backup and recovery procedures

### Regulatory Alignment

- **EMA GVP Module VI/IX**: Narrative structure and completeness validation
- **FDA FAERS**: Field mapping and submission format
- **ICH E2B(R3)**: Future enhancement for XML export

---

## 🧪 Testing

Run the test suite to ensure system integrity:

```bash
# Run all tests
python -m pytest tests/

# Run specific test categories
python -m pytest tests/test_patient_context.py  # P0 Critical
python -m pytest tests/test_model_tracking.py   # P0 Critical
python -m pytest tests/test_readback.py         # P0 Critical

# Run validation tests
python -m pytest tests/validation/
```

---

## 📊 Performance Metrics

### Target Performance (MVP)
- **Response Time**: < 2 seconds for narrative generation
- **Accuracy**: > 95% for voice transcription
- **Uptime**: > 99.9% availability
- **Concurrent Users**: Up to 10 simultaneous sessions

### Patient Safety Metrics
- **Context Preservation**: 100% (never allow degradation)
- **Voice Confirmation**: Available for all voice inputs
- **Audit Completeness**: 100% traceability

---

## 🔐 Security & Privacy

### Data Protection
- **Local Processing**: No data leaves your environment
- **Encryption**: At-rest and in-transit encryption
- **Access Control**: Role-based permissions
- **Audit Logging**: Complete user action tracking

### GDPR Compliance
- **Data Minimization**: Only collect necessary data
- **Consent Tracking**: Voice vs typed input consent
- **Right to Erasure**: Data retention policies
- **Privacy by Design**: Built-in privacy protection

---

## 🆘 Troubleshooting

### Common Issues

**Voice input not working**
```bash
# Check microphone permissions
python scripts/test_audio.py
```

**Model loading errors**
```bash
# Verify model files
python scripts/verify_models.py
```

**Performance issues**
```bash
# Check system resources
python scripts/system_check.py
```

### Support Channels

- 📧 **Email**: support@pv-sentinel.com
- 📖 **Documentation**: [docs.pv-sentinel.com](https://docs.pv-sentinel.com)
- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/your-org/pv-sentinel/issues)
- 💬 **Community**: [PV Sentinel Forum](https://forum.pv-sentinel.com)

---

## 🗺️ Roadmap

### Phase 1: MVP (Current)
- ✅ Core narrative generation
- ✅ Patient context preservation
- ✅ Voice readback confirmation
- ✅ Multi-user support
- ✅ Basic audit trail

### Phase 2: Enhanced Workflow (Q2 2024)
- 🔄 Case triage and assignment
- 🔄 Advanced edit tracking
- 🔄 Integration APIs
- 🔄 Enhanced reporting

### Phase 3: Advanced Features (Q3 2024)
- 🔄 PSUR module integration
- 🔄 E2B(R3) XML export
- 🔄 Advanced analytics
- 🔄 Machine learning improvements

---

## 📋 Requirements

### System Requirements
- **CPU**: 4+ cores recommended
- **RAM**: 8GB minimum, 16GB recommended
- **Storage**: 10GB for models and data
- **Network**: None required (fully offline capable)

### Software Dependencies
- Python 3.8+
- PyTorch (CPU version)
- Streamlit
- LangChain
- ChromaDB
- See `requirements.txt` for complete list

---

## 🤝 Contributing

We welcome contributions from the pharmacovigilance community!

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

### Development Guidelines
- Follow PEP 8 style guidelines
- Include tests for all new features
- Update documentation
- Ensure patient safety features are never degraded

---

## 📄 License

PV Sentinel uses an **Open Core** model:

- **Core Features**: MIT License (free for all users)
- **Enterprise Features**: Commercial license required
- **Validation Package**: Available with enterprise license

For licensing questions, contact: licensing@pv-sentinel.com

---

## 🙏 Acknowledgments

PV Sentinel was developed with input from:

- Pharmacovigilance professionals
- Regulatory affairs experts
- Patient safety advocates
- Healthcare IT specialists
- Open source contributors

Special thanks to the pharmacovigilance community for their guidance on patient-centric design and regulatory compliance requirements.

---

## ⚠️ Important Disclaimers

1. **Not a Medical Device**: PV Sentinel is a drafting assistant, not an autonomous decision-making system
2. **Human Oversight Required**: All AI-generated content must be reviewed by qualified professionals
3. **Validation Required**: Complete IQ/OQ/PQ validation must be performed before production use
4. **Local Deployment**: Designed for local/on-premises deployment only

**For production use in regulated environments, please contact our validation team for implementation support.**

---

*Last updated: 2024-01-04*  
*Version: 1.0.0-MVP* 