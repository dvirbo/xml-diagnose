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


def parse_xml_files(directory: str) -> Tuple[Dict[str, Dict], Dict[str, Dict]]:
    """
    Parses XML files in the specified directory and extracts the relevant information from files with root tags
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

    # Get all XML files at once
    xml_files = [f for f in os.listdir(directory) if f.upper().endswith(".XML")]
    
    for filename in xml_files:
        file_path = os.path.join(directory, filename)
        
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
        except ET.ParseError as e:
            logging.warning(f"Could not parse {filename}: {e}")
            continue
        except Exception as e:
            logging.error(f"Unexpected error parsing {filename}: {e}")
            continue

        if root.tag == FIRST_RESPONSE_TAG:
            first_responses.update(_parse_first_response(root))
        elif root.tag == FINAL_RESPONSE_TAG:
            final_responses.update(_parse_final_response(root))
        else:
            logging.debug(f"Skipping {filename}: Unknown root tag '{root.tag}'")

    return first_responses, final_responses


def _parse_first_response(root) -> Dict[str, Dict]:
    """Extract data from FirstResponse XML."""
    report_number = _safe_get_text(root, "ReportNumber")
    if not report_number:
        logging.warning("FirstResponse missing ReportNumber, skipping")
        return {}
        
    valid_status = _safe_get_text(root, "ReportInstanceLegalStatusDesc")
    is_valid = valid_status == FIRST_STATUS_OK
    
    return { 
        report_number: {
            "ReportDate": _safe_get_text(root, "ReportDate"),
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
            status_category = "BOTH_INVALID"
        elif first_valid and not final_valid:
            status_category = "FIRST_VALID_FINAL_INVALID"
        elif not first_valid and final_valid:
            status_category = "FIRST_INVALID_FINAL_VALID"
        else:
            status_category = "BOTH_VALID"
        
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

'''

{'ReportNumber': '5236', 
'FirstResponse': {'ReportDate': '2025-07-13', 'ReportInstanceReference': '000100', 'ReportInstanceLegalStatusDesc': 'הדיווח נחסם: נקלט בעבר', 'valid': False, 'ReportInstanceStatusReason': 'קובץ דיווח בשם זהה נקלט בעבר', 'ReportInstanceStatusId': '', 'ReportInstanceLegalStatusId': ''}
, 'FinalResponse': {'ReportInstanceReference': '000100', 'ReportInstanceLegalStatusDesc': 'לא תקין', 'ReportInstanceStatusSeq': '', 'ReportInstanceLegalStatusSeq': '', 'valid': False, 'ReportInstanceStatusReason': 'הדיווח אינו תקין ולא נקלט ברשות.   ראה פירוט בדוח שגויים.  יש להעביר דיווח מתקן בהתאם לדוח שגויים ובתיאום מראש עם הרשות.', 'ErrorCode': '9638'}
, 'Status': {'first_response_valid': False, 'final_response_valid': False, 'overall_valid': False, 'status_category': 'BOTH_INVALID', 'first_status_desc': 'הדיווח נחסם: נקלט בעבר', 'final_status_desc': 'לא תקין', 'has_first_response': True, 'has_final_response': True}}

'''