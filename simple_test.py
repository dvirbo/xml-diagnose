#!/usr/bin/env python3
"""
Simple test to debug the parsing issue.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.updater import DatabaseUpdater
import logging

# Set up logging to see debug messages
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')

# Mock connection
class MockConnection:
    def cursor(self):
        return MockCursor()
    def commit(self): pass
    def rollback(self): pass

class MockCursor:
    def execute(self, query, params): pass
    def executemany(self, query, params_list): pass
    def fetchall(self): return []

# Test data (your exact format - a list containing a dictionary)
test_reports = [{
    '5236': {
        'ReportNumber': '5236', 
        'FirstResponse': {'ReportDate': '2025-01-01'}, 
        'FinalResponse': {'mispar_tkina': 'TK001'}, 
        'Status': {'first_response_valid': True, 'final_response_valid': True}
    },
    '52367': {
        'ReportNumber': '52367', 
        'FirstResponse': {'ReportDate': '2025-01-02'}, 
        'FinalResponse': {'mispar_tkina': 'TK002'}, 
        'Status': {'first_response_valid': True, 'final_response_valid': True}
    },
    '523670': {
        'ReportNumber': '523670', 
        'FirstResponse': {'ReportDate': '2025-01-03'}, 
        'FinalResponse': {'mispar_tkina': 'TK003'}, 
        'Status': {'first_response_valid': True, 'final_response_valid': True}
    }
}]

print("=== Testing _parse_reports_input ===")
print(f"Input type: {type(test_reports)}")
print(f"Input structure: List containing {len(test_reports)} items")
if test_reports:
    print(f"First item type: {type(test_reports[0])}")
    if isinstance(test_reports[0], dict):
        print(f"Dictionary keys: {list(test_reports[0].keys())}")

updater = DatabaseUpdater(MockConnection())
report_numbers, reports_items = updater._parse_reports_input(test_reports)

print("\nResults:")
print(f"Output report_numbers: {report_numbers}")
print(f"Output reports_items count: {len(reports_items)}")
if reports_items:
    print(f"First item in reports_items: {reports_items[0][0]} -> {list(reports_items[0][1].keys())}") 