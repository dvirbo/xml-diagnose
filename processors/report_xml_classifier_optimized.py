import os
import csv
import logging
import gc
from datetime import datetime
from typing import Dict, Tuple, Any, List
from concurrent.futures import ThreadPoolExecutor, as_completed
import xml.etree.ElementTree as ET

# Constants
FIRST_RESPONSE_TAG = "FirstResponse"
FINAL_RESPONSE_TAG = "FinalResponse"
LEGAL_STATUS_OK = "תקין"

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def parse_xml_files_concurrent(directory: str, input_date: str, max_workers: int = 8) -> Tuple[Dict[str, Dict], Dict[str, Dict]]:
    """
    Optimized XML file parsing with concurrent processing.
    
    Args:
        directory (str): The path to the directory containing XML files.
        input_date (str): Date filter in ddmmyyyy format
        max_workers (int): Maximum number of worker threads for concurrent processing
        
    Returns:
        tuple: A tuple containing two dictionaries for first and final responses
    """
    if not os.path.exists(directory):
        raise FileNotFoundError(f"Directory not found: {directory}")

    # Get all XML files matching the date filter
    xml_files = []
    for filename in os.listdir(directory):
        if (filename.upper().endswith(".XML") and 
            len(filename) >= 8 and 
            filename[:8] == input_date):
            xml_files.append(os.path.join(directory, filename))
    
    if not xml_files:
        logging.warning(f"No XML files found for date {input_date}")
        return {}, {}
    
    logging.info(f"Found {len(xml_files)} XML files to process")
    
    first_responses: Dict[str, Any] = {}
    final_responses: Dict[str, Any] = {}
    
    # Process files concurrently
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all file parsing tasks
        future_to_file = {
            executor.submit(_parse_single_xml_file, file_path): file_path 
            for file_path in xml_files
        }
        
        # Collect results as they complete
        for future in as_completed(future_to_file):
            file_path = future_to_file[future]
            try:
                result = future.result()
                if result:
                    response_type, report_number, data = result
                    if response_type == FIRST_RESPONSE_TAG:
                        first_responses[report_number] = data
                    elif response_type == FINAL_RESPONSE_TAG:
                        final_responses[report_number] = data
            except Exception as e:
                logging.error(f"Error processing {file_path}: {e}")
    
    logging.info(f"Concurrent parsing completed: {len(first_responses)} first, {len(final_responses)} final")
    return first_responses, final_responses


def _parse_single_xml_file(file_path: str) -> Tuple[str, str, Dict] | None:
    """
    Parse a single XML file and extract relevant data.
    
    Args:
        file_path (str): Path to the XML file
        
    Returns:
        tuple: (response_type, report_number, data) or None if parsing fails
    """
    try:
        # Use iterparse for memory efficiency on large files
        for event, elem in ET.iterparse(file_path, events=('start', 'end')):
            if event == 'start' and elem.tag in (FIRST_RESPONSE_TAG, FINAL_RESPONSE_TAG):
                root = elem
                break
        else:
            return None
        
        if root.tag == FIRST_RESPONSE_TAG:
            report_number = _safe_get_text(root, "ReportNumber")
            if report_number:
                data = {
                    "ReportDate": _safe_get_text(root, "ReportDate"),
                    "ReportInstanceReference": _safe_get_text(root, "ReportInstanceReference"),
                    "ReportInstanceLegalStatusDesc": _safe_get_text(root, "ReportInstanceLegalStatusDesc"),
                    "ReportInstanceStatusReason": _safe_get_text(root, "ReportInstanceStatusReason")
                }
                return (FIRST_RESPONSE_TAG, report_number, data)
                
        elif root.tag == FINAL_RESPONSE_TAG:
            report_number = _safe_get_text(root, "ReportMetaData/ReportNumber")
            if report_number:
                legal_status = _safe_get_text(root, "ReportMetaData/ReportInstanceLegalStatusDesc")
                status_reason = "" if legal_status == LEGAL_STATUS_OK else _safe_get_text(root, "ReportMetaData/ReportInstanceStatusReason")
                data = {
                    "ReportInstanceReference": _safe_get_text(root, "ReportMetaData/ReportInstanceReference"),
                    "ReportInstanceLegalStatusDesc": legal_status,
                    "ReportInstanceStatusReason": status_reason
                }
                return (FINAL_RESPONSE_TAG, report_number, data)
                
    except ET.ParseError as e:
        logging.warning(f"Could not parse {file_path}: {e}")
    except Exception as e:
        logging.error(f"Unexpected error parsing {file_path}: {e}")
    
    return None


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
    Optimized classification with memory management.
    """
    error_reports: Dict[str, Any] = {}
    valid_reports: Dict[str, Any] = {}

    for report_number, final_data in final_responses.items():
        first_data = first_responses.get(report_number)
        combined_data = {
            "ReportNumber": report_number,
            "FinalResponse": final_data,
            "FirstResponse": first_data
        }
        
        final_status = final_data.get("ReportInstanceLegalStatusDesc", "")
        if final_status == LEGAL_STATUS_OK:
            valid_reports[report_number] = combined_data
        else:
            error_reports[report_number] = combined_data
    
    # Force garbage collection to free memory
    gc.collect()
    
    return error_reports, valid_reports


def export_reports_to_csv_optimized(error_reports: Dict[str, Dict], 
                                   valid_reports: Dict[str, Dict], 
                                   output_directory: str = ".",
                                   filename_prefix: str = "reports") -> Tuple[str, str]:
    """
    Optimized CSV export with better memory management and I/O performance.
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
    
    # Export with concurrent I/O and buffering
    with ThreadPoolExecutor(max_workers=2) as executor:
        error_future = executor.submit(_write_reports_to_csv_optimized, error_reports, error_csv_path, headers)
        valid_future = executor.submit(_write_reports_to_csv_optimized, valid_reports, valid_csv_path, headers)
        
        # Wait for both to complete
        error_future.result()
        valid_future.result()
    
    return error_csv_path, valid_csv_path


def _write_reports_to_csv_optimized(reports: Dict[str, Dict], csv_path: str, headers: List[str], buffer_size: int = 8192) -> None:
    """
    Optimized CSV writing with buffering and batch processing.
    """
    try:
        with open(csv_path, 'w', newline='', encoding='utf-8', buffering=buffer_size) as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            writer.writeheader()
            
            # Process reports in batches to reduce memory usage
            batch_size = 1000
            report_items = list(reports.items())
            
            for i in range(0, len(report_items), batch_size):
                batch = report_items[i:i + batch_size]
                rows = []
                
                for report_number, report_data in batch:
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
                    rows.append(row)
                
                # Write batch to file
                writer.writerows(rows)
                
                # Clear batch from memory
                del rows, batch
                
            # Force garbage collection
            gc.collect()
            
    except OSError as e:
        logging.error(f"Failed to write CSV file {csv_path}: {e}")
        raise


# Keep original functions for backward compatibility
def parse_xml_files(directory: str, input_date: str) -> Tuple[Dict[str, Dict], Dict[str, Dict]]:
    """Backward compatibility wrapper for the original function."""
    return parse_xml_files_concurrent(directory, input_date, max_workers=4)


def export_reports_to_csv(error_reports: Dict[str, Dict], 
                         valid_reports: Dict[str, Dict], 
                         output_directory: str = ".",
                         filename_prefix: str = "reports") -> Tuple[str, str]:
    """Backward compatibility wrapper for the original function."""
    return export_reports_to_csv_optimized(error_reports, valid_reports, output_directory, filename_prefix)