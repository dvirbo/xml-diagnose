#!/usr/bin/env python3
"""
Test script to verify the parsing works correctly with the provided input format.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.db_usage import DatabaseUpdater
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Mock database connection for testing
class MockConnection:
    def cursor(self):
        return MockCursor()
    
    def commit(self):
        pass
    
    def rollback(self):
        pass

class MockCursor:
    def execute(self, query, params):
        print(f"Mock execute: {query}")
        print(f"Mock params: {params}")
    
    def executemany(self, query, params_list):
        print(f"Mock executemany: {query}")
        print(f"Mock params_list: {params_list}")
    
    def fetchall(self):
        # Mock database results
        return [
            ('5236', 'alert_123', 'folder_1'),
            ('52367', 'alert_456', 'folder_2'),
            ('523670', 'alert_789', 'folder_3')
        ]

def test_parsing():
    """Test the parsing with the provided input format."""
    
    # Sample input data (your format)
    test_reports = {
        '5236': {
            'ReportNumber': '5236', 
            'FirstResponse': {'ReportDate': '2025-01-01'}, 
            'FinalResponse': {'mispar_tkina': 'TK001', 'ReportInstanceStatusReason': 'Success'}, 
            'Status': {'first_response_valid': True, 'final_response_valid': True, 'status_category': 'Valid'}
        },
        '52367': {
            'ReportNumber': '52367', 
            'FirstResponse': {'ReportDate': '2025-01-02'}, 
            'FinalResponse': {'mispar_tkina': 'TK002', 'ReportInstanceStatusReason': 'Success'}, 
            'Status': {'first_response_valid': True, 'final_response_valid': True, 'status_category': 'Valid'}
        },
        '523670': {
            'ReportNumber': '523670', 
            'FirstResponse': {'ReportDate': '2025-01-03'}, 
            'FinalResponse': {'mispar_tkina': 'TK003', 'ReportInstanceStatusReason': 'Success'}, 
            'Status': {'first_response_valid': True, 'final_response_valid': True, 'status_category': 'Valid'}
        }
    }
    
    print("Testing with input format:")
    print(f"Type: {type(test_reports)}")
    print(f"Keys: {list(test_reports.keys())}")
    print()
    
    # Create updater with mock connection
    updater = DatabaseUpdater(MockConnection())
    
    # Test parsing
    report_numbers, reports_items = updater._parse_reports_input(test_reports)
    
    print("Parsing results:")
    print(f"Report numbers: {report_numbers}")
    print(f"Reports items count: {len(reports_items)}")
    print(f"First item: {reports_items[0] if reports_items else 'None'}")
    print()
    
    # Test the full update process
    print("Testing full update process:")
    try:
        updater.update_database_bulk(test_reports)
        print("✅ Update process completed successfully!")
    except Exception as e:
        print(f"❌ Update process failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_parsing() 