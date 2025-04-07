import unittest
import os
import tempfile
from datetime import datetime
from log_analyzer.py import parse_log_file, analyze_logs

class TestLogAnalyzer(unittest.TestCase):
    def setUp(self):
        """Create temporary log files for testing."""
        # Test case 1: Standard hyphen-separated logs
        self.log1_content = [
            "2023-01-01 10:00:00 - auth - INFO - User login successful",
            "2023-01-01 10:01:00 - database - ERROR - Connection timeout",
            "2023-01-01 10:02:00 - api - WARNING - High response time"
        ]
        
        # Test case 2: Different timestamp format and mixed cases
        self.log2_content = [
            "01/02/2023 08:15:00 - AUTH - info - Login attempt",
            "01/02/2023 08:16:00 - DB - error - Connection failed",
            "01/02/2023 08:17:00 - API - WARNING - Slow response"
        ]
        
        # Create temporary files
        self.temp_file1 = tempfile.NamedTemporaryFile(mode='w+', delete=False)
        self.temp_file1.write('\n'.join(self.log1_content))
        self.temp_file1.close()
        
        self.temp_file2 = tempfile.NamedTemporaryFile(mode='w+', delete=False)
        self.temp_file2.write('\n'.join(self.log2_content))
        self.temp_file2.close()

    def tearDown(self):
        """Clean up temporary files."""
        os.unlink(self.temp_file1.name)
        os.unlink(self.temp_file2.name)

    def test_parse_log_file_standard_format(self):
        """Test parsing of standard hyphen-separated logs."""
        logs = parse_log_file(self.temp_file1.name)
        
        # Check number of logs parsed
        self.assertEqual(len(logs), 3)
        
        # Check first log entry
        self.assertEqual(logs[0]['service'], 'auth')
        self.assertEqual(logs[0]['log_level'], 'INFO')
        self.assertEqual(logs[0]['message'], 'User login successful')
        self.assertIsInstance(logs[0]['timestamp'], datetime)
        
        # Check error log entry
        self.assertEqual(logs[1]['service'], 'database')
        self.assertEqual(logs[1]['log_level'], 'ERROR')

    def test_parse_log_file_alternate_format(self):
        """Test parsing of logs with different timestamp format and mixed cases."""
        logs = parse_log_file(self.temp_file2.name)
        
        # Check number of logs parsed
        self.assertEqual(len(logs), 3)
        
        # Check case normalization (should preserve original case)
        self.assertEqual(logs[0]['service'], 'AUTH')
        self.assertEqual(logs[0]['log_level'], 'info')
        
        # Check timestamp parsing
        self.assertIsInstance(logs[0]['timestamp'], (datetime, str))
        
        # Check error log entry
        self.assertEqual(logs[1]['service'], 'DB')
        self.assertEqual(logs[1]['log_level'], 'error')

    def test_analyze_logs(self):
        """Test the analysis of parsed logs."""
        logs = parse_log_file(self.temp_file1.name)
        analysis = analyze_logs(logs)
        
        # Check basic counts
        self.assertEqual(analysis['total_logs'], 3)
        self.assertEqual(analysis['log_level_counts']['INFO'], 1)
        self.assertEqual(analysis['log_level_counts']['ERROR'], 1)
        self.assertEqual(analysis['log_level_counts']['WARNING'], 1)
        
        # Check service distribution
        self.assertEqual(analysis['service_counts']['auth'], 1)
        self.assertEqual(analysis['service_counts']['database'], 1)
        self.assertEqual(analysis['service_counts']['api'], 1)
        
        # Check error analysis
        self.assertEqual(analysis['error_service_distribution']['database'], 1)
        self.assertIn('Connection timeout', analysis['common_error_messages'])

    def test_analyze_empty_logs(self):
        """Test analysis with empty log file."""
        empty_file = tempfile.NamedTemporaryFile(mode='w+', delete=False)
        empty_file.close()
        
        logs = parse_log_file(empty_file.name)
        analysis = analyze_logs(logs)
        
        self.assertEqual(analysis, {})
        os.unlink(empty_file.name)

if __name__ == '__main__':
    unittest.main()
