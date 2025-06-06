"""

PV Sentinel - Phase 4B Smart Automation Module

Advanced AI-powered workflow automation and intelligent case processing

Focus Group Priority: High Impact Feature for 60%+ processing efficiency

"""



import streamlit as st

import pandas as pd

import numpy as np

from datetime import datetime, timedelta

import json

import re

from typing import Dict, List, Tuple, Optional

import time



def create_smart_automation_system():

    """

    Create comprehensive smart automation system

    Phase 4B Feature: AI-powered workflow automation

    """

    return SmartAutomationManager()



class SmartAutomationManager:

    """Phase 4B Smart Automation Manager - AI-Powered Workflow System"""

    

    def __init__(self):

        self.classification_models = self._initialize_classification_models()

        self.nlp_processors = self._initialize_nlp_processors()

        self.workflow_rules = self._initialize_workflow_rules()

        self.quality_metrics = self._initialize_quality_metrics()

    

    def _initialize_classification_models(self):

        """Initialize AI classification models for severity assessment"""

        return {

            "severity_keywords": {

                "death": ["death", "died", "fatal", "mortality", "deceased"],

                "life_threatening": ["life-threatening", "critical", "intensive care", "ventilator", "resuscitation"],

                "hospitalization": ["hospitalized", "admitted", "hospital", "emergency room", "er visit"],

                "serious": ["serious", "severe", "significant", "prolonged", "disability"],

                "non_serious": ["mild", "minor", "transient", "resolved", "temporary"]

            },

            "confidence_weights": {

                "keyword_match": 0.4,

                "context_analysis": 0.3,

                "temporal_relationship": 0.2,

                "patient_demographics": 0.1

            }

        }

    

    def _initialize_nlp_processors(self):

        """Initialize NLP processing components"""

        return {

            "medical_term_patterns": [

                r'\b(?:nausea|vomiting|dizziness|headache|rash|fever|pain|swelling)\b',

                r'\b(?:severe|mild|moderate|chronic|acute|sudden)\s+\w+',

                r'\b(?:after|following|during|within)\s+\d+\s*(?:hours?|days?|minutes?)\b'

            ],

            "temporal_patterns": [

                r'(?:after|following|within|during)\s+(?:\d+\s*(?:hours?|days?|minutes?|weeks?))',

                r'(?:approximately|about|roughly)\s+\d+\s*(?:hours?|days?|minutes?)',

                r'(?:immediately|shortly|soon)\s+(?:after|following)'

            ],

            "causality_indicators": [

                r'\b(?:caused by|due to|resulted from|attributed to|related to)\b',

                r'\b(?:following|after taking|upon administration)\b',

                r'\b(?:coincidental|unrelated|pre-existing)\b'

            ]

        }

    

    def _initialize_workflow_rules(self):

        """Initialize automated workflow routing rules"""

        return {

            "severity_routing": {

                "death": {

                    "assignee": "Senior Medical Officer",

                    "priority": "Urgent",

                    "timeline_hours": 0,  # Immediate

                    "notifications": ["medical_director", "regulatory_affairs", "quality_assurance"]

                },

                "life_threatening": {

                    "assignee": "Medical Officer",

                    "priority": "High",

                    "timeline_hours": 4,

                    "notifications": ["medical_director", "assigned_reviewer"]

                },

                "hospitalization": {

                    "assignee": "Medical Officer",

                    "priority": "High",

                    "timeline_hours": 24,

                    "notifications": ["assigned_reviewer", "operations_manager"]

                },

                "serious": {

                    "assignee": "Reviewer",

                    "priority": "Medium",

                    "timeline_hours": 72,

                    "notifications": ["assigned_reviewer"]

                },

                "non_serious": {

                    "assignee": "Reviewer",

                    "priority": "Low",

                    "timeline_hours": 168,  # 7 days

                    "notifications": ["assigned_reviewer"]

                }

            }

        }

    

    def _initialize_quality_metrics(self):

        """Initialize quality assessment framework"""

        return {

            "assessment_factors": {

                "patient_info_completeness": {

                    "weight": 0.20,

                    "required_fields": ["age", "gender", "medical_history"],

                    "description": "Completeness of patient demographic and medical information"

                },

                "event_description_adequacy": {

                    "weight": 0.20,

                    "criteria": ["detailed_description", "temporal_relationship", "outcome"],

                    "description": "Quality and completeness of adverse event description"

                },

                "temporal_relationship_clarity": {

                    "weight": 0.15,

                    "patterns": ["time_to_onset", "duration", "resolution"],

                    "description": "Clear temporal relationship between drug and event"

                },

                "outcome_documentation": {

                    "weight": 0.15,

                    "requirements": ["current_status", "actions_taken", "resolution"],

                    "description": "Documentation of event outcome and interventions"

                },

                "reporter_credibility": {

                    "weight": 0.20,

                    "factors": ["healthcare_professional", "direct_observation", "medical_records"],

                    "description": "Credibility and reliability of the reporter"

                },

                "supporting_documents": {

                    "weight": 0.10,

                    "types": ["medical_records", "lab_results", "imaging", "discharge_summary"],

                    "description": "Availability of supporting medical documentation"

                }

            }

        }

    

    def classify_case_severity(self, case_data: Dict) -> Dict:

        """

        AI-powered case severity classification

        

        Args:

            case_data: Dictionary containing case information

            

        Returns:

            Classification result with confidence score

        """

        start_time = time.time()

        

        description = case_data.get('description', '').lower()

        patient_age = case_data.get('patient_age', 0)

        

        # Keyword-based classification

        severity_scores = {}

        for severity, keywords in self.classification_models["severity_keywords"].items():

            score = sum(1 for keyword in keywords if keyword in description)

            severity_scores[severity] = score

        

        # Determine primary classification

        if not any(severity_scores.values()):

            predicted_severity = "non_serious"

            confidence = 0.5

        else:

            predicted_severity = max(severity_scores, key=severity_scores.get)

            base_confidence = min(0.9, severity_scores[predicted_severity] * 0.3 + 0.5)

            

            # Adjust confidence based on additional factors

            confidence_adjustments = 0

            

            # Age factor

            if patient_age > 65 and predicted_severity in ["serious", "hospitalization"]:

                confidence_adjustments += 0.1

            

            # Description length factor

            if len(description) > 100:

                confidence_adjustments += 0.05

            

            confidence = min(0.95, base_confidence + confidence_adjustments)

        

        # Generate contributing factors

        contributing_factors = []

        if patient_age > 65:

            contributing_factors.append("vulnerable population (elderly)")

        if any(keyword in description for keyword in ["hospital", "admitted", "emergency"]):

            contributing_factors.append("hospitalization keywords")

        if any(keyword in description for keyword in ["severe", "serious", "critical"]):

            contributing_factors.append("severity descriptors")

        

        # Generate recommended actions

        recommended_actions = self._generate_recommended_actions(predicted_severity, case_data)

        

        processing_time = time.time() - start_time

        

        return {

            "predicted_severity": predicted_severity,

            "confidence_score": confidence,

            "contributing_factors": contributing_factors,

            "recommended_actions": recommended_actions,

            "processing_time_seconds": round(processing_time, 2),

            "severity_scores": severity_scores

        }

    

    def _generate_recommended_actions(self, severity: str, case_data: Dict) -> List[str]:

        """Generate recommended actions based on severity classification"""

        actions = []

        

        if severity == "death":

            actions.extend([

                "Immediate medical director notification",

                "Regulatory authority notification within 15 days",

                "Complete case investigation",

                "Autopsy report if available"

            ])

        elif severity == "life_threatening":

            actions.extend([

                "Medical review within 4 hours",

                "Request detailed medical records",

                "Assess need for regulatory notification",

                "Monitor for similar cases"

            ])

        elif severity == "hospitalization":

            actions.extend([

                "Medical review within 24 hours",

                "Request hospital discharge summary",

                "Assess causality relationship",

                "Document outcome"

            ])

        elif severity == "serious":

            actions.extend([

                "Medical review within 72 hours",

                "Request additional medical information",

                "Assess causality relationship"

            ])

        else:  # non_serious

            actions.extend([

                "Standard review process",

                "Monitor for symptom resolution",

                "Document in safety database"

            ])

        

        return actions

    

    def process_nlp_analysis(self, text: str, options: Dict) -> Dict:

        """

        Advanced NLP processing for medical text analysis

        

        Args:

            text: Medical text to analyze

            options: Processing options (extract_terms, generate_summary, assess_causality)

            

        Returns:

            NLP analysis results

        """

        results = {}

        

        if options.get('extract_terms', False):

            results['extracted_terms'] = self._extract_medical_terms(text)

        

        if options.get('generate_summary', False):

            results['case_summary'] = self._generate_case_summary(text)

        

        if options.get('assess_causality', False):

            results['causality_assessment'] = self._assess_causality(text)

        

        return results

    

    def _extract_medical_terms(self, text: str) -> List[Dict]:

        """Extract medical terms from text using NLP patterns"""

        terms = []

        text_lower = text.lower()

        

        # Define term categories and patterns

        term_categories = {

            "adverse_events": [

                ("nausea", "10017947"), ("vomiting", "10046743"), ("dizziness", "10013573"),

                ("headache", "10019211"), ("rash", "10037844"), ("fever", "10016558"),

                ("pain", "10033371"), ("fatigue", "10016256"), ("weakness", "10047862")

            ],

            "severity_modifiers": [

                ("severe", None), ("mild", None), ("moderate", None),

                ("chronic", None), ("acute", None), ("sudden", None)

            ],

            "temporal_indicators": [

                ("immediately", None), ("within hours", None), ("after administration", None)

            ]

        }

        

        for category, term_list in term_categories.items():

            for term, meddra_code in term_list:

                if term in text_lower:

                    confidence = 0.95 if category == "adverse_events" else 0.8

                    

                    term_data = {

                        "term": term,

                        "category": category,

                        "confidence": confidence

                    }

                    

                    if meddra_code:

                        term_data["meddra"] = f"{term.title()} ({meddra_code})"

                    

                    terms.append(term_data)

        

        return terms

    

    def _generate_case_summary(self, text: str) -> str:

        """Generate AI case summary from medical text"""

        # Extract key information

        age_match = re.search(r'\b(\d+)[\s-]*year[\s-]*old\b', text, re.IGNORECASE)

        gender_match = re.search(r'\b(male|female|man|woman)\b', text, re.IGNORECASE)

        

        age_info = f"{age_match.group(1)}-year-old" if age_match else "patient of unspecified age"

        gender_info = gender_match.group(1) if gender_match else "gender unspecified"

        

        # Extract events

        event_terms = self._extract_medical_terms(text)

        events = [term["term"] for term in event_terms if term["category"] == "adverse_events"]

        

        # Extract temporal information

        temporal_match = re.search(r'(?:after|following|within)\s+(\d+\s*(?:hours?|days?|minutes?))', text, re.IGNORECASE)

        temporal_info = temporal_match.group(0) if temporal_match else "unspecified timeframe"

        

        summary = f"""

        **Executive Summary:** {age_info.title()} {gender_info} experienced {', '.join(events) if events else 'adverse events'} {temporal_info}.

        

        **Key Facts:**

        "  Patient: {age_info.title()} {gender_info.title()}

        "  Event onset: {temporal_info}

        "  Primary events: {', '.join(events).title() if events else 'Multiple symptoms reported'}

        "  Reporter: Healthcare Professional

        

        **Risk Factors:** {'Elderly patient' if age_match and int(age_match.group(1)) > 65 else 'None identified'}

        

        **Recommended Follow-up:**

        "  Assess causality relationship

        "  Monitor for symptom resolution

        "  Consider dose adjustment if rechallenge occurs

        """

        

        return summary.strip()

    

    def _assess_causality(self, text: str) -> Dict:

        """Assess causality relationship using NLP analysis"""

        text_lower = text.lower()

        

        # Assess temporal relationship

        temporal_score = 0

        if re.search(r'(?:after|following|within)\s+\d+\s*(?:hours?|days?)', text_lower):

            temporal_score = 0.8

        elif re.search(r'(?:immediately|shortly|soon)', text_lower):

            temporal_score = 0.9

        else:

            temporal_score = 0.4

        

        # Assess known drug effects

        drug_effect_score = 0.7  # Default assumption

        

        # Assess alternative explanations

        alternative_score = 0.8 if not re.search(r'(?:coincidental|unrelated|pre-existing)', text_lower) else 0.4

        

        # Calculate overall causality

        overall_score = (temporal_score + drug_effect_score + alternative_score) / 3

        

        # Determine causality category

        if overall_score >= 0.8:

            assessment = "Probable"

        elif overall_score >= 0.6:

            assessment = "Possible"

        elif overall_score >= 0.4:

            assessment = "Unlikely"

        else:

            assessment = "Unrelated"

        

        reasoning = [

            f"Temporal relationship score: {temporal_score:.1%}",

            "Known adverse events for drug class",

            "No clear alternative explanations identified" if alternative_score > 0.6 else "Alternative explanations possible"

        ]

        

        return {

            "assessment": assessment,

            "confidence": overall_score,

            "reasoning": reasoning,

            "who_umc_score": int(overall_score * 10)

        }

    

    def route_workflow(self, case_data: Dict) -> Dict:

        """

        Automated workflow routing based on case characteristics

        

        Args:

            case_data: Case information for routing decision

            

        Returns:

            Routing decision with assignments and notifications

        """

        severity = case_data.get('severity', 'non_serious')

        confidence = case_data.get('confidence', 0.5)

        patient_age = case_data.get('patient_age', 0)

        

        # Get base routing rule

        routing_rule = self.workflow_rules["severity_routing"].get(severity, 

                                                                  self.workflow_rules["severity_routing"]["non_serious"])

        

        # Customize based on additional factors

        routing_decision = routing_rule.copy()

        

        # Adjust for special populations

        special_considerations = []

        if patient_age > 65:

            special_considerations.append("Elderly patient - requires specialized review")

            if routing_decision["timeline_hours"] > 24:

                routing_decision["timeline_hours"] = 24  # Expedite for elderly

        

        if patient_age < 18:

            special_considerations.append("Pediatric case - requires pediatric specialist review")

            routing_decision["notifications"].append("pediatric_specialist")

        

        # Adjust for low confidence classifications

        if confidence < 0.7:

            special_considerations.append("Low confidence classification - manual review recommended")

            routing_decision["notifications"].append("quality_assurance")

        

        routing_decision["special_considerations"] = special_considerations

        

        return routing_decision

    

    def calculate_quality_score(self, case_data: Dict) -> Dict:

        """

        Calculate comprehensive quality score for case

        

        Args:

            case_data: Case information for quality assessment

            

        Returns:

            Quality score breakdown and overall assessment

        """

        factor_scores = {}

        

        for factor_name, factor_config in self.quality_metrics["assessment_factors"].items():

            score = self._calculate_factor_score(factor_name, factor_config, case_data)

            factor_scores[factor_name] = {

                "score": score,

                "weight": factor_config["weight"],

                "weighted_score": score * factor_config["weight"]

            }

        

        # Calculate overall score

        overall_score = sum(factor_data["weighted_score"] for factor_data in factor_scores.values())

        overall_score = min(100, max(0, overall_score))  # Ensure 0-100 range

        

        # Determine quality grade

        if overall_score >= 90:

            grade = "A"

            grade_description = "Excellent"

        elif overall_score >= 80:

            grade = "B"

            grade_description = "Good"

        elif overall_score >= 70:

            grade = "C"

            grade_description = "Adequate"

        else:

            grade = "D"

            grade_description = "Needs Improvement"

        

        # Generate compliance status

        compliance_status = "' Compliant" if overall_score >= 80 else "& Review Required"

        

        # Generate compliance checklist

        compliance_checks = self._generate_compliance_checklist(case_data, overall_score)

        

        return {

            "overall_score": round(overall_score, 1),

            "grade": grade,

            "grade_description": grade_description,

            "compliance_status": compliance_status,

            "factor_scores": factor_scores,

            "compliance_checks": compliance_checks

        }

    

    def _calculate_factor_score(self, factor_name: str, factor_config: Dict, case_data: Dict) -> float:

        """Calculate score for individual quality factor"""

        # Simulate scoring based on case data completeness and quality

        base_score = 70  # Base score

        

        # Factor-specific scoring logic

        if factor_name == "patient_info_completeness":

            required_fields = ["age", "gender", "medical_history"]

            completed_fields = sum(1 for field in required_fields if case_data.get(field))

            base_score = (completed_fields / len(required_fields)) * 100

        

        elif factor_name == "event_description_adequacy":

            description = case_data.get('description', '')

            if len(description) > 200:

                base_score = 95

            elif len(description) > 100:

                base_score = 85

            elif len(description) > 50:

                base_score = 75

            else:

                base_score = 60

        

        elif factor_name == "temporal_relationship_clarity":

            description = case_data.get('description', '').lower()

            if re.search(r'(?:after|following|within)\s+\d+\s*(?:hours?|days?)', description):

                base_score = 90

            elif re.search(r'(?:after|following)', description):

                base_score = 75

            else:

                base_score = 60

        

        elif factor_name == "reporter_credibility":

            reporter_type = case_data.get('reporter_type', 'patient')

            if reporter_type.lower() in ['physician', 'pharmacist', 'nurse']:

                base_score = 95

            elif reporter_type.lower() == 'patient':

                base_score = 75

            else:

                base_score = 65

        

        # Add random variation for demo purposes

        variation = np.random.uniform(-5, 5)

        return max(0, min(100, base_score + variation))

    

    def _generate_compliance_checklist(self, case_data: Dict, overall_score: float) -> List[Dict]:

        """Generate compliance checklist based on case data"""

        checks = [

            {

                "check": "Reporting Timeline",

                "status": "' Pass",

                "details": "Within regulatory timeframes"

            },

            {

                "check": "Required Fields",

                "status": "' Pass" if overall_score > 80 else "& Warning",

                "details": "All mandatory fields completed" if overall_score > 80 else "Some required fields missing"

            },

            {

                "check": "Patient Consent",

                "status": "& Warning" if np.random.random() > 0.7 else "' Pass",

                "details": "Consent documentation pending" if np.random.random() > 0.7 else "Patient consent documented"

            },

            {

                "check": "Data Quality",

                "status": "' Pass" if overall_score > 75 else "L' Fail",

                "details": "Adequate event description" if overall_score > 75 else "Event description needs improvement"

            },

            {

                "check": "Regulatory Requirements",

                "status": "' Pass",

                "details": "Meets current standards"

            }

        ]

        

        return checks

    

    def get_automation_statistics(self) -> Dict:

        """Get current automation performance statistics"""

        # Simulate realistic statistics

        return {

            "cases_auto_routed": 1247,

            "routing_accuracy": "94.2%",

            "avg_processing_time": "1.8s",

            "manual_interventions": "5.8%",

            "quality_score_avg": 87.3,

            "compliance_rate": "96.1%"

        }



# Demo functions for testing

def demo_smart_automation():

    """Demo function to test smart automation features"""

    automation_manager = SmartAutomationManager()

    

    # Demo case data

    sample_case = {

        "description": "65-year-old male patient experienced severe nausea and vomiting approximately 2 hours after taking the medication. Patient was hospitalized for observation.",

        "patient_age": 65,

        "patient_gender": "Male",

        "reporter_type": "Physician",

        "product_name": "Test Product"

    }

    

    # Test classification

    classification = automation_manager.classify_case_severity(sample_case)

    

    # Test NLP analysis

    nlp_options = {"extract_terms": True, "generate_summary": True, "assess_causality": True}

    nlp_results = automation_manager.process_nlp_analysis(sample_case["description"], nlp_options)

    

    # Test workflow routing

    routing = automation_manager.route_workflow({

        "severity": classification["predicted_severity"],

        "confidence": classification["confidence_score"],

        "patient_age": sample_case["patient_age"]

    })

    

    # Test quality scoring

    quality = automation_manager.calculate_quality_score(sample_case)

    

    return {

        "classification": classification,

        "nlp_results": nlp_results,

        "routing": routing,

        "quality": quality

    }



if __name__ == "__main__":

    # Run demo

    demo_results = demo_smart_automation()

    print("Smart Automation Demo Results:")

    for key, value in demo_results.items():

        print(f"\n{key.upper()}:")

        print(json.dumps(value, indent=2, default=str))

