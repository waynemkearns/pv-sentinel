#!/usr/bin/env python3
"""
PV Sentinel - Phase 3 UX Enhancement Tests
Tests for Enhanced User Experience & Accessibility Features
"""

import unittest
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

try:
    from backend.ux_enhancement import (
        ResponsiveDesignManager,
        AccessibilityManager, 
        AnalyticsManager,
        PatientInterfaceManager,
        UserPreferences,
        AccessibilityLevel,
        InterfaceType,
        DeviceType,
        create_ux_enhancement_system
    )
    backend_available = True
except ImportError as e:
    print(f"⚠️ Backend modules not available: {e}")
    backend_available = False

class TestPhase3UXEnhancement(unittest.TestCase):
    """Test Phase 3 UX Enhancement features"""
    
    def setUp(self):
        """Set up test configuration"""
        self.test_config = {
            'ux_enhancement': {
                'responsive_design': True,
                'accessibility': True,
                'wcag_level': 'AA',
                'analytics': True,
                'patient_interface': True,
                'simplify_language': True
            }
        }
    
    def test_import_ux_enhancement(self):
        """Test UX enhancement module import"""
        self.assertTrue(backend_available, "UX enhancement module should be importable")
        print("✅ UX enhancement module import: PASSED")
    
    @unittest.skipUnless(backend_available, "Backend modules required")
    def test_create_ux_system(self):
        """Test UX enhancement system creation"""
        managers = create_ux_enhancement_system(self.test_config)
        self.assertEqual(len(managers), 4)
        print("✅ UX enhancement system creation: PASSED")
    
    @unittest.skipUnless(backend_available, "Backend modules required")
    def test_responsive_design_manager(self):
        """Test responsive design manager"""
        manager = ResponsiveDesignManager(self.test_config)
        self.assertTrue(manager.responsive_enabled)
        
        # Test device detection
        device_type = manager.detect_device_type("iPhone", 375)
        self.assertEqual(device_type, DeviceType.MOBILE)
        print("✅ Responsive design manager: PASSED")
    
    @unittest.skipUnless(backend_available, "Backend modules required")
    def test_accessibility_manager(self):
        """Test accessibility manager"""
        manager = AccessibilityManager(self.test_config)
        self.assertTrue(manager.accessibility_enabled)
        self.assertEqual(manager.target_level, AccessibilityLevel.AA)
        print("✅ Accessibility manager: PASSED")
    
    @unittest.skipUnless(backend_available, "Backend modules required")
    def test_analytics_manager(self):
        """Test analytics manager"""
        manager = AnalyticsManager(self.test_config)
        self.assertTrue(manager.analytics_enabled)
        
        # Test event tracking
        event_id = manager.track_event("test_user", "page_view", "Home")
        self.assertIsInstance(event_id, str)
        print("✅ Analytics manager: PASSED")
    
    @unittest.skipUnless(backend_available, "Backend modules required")
    def test_patient_interface_manager(self):
        """Test patient interface manager"""
        manager = PatientInterfaceManager(self.test_config)
        self.assertTrue(manager.patient_interface_enabled)
        
        # Test text simplification
        simplified = manager.simplify_medical_text("adverse event medication")
        self.assertIn("side effect", simplified)
        self.assertIn("medicine", simplified)
        print("✅ Patient interface manager: PASSED")

def run_phase3_tests():
    """Run all Phase 3 UX enhancement tests"""
    print("🚀 Running Phase 3 UX Enhancement Tests")
    print("=" * 50)
    
    if not backend_available:
        print("⚠️  Backend modules not available - running basic tests only")
    
    suite = unittest.TestLoader().loadTestsFromTestCase(TestPhase3UXEnhancement)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "=" * 50)
    print("📊 Phase 3 Test Results Summary")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    
    success_rate = ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100) if result.testsRun > 0 else 0
    print(f"✅ Success rate: {success_rate:.1f}%")
    
    if success_rate >= 90:
        print("🎉 Phase 3 UX Enhancement features are working excellently!")
    elif success_rate >= 75:
        print("👍 Phase 3 UX Enhancement features are working well!")
    else:
        print("⚠️  Some Phase 3 UX Enhancement features need attention.")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_phase3_tests()
    sys.exit(0 if success else 1)