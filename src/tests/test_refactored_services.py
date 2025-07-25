"""
Tests for refactored services and utilities.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from typing import Dict, Any

from ..services.scan_service import ScanService, ScanResult
from ..services.sheets_service import GoogleSheetsService, SheetConfig, ScanData
from ..services.volunteer_service import VolunteerService
from ..utils.common_utils import CallbackManager, StateManager, RetryManager
from ..config.config_manager import ConfigManager, ApplicationConfig


class TestScanService(unittest.TestCase):
    """Test cases for the ScanService class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.volunteer_service = Mock(spec=VolunteerService)
        self.scan_service = ScanService(self.volunteer_service)
    
    def test_process_scan_with_volunteer_found(self):
        """Test processing a scan when volunteer is found in master list."""
        # Mock volunteer service response
        volunteer_info = {
            'volunteer_id': '12345',
            'first_name': 'John',
            'last_name': 'Doe'
        }
        self.volunteer_service.lookup_volunteer.return_value = volunteer_info
        
        # Process scan
        result = self.scan_service.process_scan('12345', 'QR_CODE')
        
        # Verify result
        self.assertTrue(result.success)
        self.assertEqual(result.data, '12345')
        self.assertEqual(result.barcode_type, 'QR_CODE')
        self.assertEqual(result.first_name, 'John')
        self.assertEqual(result.last_name, 'Doe')
        self.assertEqual(result.formatted_name, 'Doe, John')
        self.assertEqual(result.status, 'Present')
        self.assertIsNone(result.error_message)
    
    def test_process_scan_with_volunteer_not_found(self):
        """Test processing a scan when volunteer is not found in master list."""
        # Mock volunteer service to return None
        self.volunteer_service.lookup_volunteer.return_value = None
        
        # Process scan with name-like data
        result = self.scan_service.process_scan('Doe, John', 'QR_CODE')
        
        # Verify result
        self.assertTrue(result.success)
        self.assertEqual(result.data, 'Doe, John')
        self.assertEqual(result.barcode_type, 'QR_CODE')
        self.assertEqual(result.first_name, 'John')
        self.assertEqual(result.last_name, 'Doe')
        self.assertEqual(result.formatted_name, 'Doe, John')
        self.assertEqual(result.status, 'Present')
    
    def test_process_scan_with_invalid_data(self):
        """Test processing a scan with invalid data."""
        # Mock validation to fail
        with patch('src.services.scan_service.validate_scan_data', return_value=False):
            result = self.scan_service.process_scan('', 'QR_CODE')
        
        # Verify result
        self.assertFalse(result.success)
        self.assertEqual(result.status, 'Error')
        self.assertIsNotNone(result.error_message)
    
    def test_is_name_format_detection(self):
        """Test name format detection."""
        # Test valid name format
        self.assertTrue(self.scan_service._is_name_format('Doe, John'))
        self.assertTrue(self.scan_service._is_name_format('Smith, Jane'))
        
        # Test invalid name format
        self.assertFalse(self.scan_service._is_name_format('john@example.com'))
        self.assertFalse(self.scan_service._is_name_format('https://example.com'))
        self.assertFalse(self.scan_service._is_name_format('John Doe'))  # No comma
    
    def test_parse_name_format(self):
        """Test parsing name from format."""
        first_name, last_name = self.scan_service._parse_name_format('Doe, John')
        self.assertEqual(first_name, 'John')
        self.assertEqual(last_name, 'Doe')
        
        first_name, last_name = self.scan_service._parse_name_format('Smith, Jane Marie')
        self.assertEqual(first_name, 'Jane')
        self.assertEqual(last_name, 'Smith')


class TestGoogleSheetsService(unittest.TestCase):
    """Test cases for the GoogleSheetsService class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = SheetConfig(
            spreadsheet_id='test_spreadsheet_id',
            sheet_name='test_sheet',
            master_list_sheet='test_master_list'
        )
        self.sheets_service = GoogleSheetsService(self.config)
    
    def test_add_scan_data_success(self):
        """Test successfully adding scan data."""
        # Mock the sheets service
        self.sheets_service.sheets_service = Mock()
        self.sheets_service.sheets_service.spreadsheets.return_value.values.return_value.append.return_value.execute.return_value = {}
        
        # Create scan data
        scan_data = ScanData(
            data='12345',
            barcode_type='QR_CODE',
            formatted_name='Doe, John',
            first_name='John',
            last_name='Doe',
            status='Present'
        )
        
        # Add scan data
        result = self.sheets_service.add_scan_data(scan_data)
        
        # Verify result
        self.assertTrue(result)
    
    def test_add_scan_data_not_connected(self):
        """Test adding scan data when not connected."""
        # Ensure not connected
        self.sheets_service.sheets_service = None
        
        # Create scan data
        scan_data = ScanData(
            data='12345',
            barcode_type='QR_CODE',
            formatted_name='Doe, John',
            first_name='John',
            last_name='Doe',
            status='Present'
        )
        
        # Add scan data
        result = self.sheets_service.add_scan_data(scan_data)
        
        # Verify result
        self.assertFalse(result)
    
    def test_lookup_volunteer_success(self):
        """Test successfully looking up a volunteer."""
        # Mock master list data
        self.sheets_service.master_list_headers = ['ID', 'First Name', 'Last Name']
        self.sheets_service.master_list_data = [
            ['12345', 'John', 'Doe'],
            ['67890', 'Jane', 'Smith']
        ]
        
        # Look up volunteer
        result = self.sheets_service.lookup_volunteer('12345')
        
        # Verify result
        self.assertIsNotNone(result)
        self.assertEqual(result['volunteer_id'], '12345')
        self.assertEqual(result['first_name'], 'John')
        self.assertEqual(result['last_name'], 'Doe')
    
    def test_lookup_volunteer_not_found(self):
        """Test looking up a volunteer that doesn't exist."""
        # Mock master list data
        self.sheets_service.master_list_headers = ['ID', 'First Name', 'Last Name']
        self.sheets_service.master_list_data = [
            ['12345', 'John', 'Doe']
        ]
        
        # Look up volunteer
        result = self.sheets_service.lookup_volunteer('99999')
        
        # Verify result
        self.assertIsNone(result)


class TestVolunteerService(unittest.TestCase):
    """Test cases for the VolunteerService class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.volunteer_service = VolunteerService()
        self.volunteer_service.master_list_headers = ['ID', 'First Name', 'Last Name']
        self.volunteer_service.master_list_data = [
            ['12345', 'John', 'Doe'],
            ['67890', 'Jane', 'Smith']
        ]
    
    def test_lookup_volunteer_success(self):
        """Test successfully looking up a volunteer."""
        result = self.volunteer_service.lookup_volunteer('12345')
        
        self.assertIsNotNone(result)
        self.assertEqual(result['volunteer_id'], '12345')
        self.assertEqual(result['first_name'], 'John')
        self.assertEqual(result['last_name'], 'Doe')
    
    def test_lookup_volunteer_not_found(self):
        """Test looking up a volunteer that doesn't exist."""
        result = self.volunteer_service.lookup_volunteer('99999')
        
        self.assertIsNone(result)
    
    def test_process_volunteer_scan_with_master_list(self):
        """Test processing a volunteer scan with master list lookup."""
        result = self.volunteer_service.process_volunteer_scan('12345')
        
        formatted_name, first_name, last_name = result
        self.assertEqual(formatted_name, 'Doe, John')
        self.assertEqual(first_name, 'John')
        self.assertEqual(last_name, 'Doe')
    
    def test_process_volunteer_scan_without_master_list(self):
        """Test processing a volunteer scan without master list."""
        # Clear master list
        self.volunteer_service.master_list_data = []
        
        result = self.volunteer_service.process_volunteer_scan('Doe, John')
        
        formatted_name, first_name, last_name = result
        self.assertEqual(formatted_name, 'Doe, John')
        self.assertEqual(first_name, 'John')
        self.assertEqual(last_name, 'Doe')


class TestCallbackManager(unittest.TestCase):
    """Test cases for the CallbackManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.callback_manager = CallbackManager()
        self.test_callback = Mock()
    
    def test_register_callback(self):
        """Test registering a callback."""
        result = self.callback_manager.register_callback('test_event', self.test_callback)
        
        self.assertTrue(result)
        self.assertEqual(self.callback_manager.get_callback_count('test_event'), 1)
    
    def test_register_duplicate_callback(self):
        """Test registering the same callback twice."""
        self.callback_manager.register_callback('test_event', self.test_callback)
        result = self.callback_manager.register_callback('test_event', self.test_callback)
        
        self.assertTrue(result)
        self.assertEqual(self.callback_manager.get_callback_count('test_event'), 1)
    
    def test_unregister_callback(self):
        """Test unregistering a callback."""
        self.callback_manager.register_callback('test_event', self.test_callback)
        result = self.callback_manager.unregister_callback('test_event', self.test_callback)
        
        self.assertTrue(result)
        self.assertEqual(self.callback_manager.get_callback_count('test_event'), 0)
    
    def test_invoke_callbacks(self):
        """Test invoking callbacks."""
        self.callback_manager.register_callback('test_event', self.test_callback)
        
        count = self.callback_manager.invoke_callbacks('test_event', 'arg1', 'arg2')
        
        self.assertEqual(count, 1)
        self.test_callback.assert_called_once_with('arg1', 'arg2')


class TestStateManager(unittest.TestCase):
    """Test cases for the StateManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.state_manager = StateManager('initial')
        self.test_callback = Mock()
    
    def test_initial_state(self):
        """Test initial state."""
        self.assertEqual(self.state_manager.get_state(), 'initial')
        self.assertIsNone(self.state_manager.get_previous_state())
    
    def test_change_state(self):
        """Test changing state."""
        result = self.state_manager.change_state('new_state')
        
        self.assertTrue(result)
        self.assertEqual(self.state_manager.get_state(), 'new_state')
        self.assertEqual(self.state_manager.get_previous_state(), 'initial')
    
    def test_state_transition_rules(self):
        """Test state transition rules."""
        self.state_manager.add_transition_rule('initial', ['new_state'])
        
        # Valid transition
        result = self.state_manager.change_state('new_state')
        self.assertTrue(result)
        
        # Invalid transition
        result = self.state_manager.change_state('invalid_state')
        self.assertFalse(result)
    
    def test_state_callbacks(self):
        """Test state change callbacks."""
        self.state_manager.add_state_callback('new_state', self.test_callback)
        self.state_manager.change_state('new_state')
        
        self.test_callback.assert_called_once_with('new_state', 'initial')


class TestRetryManager(unittest.TestCase):
    """Test cases for the RetryManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.retry_manager = RetryManager(max_retries=2, base_delay=0.1)
    
    def test_successful_operation(self):
        """Test successful operation without retries."""
        operation = Mock(return_value='success')
        
        result = self.retry_manager.execute_with_retry(operation)
        
        self.assertEqual(result, 'success')
        operation.assert_called_once()
    
    def test_operation_with_retries(self):
        """Test operation that succeeds after retries."""
        operation = Mock(side_effect=[Exception('fail'), Exception('fail'), 'success'])
        
        result = self.retry_manager.execute_with_retry(operation)
        
        self.assertEqual(result, 'success')
        self.assertEqual(operation.call_count, 3)
    
    def test_operation_failure(self):
        """Test operation that fails after all retries."""
        operation = Mock(side_effect=Exception('fail'))
        
        with self.assertRaises(Exception):
            self.retry_manager.execute_with_retry(operation)
        
        self.assertEqual(operation.call_count, 3)  # max_retries + 1


class TestConfigManager(unittest.TestCase):
    """Test cases for the ConfigManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config_manager = ConfigManager()
    
    def test_initial_config(self):
        """Test initial configuration."""
        config = self.config_manager.get_config()
        
        self.assertIsInstance(config, ApplicationConfig)
        self.assertEqual(config.app_name, 'QR Code Scanner')
        self.assertIsNotNone(config.google_sheets)
        self.assertIsNotNone(config.camera)
        self.assertIsNotNone(config.window)
        self.assertIsNotNone(config.performance)
        self.assertIsNotNone(config.logging)
    
    def test_update_google_sheets_config(self):
        """Test updating Google Sheets configuration."""
        result = self.config_manager.update_google_sheets_config(
            spreadsheet_id='new_spreadsheet_id'
        )
        
        self.assertTrue(result)
        config = self.config_manager.get_google_sheets_config()
        self.assertEqual(config.spreadsheet_id, 'new_spreadsheet_id')
    
    def test_update_camera_config(self):
        """Test updating camera configuration."""
        result = self.config_manager.update_camera_config(
            camera_index=1,
            fps=60
        )
        
        self.assertTrue(result)
        config = self.config_manager.get_camera_config()
        self.assertEqual(config.camera_index, 1)
        self.assertEqual(config.fps, 60)
    
    def test_update_user_preferences(self):
        """Test updating user preferences."""
        result = self.config_manager.update_user_preferences(
            dark_mode=True,
            auto_save_enabled=False
        )
        
        self.assertTrue(result)
        config = self.config_manager.get_config()
        self.assertTrue(config.dark_mode)
        self.assertFalse(config.auto_save_enabled)
    
    def test_reset_to_defaults(self):
        """Test resetting configuration to defaults."""
        # Change some values
        self.config_manager.update_google_sheets_config(spreadsheet_id='changed_id')
        
        # Reset
        result = self.config_manager.reset_to_defaults('google_sheets')
        
        self.assertTrue(result)
        config = self.config_manager.get_google_sheets_config()
        self.assertEqual(config.spreadsheet_id, '1PjW2-qgjWs5123qkzVyOBc-OKs2Ygk1143zkl_CymwQ')  # Default value


if __name__ == '__main__':
    unittest.main() 