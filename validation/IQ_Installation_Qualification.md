# PV Sentinel - Installation Qualification (IQ) Protocol

**Document ID:** PVS-IQ-001  
**Version:** 1.0  
**Date:** 2024-01-04  
**Classification:** GxP Critical  

---

## 1. PURPOSE AND SCOPE

### 1.1 Purpose
This Installation Qualification (IQ) protocol establishes documented evidence that PV Sentinel has been installed according to written procedures and that all hardware and software components are properly configured and functioning as intended.

### 1.2 Scope
This IQ covers:
- Software installation verification
- Hardware requirement validation
- Configuration file setup
- Initial system functionality testing
- Critical safety feature activation
- Audit trail initialization

### 1.3 Regulatory Compliance
This protocol aligns with:
- **GAMP 5**: Good Automated Manufacturing Practice
- **FDA 21 CFR Part 11**: Electronic Records and Signatures
- **EMA Annex 11**: Computerised Systems
- **GVP Module VI**: Management and reporting of adverse reactions

---

## 2. RESPONSIBILITIES

| Role | Responsibility |
|------|---------------|
| **System Administrator** | Execute installation procedures, system configuration |
| **QA Representative** | Review and approve protocol, witness testing |
| **IT Security** | Validate security configurations, access controls |
| **Validation Manager** | Overall protocol oversight and final approval |

---

## 3. PREREQUISITES

### 3.1 Hardware Requirements
- [ ] CPU: Minimum 4 cores, 2.5 GHz
- [ ] RAM: Minimum 8GB, 16GB recommended
- [ ] Storage: Minimum 20GB free space
- [ ] Network: Local network access (internet not required)
- [ ] Audio: Microphone and speakers for voice functionality

### 3.2 Software Prerequisites
- [ ] Operating System: Windows 10/11, macOS 10.15+, or Linux (Ubuntu 20.04+)
- [ ] Python 3.8 or higher
- [ ] Administrator/root access for installation
- [ ] Antivirus software configured to exclude PV Sentinel directories

### 3.3 Documentation
- [ ] PV Sentinel Installation Manual
- [ ] System Configuration Guide
- [ ] User Requirements Specification (URS)
- [ ] This IQ Protocol approved and signed

---

## 4. INSTALLATION PROCEDURES

### 4.1 Pre-Installation Checklist

| Step | Requirement | Pass/Fail | Comments | Initials |
|------|-------------|-----------|----------|----------|
| 1 | Hardware requirements met | ☐ Pass ☐ Fail | | |
| 2 | Software prerequisites installed | ☐ Pass ☐ Fail | | |
| 3 | Installation directory available (20GB) | ☐ Pass ☐ Fail | | |
| 4 | User account with admin privileges | ☐ Pass ☐ Fail | | |
| 5 | Backup of existing system (if upgrade) | ☐ Pass ☐ Fail | N/A for new install | |

### 4.2 Software Installation

| Step | Action | Expected Result | Pass/Fail | Comments | Initials |
|------|--------|-----------------|-----------|----------|----------|
| 1 | Extract PV Sentinel package to target directory | Files extracted without errors | ☐ Pass ☐ Fail | | |
| 2 | Run `pip install -r requirements.txt` | All dependencies installed successfully | ☐ Pass ☐ Fail | | |
| 3 | Execute `python setup.py install` | Installation completes without errors | ☐ Pass ☐ Fail | | |
| 4 | Verify installation with `python -c "import backend.main"` | No import errors | ☐ Pass ☐ Fail | | |
| 5 | Create initial configuration from template | `config/config.yaml` created | ☐ Pass ☐ Fail | | |

### 4.3 Critical Safety Feature Verification

**CRITICAL**: These features are essential for patient safety and MUST be enabled.

| Feature | Configuration Setting | Expected Value | Verified | Comments | Initials |
|---------|----------------------|----------------|----------|----------|----------|
| Patient Context Preservation | `patient_safety.context_preservation` | `true` | ☐ Pass ☐ Fail | NEVER disable | |
| Model Version Tracking | `validation.model_hash_tracking` | `true` | ☐ Pass ☐ Fail | Required for GxP | |
| Voice Readback | `stt.enable_readback` | `true` | ☐ Pass ☐ Fail | Safety critical | |
| Audit Trail | `system.audit_mode` | `true` | ☐ Pass ☐ Fail | Regulatory requirement | |
| Multi-user Support | `users.multi_user_support` | `true` | ☐ Pass ☐ Fail | Required for workflows | |

---

## 5. SYSTEM CONFIGURATION VERIFICATION

### 5.1 Database Initialization

| Step | Action | Expected Result | Pass/Fail | Comments | Initials |
|------|--------|-----------------|-----------|----------|----------|
| 1 | Initialize SQLite database | Database file created in `storage/` | ☐ Pass ☐ Fail | | |
| 2 | Create initial tables | All required tables present | ☐ Pass ☐ Fail | | |
| 3 | Verify backup settings | Daily backup configured | ☐ Pass ☐ Fail | | |
| 4 | Test database connectivity | Connection successful | ☐ Pass ☐ Fail | | |

### 5.2 Model and Template Registration

| Step | Action | Expected Result | Pass/Fail | Comments | Initials |
|------|--------|-----------------|-----------|----------|----------|
| 1 | Download required AI models | Models present in `models/` directory | ☐ Pass ☐ Fail | | |
| 2 | Verify model hash calculation | Hash generated and stored | ☐ Pass ☐ Fail | | |
| 3 | Register prompt templates | All templates in model registry | ☐ Pass ☐ Fail | | |
| 4 | Lock critical templates | Production templates locked | ☐ Pass ☐ Fail | | |

### 5.3 User Management Setup

| Step | Action | Expected Result | Pass/Fail | Comments | Initials |
|------|--------|-----------------|-----------|----------|----------|
| 1 | Create default admin user | Admin account active | ☐ Pass ☐ Fail | Change default password | |
| 2 | Configure role permissions | All roles properly defined | ☐ Pass ☐ Fail | | |
| 3 | Test session management | Sessions created and expired properly | ☐ Pass ☐ Fail | | |
| 4 | Verify access controls | Permissions enforced correctly | ☐ Pass ☐ Fail | | |

---

## 6. FUNCTIONAL TESTING

### 6.1 Basic System Functions

| Test Case | Procedure | Expected Result | Pass/Fail | Comments | Initials |
|-----------|-----------|-----------------|-----------|----------|----------|
| TC-IQ-001 | Start PV Sentinel application | Application starts without errors | ☐ Pass ☐ Fail | | |
| TC-IQ-002 | Access web interface | Login page displayed | ☐ Pass ☐ Fail | | |
| TC-IQ-003 | Login with admin credentials | Dashboard displayed | ☐ Pass ☐ Fail | | |
| TC-IQ-004 | Navigate between pages | All pages load correctly | ☐ Pass ☐ Fail | | |
| TC-IQ-005 | Logout and session termination | User logged out, session cleared | ☐ Pass ☐ Fail | | |

### 6.2 Critical Safety Function Tests

| Test Case | Procedure | Expected Result | Pass/Fail | Comments | Initials |
|-----------|-----------|-----------------|-----------|----------|----------|
| TC-IQ-006 | Create test AE case with voice input | Patient context preserved | ☐ Pass ☐ Fail | P0 Critical | |
| TC-IQ-007 | Trigger readback confirmation | Readback session created | ☐ Pass ☐ Fail | P0 Critical | |
| TC-IQ-008 | Generate narrative with model tracking | Generation record created | ☐ Pass ☐ Fail | P0 Critical | |
| TC-IQ-009 | Verify audit trail creation | All actions logged | ☐ Pass ☐ Fail | GxP requirement | |

---

## 7. SECURITY VERIFICATION

### 7.1 Data Protection

| Test Case | Procedure | Expected Result | Pass/Fail | Comments | Initials |
|-----------|-----------|-----------------|-----------|----------|----------|
| TC-IQ-010 | Verify local-only processing | No external network calls | ☐ Pass ☐ Fail | Privacy critical | |
| TC-IQ-011 | Test data encryption at rest | Database files encrypted | ☐ Pass ☐ Fail | | |
| TC-IQ-012 | Verify session security | Sessions use secure tokens | ☐ Pass ☐ Fail | | |
| TC-IQ-013 | Test password hashing | Passwords properly hashed | ☐ Pass ☐ Fail | | |

### 7.2 Access Controls

| Test Case | Procedure | Expected Result | Pass/Fail | Comments | Initials |
|-----------|-----------|-----------------|-----------|----------|----------|
| TC-IQ-014 | Test role-based permissions | Users restricted to assigned permissions | ☐ Pass ☐ Fail | | |
| TC-IQ-015 | Verify session timeout | Sessions expire after configured time | ☐ Pass ☐ Fail | | |
| TC-IQ-016 | Test account lockout | Accounts locked after failed attempts | ☐ Pass ☐ Fail | | |

---

## 8. COMPLIANCE VERIFICATION

### 8.1 GxP Requirements

| Requirement | Verification Method | Pass/Fail | Comments | Initials |
|-------------|-------------------|-----------|----------|----------|
| Audit trail complete | Review audit log entries | ☐ Pass ☐ Fail | | |
| User accountability | Verify user actions traceable | ☐ Pass ☐ Fail | | |
| Data integrity | Verify no unauthorized changes | ☐ Pass ☐ Fail | | |
| Change control | Version control system active | ☐ Pass ☐ Fail | | |

### 8.2 Patient Safety Requirements

| Requirement | Verification Method | Pass/Fail | Comments | Initials |
|-------------|-------------------|-----------|----------|----------|
| Patient voice preservation | Test context preservation module | ☐ Pass ☐ Fail | P0 Critical | |
| Voice confirmation available | Test readback functionality | ☐ Pass ☐ Fail | P0 Critical | |
| Model traceability | Verify generation tracking | ☐ Pass ☐ Fail | P0 Critical | |

---

## 9. DEVIATIONS AND RESOLUTIONS

| Deviation # | Description | Root Cause | Resolution | Approved By | Date |
|-------------|-------------|------------|------------|-------------|------|
| | | | | | |
| | | | | | |
| | | | | | |

---

## 10. CONCLUSION

### 10.1 Installation Summary
☐ **PASS** - All installation requirements met, system ready for OQ  
☐ **FAIL** - Installation requirements not met, remediation required

### 10.2 Critical Findings
- Patient safety features: ☐ All enabled ☐ Issues found
- GxP compliance features: ☐ All verified ☐ Issues found  
- Security controls: ☐ All verified ☐ Issues found

### 10.3 Recommendations
1. Proceed to Operational Qualification (OQ) if all tests pass
2. Address any critical findings before OQ
3. Document any approved deviations

---

## 11. SIGNATURES

| Role | Name | Signature | Date |
|------|------|-----------|------|
| **System Administrator** | | | |
| **QA Representative** | | | |
| **IT Security** | | | |
| **Validation Manager** | | | |

---

## 12. APPENDICES

### Appendix A: Installation Log Files
- Installation command outputs
- Error logs (if any)
- System configuration files

### Appendix B: Test Evidence
- Screenshots of successful tests
- System log excerpts
- Configuration verification outputs

### Appendix C: Security Scan Results
- Vulnerability assessment results
- Network isolation verification
- Data encryption verification

---

**Document Control:**
- Created by: Validation Team
- Reviewed by: QA Manager
- Approved by: Validation Manager
- Next Review: Annual or with system changes

**Change History:**
| Version | Date | Author | Description |
|---------|------|--------|-------------|
| 1.0 | 2024-01-04 | Validation Team | Initial version | 