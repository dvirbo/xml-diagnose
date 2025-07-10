import os
import csv
import logging
from datetime import datetime
from typing import Dict, Tuple, Any, List
import xml.etree.ElementTree as ET

# Constants
FIRST_RESPONSE_TAG = "FirstResponse"
FINAL_RESPONSE_TAG = "FinalResponse"
LEGAL_STATUS_OK = "תקין"

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def parse_xml_files(directory: str) -> Tuple[Dict[str, Dict], Dict[str, Dict]]:
    """
    Parses XML files in the specified directory and extracts information from files with root tags
    "FirstResponse" and "FinalResponse".
    
    Args:
        directory (str): The path to the directory containing XML files.
        
    Returns:
        tuple: A tuple containing two dictionaries:
            - first_responses (dict): Maps ReportNumber to extracted data from FirstResponse files
            - final_responses (dict): Maps ReportNumber to extracted data from FinalResponse files
            
    Raises:
        FileNotFoundError: If the directory doesn't exist
        ET.ParseError: If XML files are malformed
    """
    if not os.path.exists(directory):
        raise FileNotFoundError(f"Directory not found: {directory}")

    first_responses: Dict[str, Any] = {}
    final_responses: Dict[str, Any] = {}

    for filename in os.listdir(directory):
        if not filename.upper().endswith(".XML"):
            continue

        file_path = os.path.join(directory, filename)

        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
        except ET.ParseError as e:
            logging.warning(f"Could not parse {filename}: {e}")
            continue

        if root.tag == FIRST_RESPONSE_TAG:
            report_number = _safe_get_text(root, "ReportNumber")
            if report_number:
                first_responses[report_number] = {
                    "ReportDate": _safe_get_text(root, "ReportDate"),
                    "ReportInstanceReference": _safe_get_text(root, "ReportInstanceReference"),
                    "ReportInstanceLegalStatusDesc": _safe_get_text(root, "ReportInstanceLegalStatusDesc"),
                    "ReportInstanceStatusReason": _safe_get_text(root, "ReportInstanceStatusReason")
                }

        elif root.tag == FINAL_RESPONSE_TAG:
            report_number = _safe_get_text(root, "ReportMetaData/ReportNumber")
            if report_number:
                legal_status = _safe_get_text(root, "ReportMetaData/ReportInstanceLegalStatusDesc")
                status_reason = "" if legal_status == LEGAL_STATUS_OK else _safe_get_text(root, "ReportMetaData/ReportInstanceStatusReason")
                final_responses[report_number] = {
                    "ReportInstanceReference": _safe_get_text(root, "ReportMetaData/ReportInstanceReference"),
                    "ReportInstanceLegalStatusDesc": legal_status,
                    "ReportInstanceStatusReason": status_reason
                }

    return first_responses, final_responses


def _safe_get_text(element: ET.Element, xpath: str) -> str:
    """
    Safely extracts text from an XML element using XPath, returning empty string if not found.
    
    Args:
        element: The XML element to search in
        xpath: The XPath expression to find the target element
        
    Returns:
        str: The text content of the found element, or empty string if not found
    """
    found_element = element.find(xpath)
    return found_element.text.strip() if found_element is not None and found_element.text else ""


def classify_reports_by_status(first_responses: Dict[str, Dict], 
                             final_responses: Dict[str, Dict]) -> Tuple[Dict[str, Dict], Dict[str, Dict]]:
    """
    Classifies reports based on their final legal status and combines first and final response data.

    Args:
        first_responses (dict): FirstResponse data keyed by ReportNumber
        final_responses (dict): FinalResponse data keyed by ReportNumber

    Returns:
        tuple: (error_reports, valid_reports) where:
            - error_reports: Reports with final status != "תקין"
            - valid_reports: Reports with final status == "תקין"
            Each entry contains combined first and final response data.
    """
    error_reports: Dict[str, Any] = {}
    valid_reports: Dict[str, Any] = {}

    for report_number, final_data in final_responses.items():
        first_data = first_responses.get(report_number)
        combined_data = {
            "ReportNumber": report_number,
            "FinalResponse": final_data,
            "FirstResponse": first_data  # May be None if no matching first response
        }
        final_status = final_data.get("ReportInstanceLegalStatusDesc", "")
        if final_status == LEGAL_STATUS_OK:
            valid_reports[report_number] = combined_data
        else:
            error_reports[report_number] = combined_data



def export_reports_to_csv(error_reports: Dict[str, Dict], 
                         valid_reports: Dict[str, Dict], 
                         output_directory: str = ".",
                         filename_prefix: str = "reports") -> Tuple[str, str]:
    """
    Exports error and valid reports to separate CSV files.
    
    Args:
        error_reports: Dictionary of error reports from classify_reports_by_status
        valid_reports: Dictionary of valid reports from classify_reports_by_status
        output_directory: Directory where CSV files will be saved (default: current directory)
        filename_prefix: Prefix for the CSV filenames (default: "reports")
        
    Returns:
        tuple: (error_csv_path, valid_csv_path) - paths to the created CSV files
        
    Raises:
        OSError: If the output directory doesn't exist or isn't writable
    """
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    error_csv_path = os.path.join(output_directory, f"{filename_prefix}_errors_{timestamp}.csv")
    valid_csv_path = os.path.join(output_directory, f"{filename_prefix}_valid_{timestamp}.csv")
    
    # Define CSV headers
    headers = [
        "ReportNumber",
        "ReportDate",
        "FirstResponse_Reference", 
        "FirstResponse_LegalStatus",
        "FirstResponse_StatusReason",
        "FinalResponse_Reference",
        "FinalResponse_LegalStatus", 
        "FinalResponse_StatusReason",
        "HasFirstResponse",
        "HasFinalResponse"
    ]
    
    # Export error reports
    _write_reports_to_csv(error_reports, error_csv_path, headers)
    
    # Export valid reports  
    _write_reports_to_csv(valid_reports, valid_csv_path, headers)
    
    return error_csv_path, valid_csv_path

def _write_reports_to_csv(reports: Dict[str, Dict], csv_path: str, headers: List[str]) -> None:
    """
    Helper function to write reports data to a CSV file.
    
    Args:
        reports: Dictionary of reports to export
        csv_path: Path where the CSV file will be created
        headers: List of column headers for the CSV
    """
    try:
        with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            writer.writeheader()
            for report_number, report_data in reports.items():
                first_response = report_data.get("FirstResponse", {}) or {}
                final_response = report_data.get("FinalResponse", {}) or {}
                row = {
                    "ReportNumber": report_number,
                    "ReportDate": first_response.get("ReportDate", ""),
                    "FirstResponse_Reference": first_response.get("ReportInstanceReference", ""),
                    "FirstResponse_LegalStatus": first_response.get("ReportInstanceLegalStatusDesc", ""),
                    "FirstResponse_StatusReason": first_response.get("ReportInstanceStatusReason", ""),
                    "FinalResponse_Reference": final_response.get("ReportInstanceReference", ""),
                    "FinalResponse_LegalStatus": final_response.get("ReportInstanceLegalStatusDesc", ""),
                    "FinalResponse_StatusReason": final_response.get("ReportInstanceStatusReason", ""),
                    "HasFirstResponse": "Yes" if first_response else "No",
                    "HasFinalResponse": "Yes" if final_response else "No"
                }
                writer.writerow(row)
    except OSError as e:
        logging.error(f"Failed to write CSV file {csv_path}: {e}")

