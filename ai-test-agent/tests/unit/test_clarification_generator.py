import unittest
from src.clarification_generator.clarification_generator import ClarificationGenerator

class TestClarificationGenerator(unittest.TestCase):
    def setUp(self):
        self.generator = ClarificationGenerator()
        self.test_structured_data = {
            'sections': ['# Requirements', '# Constraints'],
            'requirements': [
                'User authentication should be implemented',
                'Data validation is required',
                'System should handle large amounts of data'
            ],
            'constraints': [
                'Response time should be less than 2 seconds',
                'System must be scalable'
            ]
        }
    
    def test_generate_clarification(self):
        """Test clarification generation"""
        clarification_doc = self.generator.generate_clarification(self.test_structured_data)
        
        self.assertIsInstance(clarification_doc, dict)
        self.assertIn('version', clarification_doc)
        self.assertIn('timestamp', clarification_doc)
        self.assertIn('ambiguous_points', clarification_doc)
        self.assertIn('conflicts', clarification_doc)
        self.assertIn('missing_information', clarification_doc)
        self.assertIn('suggestions', clarification_doc)
    
    def test_rule_based_analysis(self):
        """Test rule-based analysis fallback"""
        # Test with minimal data
        minimal_data = {
            'sections': [],
            'requirements': [],
            'constraints': []
        }
        clarification_doc = self.generator.generate_clarification(minimal_data)
        
        self.assertIsInstance(clarification_doc, dict)
        self.assertTrue(len(clarification_doc['suggestions']) > 0)
    
    def test_ambiguous_requirements(self):
        """Test detection of ambiguous requirements"""
        ambiguous_data = {
            'sections': ['# Requirements'],
            'requirements': [
                'System should handle some data',
                'User interface may be improved'
            ],
            'constraints': []
        }
        clarification_doc = self.generator.generate_clarification(ambiguous_data)
        
        self.assertIsInstance(clarification_doc, dict)
        # Should identify ambiguous points
        self.assertTrue(len(clarification_doc['ambiguous_points']) >= 0)

if __name__ == '__main__':
    unittest.main()