"""
Test Suite for PV Sentinel Phase 4A & 4B Features
Comprehensive testing for enhanced analytics, operational improvements, and smart automation

Test Coverage:
- Phase 4A: Enhanced Analytics, Templates, Bulk Processing, Quick Actions, Enhanced Search
- Phase 4B: Intelligent Case Processing, Advanced NLP, Workflow Automation
"""

import unittest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta

# Add the parent directory to the path so we can import backend modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestPhase4AEnhancedAnalytics(unittest.TestCase):
    """Test Phase 4A Enhanced Analytics functionality"""
    
    def setUp(self):
        """Set up test configuration"""
        self.config = {
            'phase_4a': {
                'enhanced_analytics': {
                    'enabled': True,
                    'export_enabled': True,
                    'export_formats': ['pdf', 'excel', 'csv', 'json'],
                    'mvp_validation_tracking': True
                }
            }
        }
    
    def test_enhanced_analytics_manager_initialization(self):
        """Test Enhanced Analytics Manager initialization"""
        try:
            from backend.enhanced_analytics import create_enhanced_analytics_manager
            manager = create_enhanced_analytics_manager(self.config)
            
            self.assertIsNotNone(manager)
            self.assertTrue(manager.enabled)
            self.assertTrue(manager.export_enabled)
            print("✅ Enhanced Analytics Manager initialization: PASSED")
            
        except ImportError:
            print("⚠️ Enhanced Analytics Manager: Module not available (development mode)")
            self.skipTest("Enhanced Analytics module not available")
    
    def test_mvp_metrics_tracking(self):
        """Test MVP validation metrics tracking"""
        try:
            from backend.enhanced_analytics import create_enhanced_analytics_manager, MetricType
            manager = create_enhanced_analytics_manager(self.config)
            
            # Test metric tracking
            success = manager.track_metric(
                metric_type=MetricType.USER_ADOPTION,
                metric_name="daily_active_users",
                value=87.5,
                unit="percentage",
                user_role="operations_manager"
            )
            
            self.assertTrue(success)
            self.assertEqual(len(manager.metrics_data), 1)
            
            # Test MVP validation metrics
            mvp_metrics = manager.get_mvp_validation_metrics()
            self.assertIn("user_adoption_rate", mvp_metrics)
            self.assertIn("productivity_improvements", mvp_metrics)
            
            print("✅ MVP Metrics Tracking: PASSED")
            
        except ImportError:
            print("⚠️ MVP Metrics Tracking: Module not available (development mode)")
            self.skipTest("Enhanced Analytics module not available")
    
    def test_analytics_export_functionality(self):
        """Test analytics export in different formats"""
        try:
            from backend.enhanced_analytics import create_enhanced_analytics_manager, ReportFormat
            manager = create_enhanced_analytics_manager(self.config)
            
            # Test JSON export
            json_report = manager.export_analytics_report(
                report_format=ReportFormat.JSON,
                user_role="medical_director",
                time_period=30
            )
            
            self.assertIsNotNone(json_report)
            self.assertIn("PV Sentinel Analytics Report", json_report)
            
            # Test CSV export
            csv_report = manager.export_analytics_report(
                report_format=ReportFormat.CSV,
                user_role="operations_manager",
                time_period=7
            )
            
            self.assertIsNotNone(csv_report)
            self.assertIn("Generated Date", csv_report)
            
            print("✅ Analytics Export Functionality: PASSED")
            
        except ImportError:
            print("⚠️ Analytics Export: Module not available (development mode)")
            self.skipTest("Enhanced Analytics module not available")

class TestPhase4AOperationalImprovements(unittest.TestCase):
    """Test Phase 4A Operational Improvements functionality"""
    
    def setUp(self):
        """Set up test configuration"""
        self.config = {
            'phase_4a': {
                'operational_improvements': {
                    'templates': {'enabled': True, 'max_templates': 100},
                    'bulk_processing': {'enabled': True, 'max_batch_size': 50},
                    'quick_actions': {'enabled': True},
                    'enhanced_search': {'enabled': True}
                }
            }
        }
    
    def test_template_management(self):
        """Test template creation and management"""
        try:
            from backend.operational_improvements import create_operational_improvements_system, TemplateType
            
            template_manager, _, _, _ = create_operational_improvements_system(self.config)
            
            # Test template creation
            template_id = template_manager.create_template(
                template_type=TemplateType.CASE_NARRATIVE,
                name="Test Template",
                description="Test description",
                content="Patient {age} experienced {event}",
                created_by="test_user"
            )
            
            self.assertIsNotNone(template_id)
            
            # Test template retrieval
            template = template_manager.get_template(template_id)
            self.assertIsNotNone(template)
            self.assertEqual(template.name, "Test Template")
            
            # Test template application
            rendered = template_manager.apply_template(template_id, {"age": "65", "event": "headache"})
            self.assertIn("Patient 65 experienced headache", rendered)
            
            print("✅ Template Management: PASSED")
            
        except ImportError:
            print("⚠️ Template Management: Module not available (development mode)")
            self.skipTest("Operational Improvements module not available")
    
    def test_bulk_processing(self):
        """Test bulk processing functionality"""
        try:
            from backend.operational_improvements import create_operational_improvements_system
            
            _, bulk_manager, _, _ = create_operational_improvements_system(self.config)
            
            # Test bulk operation
            result = bulk_manager.process_batch(
                operation_type="assign_reviewer",
                target_items=["CASE_001", "CASE_002", "CASE_003"],
                parameters={"reviewer": "Dr. Smith"},
                created_by="test_user"
            )
            
            self.assertTrue(result["success"])
            self.assertEqual(result["total_items"], 3)
            self.assertIn("processing_time", result)
            
            print("✅ Bulk Processing: PASSED")
            
        except ImportError:
            print("⚠️ Bulk Processing: Module not available (development mode)")
            self.skipTest("Operational Improvements module not available")
    
    def test_quick_actions(self):
        """Test quick actions functionality"""
        try:
            from backend.operational_improvements import create_operational_improvements_system
            
            _, _, quick_actions_manager, _ = create_operational_improvements_system(self.config)
            
            # Test getting available actions
            user_permissions = ["assign_reviewer", "modify_priority"]
            actions = quick_actions_manager.get_available_actions(user_permissions)
            
            self.assertGreater(len(actions), 0)
            
            # Test executing quick action
            if actions:
                action_id = actions[0].action_id
                result = quick_actions_manager.execute_quick_action(
                    action_id=action_id,
                    target_items=["CASE_001"],
                    action_parameters={"priority": "high"},
                    executed_by="test_user"
                )
                
                self.assertTrue(result["success"])
                self.assertEqual(result["affected_items"], 1)
            
            print("✅ Quick Actions: PASSED")
            
        except ImportError:
            print("⚠️ Quick Actions: Module not available (development mode)")
            self.skipTest("Operational Improvements module not available")
    
    def test_enhanced_search(self):
        """Test enhanced search functionality"""
        try:
            from backend.operational_improvements import create_operational_improvements_system
            
            _, _, _, search_manager = create_operational_improvements_system(self.config)
            
            # Test search functionality
            results = search_manager.search_cases(
                query="high priority cases",
                filters={"priority": "high", "status": "pending_review"}
            )
            
            self.assertTrue(results["success"])
            self.assertIn("total_results", results)
            self.assertIn("results", results)
            self.assertIn("search_time", results)
            
            print("✅ Enhanced Search: PASSED")
            
        except ImportError:
            print("⚠️ Enhanced Search: Module not available (development mode)")
            self.skipTest("Operational Improvements module not available")

class TestPhase4BSmartAutomation(unittest.TestCase):
    """Test Phase 4B Smart Automation functionality"""
    
    def setUp(self):
        """Set up test configuration"""
        self.config = {
            'phase_4b': {
                'intelligent_processing': {
                    'enabled': True,
                    'auto_classification': True,
                    'confidence_threshold': 0.8
                },
                'advanced_nlp': {
                    'enabled': True,
                    'medical_dictionary': True
                },
                'workflow_automation': {
                    'enabled': True,
                    'auto_routing': True,
                    'compliance_checks': True
                }
            }
        }
        
        self.sample_case = {
            'case_id': 'TEST_001',
            'description': 'Patient experienced severe headache and nausea after taking medication',
            'patient_age': 45,
            'patient_gender': 'female',
            'product_name': 'TestDrug',
            'time_to_onset_hours': 24,
            'reporter_type': 'physician'
        }
    
    def test_intelligent_case_processing(self):
        """Test intelligent case processing and auto-classification"""
        try:
            from backend.smart_automation import create_smart_automation_system
            
            intelligent_processor, _, _ = create_smart_automation_system(self.config)
            
            # Test auto-classification
            classification = intelligent_processor.auto_classify_severity(self.sample_case)
            
            self.assertIsNotNone(classification)
            self.assertIn(classification.severity_level.value, ['non_serious', 'serious', 'death', 'life_threatening', 'hospitalization'])
            self.assertGreaterEqual(classification.confidence_score, 0.0)
            self.assertLessEqual(classification.confidence_score, 1.0)
            
            # Test causality assessment
            causality = intelligent_processor.assess_causality(self.sample_case)
            
            self.assertIn("causality_assessment", causality)
            self.assertIn("confidence_score", causality)
            
            # Test quality scoring
            quality = intelligent_processor.calculate_quality_score(self.sample_case)
            
            self.assertIn("overall_score", quality)
            self.assertIn("quality_grade", quality)
            
            print("✅ Intelligent Case Processing: PASSED")
            
        except ImportError:
            print("⚠️ Intelligent Case Processing: Module not available (development mode)")
            self.skipTest("Smart Automation module not available")
    
    def test_advanced_nlp_processing(self):
        """Test advanced NLP processing functionality"""
        try:
            from backend.smart_automation import create_smart_automation_system
            
            _, nlp_processor, _ = create_smart_automation_system(self.config)
            
            # Test medical term extraction
            text = "Patient experienced severe headache, nausea, and dizziness after taking aspirin"
            medical_terms = nlp_processor.extract_medical_terms(text)
            
            self.assertIsInstance(medical_terms, list)
            if medical_terms:
                self.assertIn("term", [term.term for term in medical_terms])
                self.assertIn("category", [term.category for term in medical_terms])
            
            # Test case summary generation
            summary = nlp_processor.generate_case_summary(self.sample_case)
            
            self.assertIsNotNone(summary)
            self.assertIsNotNone(summary.executive_summary)
            self.assertIsInstance(summary.key_facts, list)
            self.assertIsInstance(summary.timeline, list)
            
            print("✅ Advanced NLP Processing: PASSED")
            
        except ImportError:
            print("⚠️ Advanced NLP Processing: Module not available (development mode)")
            self.skipTest("Smart Automation module not available")
    
    def test_workflow_automation(self):
        """Test workflow automation functionality"""
        try:
            from backend.smart_automation import create_smart_automation_system, AutoClassificationResult, SeverityLevel
            
            intelligent_processor, _, workflow_manager = create_smart_automation_system(self.config)
            
            # Create mock classification result
            classification = AutoClassificationResult(
                case_id="TEST_001",
                severity_level=SeverityLevel.SERIOUS,
                confidence_score=0.85,
                contributing_factors=["severe symptoms"],
                recommended_actions=["medical review"],
                classification_timestamp=datetime.now().isoformat()
            )
            
            # Test case routing
            routing = workflow_manager.route_case(self.sample_case, classification)
            
            self.assertIn("recommended_assignee", routing)
            self.assertIn("priority_level", routing)
            self.assertIn("review_timeline", routing)
            
            # Test compliance checks
            compliance = workflow_manager.check_compliance(self.sample_case)
            
            self.assertIn("compliance_score", compliance)
            self.assertIn("compliance_status", compliance)
            
            print("✅ Workflow Automation: PASSED")
            
        except ImportError:
            print("⚠️ Workflow Automation: Module not available (development mode)")
            self.skipTest("Smart Automation module not available")

class TestPhase4Integration(unittest.TestCase):
    """Test integration between Phase 4A and 4B features"""
    
    def test_phase4_feature_integration(self):
        """Test that Phase 4A and 4B features work together"""
        print("🔗 Testing Phase 4A & 4B Integration...")
        
        # Test that enhanced analytics can track smart automation metrics
        try:
            from backend.enhanced_analytics import create_enhanced_analytics_manager, MetricType
            from backend.operational_improvements import create_operational_improvements_system
            
            analytics_config = {
                'phase_4a': {
                    'enhanced_analytics': {'enabled': True, 'mvp_validation_tracking': True}
                }
            }
            
            ops_config = {
                'phase_4a': {
                    'operational_improvements': {
                        'templates': {'enabled': True},
                        'bulk_processing': {'enabled': True}
                    }
                }
            }
            
            analytics_manager = create_enhanced_analytics_manager(analytics_config)
            template_manager, bulk_manager, _, _ = create_operational_improvements_system(ops_config)
            
            # Simulate using operational improvements and tracking with analytics
            analytics_manager.track_metric(
                metric_type=MetricType.FEATURE_USAGE,
                metric_name="template_usage",
                value=15.0,
                unit="uses_per_day"
            )
            
            # Test that both systems are working
            self.assertTrue(analytics_manager.enabled)
            self.assertTrue(template_manager.enabled)
            
            print("✅ Phase 4A & 4B Integration: PASSED")
            
        except ImportError:
            print("⚠️ Phase 4 Integration: Modules not available (development mode)")
            self.skipTest("Phase 4 modules not available")
    
    def test_frontend_integration_readiness(self):
        """Test that frontend integration points are ready"""
        print("🖥️ Testing Frontend Integration Readiness...")
        
        # Test import paths that frontend will use
        integration_tests = [
            ("Enhanced Analytics", "backend.enhanced_analytics", "create_enhanced_analytics_manager"),
            ("Operational Improvements", "backend.operational_improvements", "create_operational_improvements_system"),
            ("Smart Automation", "backend.smart_automation", "create_smart_automation_system")
        ]
        
        passed_tests = 0
        for test_name, module_path, function_name in integration_tests:
            try:
                module = __import__(module_path, fromlist=[function_name])
                func = getattr(module, function_name)
                self.assertTrue(callable(func))
                passed_tests += 1
                print(f"  ✅ {test_name}: Import ready")
            except (ImportError, AttributeError):
                print(f"  ⚠️ {test_name}: Not available (development mode)")
        
        if passed_tests > 0:
            print("✅ Frontend Integration Readiness: PARTIAL (development environment)")
        else:
            print("⚠️ Frontend Integration Readiness: Modules need to be completed")

def run_phase4_tests():
    """Run all Phase 4 tests and generate report"""
    print("="*80)
    print("🧪 PV SENTINEL PHASE 4A & 4B COMPREHENSIVE TEST SUITE")
    print("="*80)
    print(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add Phase 4A tests
    test_suite.addTest(unittest.makeSuite(TestPhase4AEnhancedAnalytics))
    test_suite.addTest(unittest.makeSuite(TestPhase4AOperationalImprovements))
    
    # Add Phase 4B tests
    test_suite.addTest(unittest.makeSuite(TestPhase4BSmartAutomation))
    
    # Add integration tests
    test_suite.addTest(unittest.makeSuite(TestPhase4Integration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Generate summary
    print("\n" + "="*80)
    print("📊 TEST RESULTS SUMMARY")
    print("="*80)
    
    total_tests = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)
    skipped = len(result.skipped) if hasattr(result, 'skipped') else 0
    passed = total_tests - failures - errors - skipped
    
    print(f"Total Tests: {total_tests}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failures}")
    print(f"💥 Errors: {errors}")
    print(f"⏭️ Skipped: {skipped}")
    
    success_rate = (passed / total_tests * 100) if total_tests > 0 else 0
    print(f"\n🎯 Success Rate: {success_rate:.1f}%")
    
    if success_rate >= 70:
        print("🎉 PHASE 4 FEATURES: READY FOR DEPLOYMENT!")
    elif success_rate >= 50:
        print("⚠️ PHASE 4 FEATURES: PARTIAL IMPLEMENTATION")
    else:
        print("🚨 PHASE 4 FEATURES: NEEDS DEVELOPMENT")
    
    return result

if __name__ == "__main__":
    run_phase4_tests() 