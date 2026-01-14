"""XML parsing utilities for FirstResponse and FinalResponse XML files."""
import os
import logging
from typing import Dict, Tuple, Any, List
import xml.etree.ElementTree as ET

# Constants
FIRST_RESPONSE_TAG = "FirstResponse"
FINAL_RESPONSE_TAG = "FinalResponse"
LEGAL_STATUS_OK = "תקין"
FIRST_STATUS_OK = "קבצים תקינים"

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def parse_xml_files(directory: str, date_filter: str = None) -> Tuple[Dict[str, Dict], Dict[str, Dict]]:
    """
    Parses XML files from FirstResponses/ and FinalResponses/ subfolders.
    
    Args:
        directory (str): The path to Response_From_Rashut_05 directory containing FirstResponses/ and FinalResponses/ subfolders.
        date_filter (str): Optional date prefix (ddmmyyyy) to filter files by filename. Files must start with this date.
        
    Returns:
        tuple: A tuple containing two dictionaries:
            - first_responses (dict): Maps ReportNumber to extracted data from FirstResponse files
            - final_responses (dict): Maps ReportNumber to extracted data from FinalResponse files
            
    Raises:
        FileNotFoundError: If the directory or subfolders don't exist
        ET.ParseError: If XML files are malformed
    """
    if not os.path.exists(directory):
        raise FileNotFoundError("Directory not found: {}".format(directory))

    first_responses: Dict[str, Any] = {}
    final_responses: Dict[str, Any] = {}
    
    # Define subfolder paths
    first_responses_dir = os.path.join(directory, 'FirstResponses')
    final_responses_dir = os.path.join(directory, 'FinalResponses')
    
    # Parse FirstResponse XML files
    if os.path.exists(first_responses_dir):
        xml_files = [f for f in os.listdir(first_responses_dir) if f.upper().endswith(".XML")]
        # Filter by date prefix if provided
        if date_filter:
            xml_files = [f for f in xml_files if f.startswith(date_filter)]
            logging.info("Filtered FirstResponse files by date {}: {} files found".format(date_filter, len(xml_files)))
        for filename in xml_files:
            file_path = os.path.join(first_responses_dir, filename)
            try:
                tree = ET.parse(file_path)
                root = tree.getroot()
                if root.tag == FIRST_RESPONSE_TAG:
                    first_responses.update(_parse_first_response(root))
                else:
                    logging.debug("Skipping {}: Expected FirstResponse, got '{}'".format(filename, root.tag))
            except ET.ParseError as e:
                logging.warning("Could not parse {}: {}".format(filename, e))
                continue
            except Exception as e:
                logging.error("Unexpected error parsing {}: {}".format(filename, e))
                continue
    else:
        logging.warning("FirstResponses directory not found: {}".format(first_responses_dir))
    
    # Parse FinalResponse XML files
    if os.path.exists(final_responses_dir):
        xml_files = [f for f in os.listdir(final_responses_dir) if f.upper().endswith(".XML")]
        # Filter by date prefix if provided
        if date_filter:
            xml_files = [f for f in xml_files if f.startswith(date_filter)]
            logging.info("Filtered FinalResponse files by date {}: {} files found".format(date_filter, len(xml_files)))
        for filename in xml_files:
            file_path = os.path.join(final_responses_dir, filename)
            try:
                tree = ET.parse(file_path)
                root = tree.getroot()
                if root.tag == FINAL_RESPONSE_TAG:
                    final_responses.update(_parse_final_response(root))
                else:
                    logging.debug("Skipping {}: Expected FinalResponse, got '{}'".format(filename, root.tag))
            except ET.ParseError as e:
                logging.warning("Could not parse {}: {}".format(filename, e))
                continue
            except Exception as e:
                logging.error("Unexpected error parsing {}: {}".format(filename, e))
                continue
    else:
        logging.warning("FinalResponses directory not found: {}".format(final_responses_dir))

    return first_responses, final_responses


def _parse_first_response(root) -> Dict[str, Dict]:
    """Extract data from FirstResponse XML."""
    report_number = _safe_get_text(root, "ReportNumber")
    report_number = report_number.lstrip('0')
    if not report_number:
        logging.warning("FirstResponse missing ReportNumber, skipping")
        return {}
        
    valid_status = _safe_get_text(root, "ReportInstanceLegalStatusDesc")
    is_valid = valid_status == FIRST_STATUS_OK
    
    return { 
        report_number: {
            "ReportDate": _safe_get_text(root, "ReportDate"),
            "ReportInstanceDate": _safe_get_text(root, "ReportInstanceDate"),
            "ReportInstanceReference": _safe_get_text(root, "ReportInstanceReference"),
            "ReportInstanceLegalStatusDesc": valid_status,
            "valid": is_valid,
            "ReportInstanceStatusReason": _safe_get_text(root, "ReportInstanceStatusReason"),
            "ReportInstanceStatusId": _safe_get_text(root, "ReportInstanceStatusId"),
            "ReportInstanceLegalStatusId": _safe_get_text(root, "ReportInstanceLegalStatusId")
        }
    }


def _parse_final_response(root) -> Dict[str, Dict]:
    """Extract data from FinalResponse XML."""
    report_number = _safe_get_text(root, "ReportMetaData/ReportNumber")
    report_number = report_number.lstrip('0')
    if not report_number:
        logging.warning("FinalResponse missing ReportNumber, skipping")
        return {}
        
    legal_status = _safe_get_text(root, "ReportMetaData/ReportInstanceLegalStatusDesc")
    error_code = _safe_get_text(root, "ErrorReport/Error/ErrorCode")
    is_valid = legal_status == LEGAL_STATUS_OK
    
    data = {
        "ReportInstanceReference": _safe_get_text(root, "ReportMetaData/ReportInstanceReference"),
        "ReportInstanceLegalStatusDesc": legal_status,
        "ReportInstanceStatusSeq": _safe_get_text(root, "ReportMetaData/ReportInstanceLegalStatusSeq"),
        "ReportInstanceLegalStatusSeq": _safe_get_text(root, "ReportMetaData/ReportInstanceLegalStatusSeq"),
        "valid": is_valid
    }
    
    if is_valid:
        data.update({
            "ReportInstanceStatusReason": "",
            "mispar_tkina": _safe_get_text(root, "Mivzak/GeneralData/Statuses/Status/@id")
        })
    else:
        data.update({
            "ReportInstanceStatusReason": _safe_get_text(root, "ReportMetaData/ReportInstanceStatusReason"),
            "ErrorCode": error_code
        })
    
    return {report_number: data}


def _safe_get_text(element: ET.Element, xpath: str) -> str:
    """
    Safely extracts text from an XML element using XPath, returning empty string if not found.
    
    Args:
        element: The XML element to search in
        xpath: The XPath expression to find the target element
        
    Returns:
        str: The text content of the found element, or empty string if not found
    """
    if xpath.endswith("/@id"):
        # Handle attribute extraction
        attr_xpath = xpath[:-4]  # Remove /@id
        found_element = element.find(attr_xpath)
        return found_element.get("id", "") if found_element is not None else ""
    
    found_element = element.find(xpath)
    return found_element.text.strip() if found_element is not None and found_element.text else ""


def link_responses(first_responses: Dict[str, Dict], 
                  final_responses: Dict[str, Dict]) -> Dict[str, Dict]:
    """
    Links FirstResponse and FinalResponse data by ReportNumber and determines overall status.
    
    Args:
        first_responses: Dictionary mapping ReportNumber to FirstResponse data
        final_responses: Dictionary mapping ReportNumber to FinalResponse data
        
    Returns:
        Dict[str, Dict]: Combined report data with status indicators
    """
    reports: Dict[str, Dict] = {}

    # Process all reports that have final responses
    for report_number, final_data in final_responses.items():
        first_data = first_responses.get(report_number)
        
        # Determine status indicators
        first_valid = first_data.get("valid", False) if first_data else False
        final_valid = final_data.get("valid", False)
        
        # Overall status logic: both must be valid for report to be considered valid
        overall_valid = first_valid and final_valid
        
        # Status classification
        if first_data is None:
            status_category = "MISSING_FIRST_RESPONSE"
        elif not first_valid and not final_valid:
            status_category = "דיווח לא תקין"
        elif first_valid and not final_valid:
            status_category = "FIRST_VALID_FINAL_INVALID"
        elif not first_valid and final_valid:
            status_category = "FIRST_INVALID_FINAL_VALID"
        else:
            status_category = "דיווח תקין"
        
        combined_data = {
            "ReportNumber": report_number,
            "FirstResponse": first_data,
            "FinalResponse": final_data,
            "Status": {
                "first_response_valid": first_valid,
                "final_response_valid": final_valid,
                "overall_valid": overall_valid,
                "status_category": status_category,
                "first_status_desc": first_data.get("ReportInstanceLegalStatusDesc", "") if first_data else "",
                "final_status_desc": final_data.get("ReportInstanceLegalStatusDesc", ""),
                "has_first_response": first_data is not None,
                "has_final_response": True  # Always true since we iterate over final_responses
            }
        }

        reports[report_number] = combined_data

    return reports

