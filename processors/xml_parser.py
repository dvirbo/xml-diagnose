"""XML parsing utilities for FirstResponse and FinalResponse XML files."""
import os
import re
import logging
from typing import Dict, Tuple, Any, List, Set, Optional
import xml.etree.ElementTree as ET

from utils.report_utils import report_number_normalize, report_number_to_int

# Constants
FIRST_RESPONSE_TAG = "FirstResponse"
FINAL_RESPONSE_TAG = "FinalResponse"
LEGAL_STATUS_OK = "תקין"
FIRST_STATUS_OK = "קבצים תקינים"

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def _extract_report_number_from_filename(filename: str) -> Optional[int]:
    """
    Extract report_number from XML filename.
    Filename format: ReportDate-?-UAR-ST-ReportNumber-ReportInstanceReference.FinR.XML
    Example: 01012025-200005-UAR-ST-000000251531.41077558.FinR.XML
    
    Args:
        filename: The XML filename
        
    Returns:
        report_number as integer, or None if not found
    """
    # Pattern: UAR-ST- followed by a token (numeric or 000ACTxxxxxx) up to the next dot
    # Examples:
    #   UAR-ST-000000251531.41077558
    #   UAR-ST-000ACT000004.41077558
    match = re.search(r'UAR-ST-([^.]+)\.', filename)
    if match:
        token = match.group(1)
        return report_number_to_int(token)
    return None


def parse_xml_files(directory: str, date_filter: str = None, allowed_report_ids: Set[int] = None) -> Tuple[Dict[str, Dict], Dict[str, Dict]]:
    """
    Parses XML files from FirstResponses/ and FinalResponses/ subfolders.
    Filters files by report_number in filename BEFORE parsing if allowed_report_ids is provided.
    
    Args:
        directory (str): The path to Response_From_Rashut_05 directory containing FirstResponses/ and FinalResponses/ subfolders.
        date_filter (str): Optional date prefix (ddmmyyyy) to filter files by filename. Files must start with this date.
        allowed_report_ids (set): Optional set of report_id values (as integers) to filter by. Only files with matching report_number in filename will be parsed.
        
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
        
        # Filter by report_id BEFORE parsing if allowed_report_ids is provided
        filtered_count = 0
        if allowed_report_ids is not None:
            original_count = len(xml_files)
            xml_files = [f for f in xml_files if _extract_report_number_from_filename(f) in allowed_report_ids]
            filtered_count = original_count - len(xml_files)
            if filtered_count > 0:
                logging.info("Filtered out {} FirstResponse files not matching allowed report_ids (before parsing)".format(filtered_count))
        
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
        
        # Filter by report_id BEFORE parsing if allowed_report_ids is provided
        filtered_count = 0
        if allowed_report_ids is not None:
            original_count = len(xml_files)
            xml_files = [f for f in xml_files if _extract_report_number_from_filename(f) in allowed_report_ids]
            filtered_count = original_count - len(xml_files)
            if filtered_count > 0:
                logging.info("Filtered out {} FinalResponse files not matching allowed report_ids (before parsing)".format(filtered_count))
        
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
    raw_report_number = _safe_get_text(root, "ReportNumber")
    normalized_report_number = report_number_normalize(raw_report_number)
    if not normalized_report_number:
        logging.warning("FirstResponse missing ReportNumber, skipping")
        return {}
        
    valid_status = _safe_get_text(root, "ReportInstanceLegalStatusDesc")
    is_valid = valid_status == FIRST_STATUS_OK
    
    return { 
        normalized_report_number: {
            "ReportDate": _safe_get_text(root, "ReportDate"),
            "ReportInstanceDate": _safe_get_text(root, "ReportInstanceDate"),
            "ReportInstanceReference": _safe_get_text(root, "ReportInstanceReference"),
            "ReportInstanceLegalStatusDesc": valid_status,
            "valid": is_valid,
            "ReportInstanceStatusReason": _safe_get_text(root, "ReportInstanceStatusReason"),
            "ReportInstanceStatusId": _safe_get_text(root, "ReportInstanceStatusId"),
            "ReportInstanceLegalStatusId": _safe_get_text(root, "ReportInstanceLegalStatusId"),
            # Preserve the original ReportNumber as received from Rashut
            "ReportNumberOriginal": raw_report_number
        }
    }


def _parse_final_response(root) -> Dict[str, Dict]:
    """Extract data from FinalResponse XML."""
    raw_report_number = _safe_get_text(root, "ReportMetaData/ReportNumber")
    normalized_report_number = report_number_normalize(raw_report_number)
    if not normalized_report_number:
        logging.warning("FinalResponse missing ReportNumber, skipping")
        return {}
        
    legal_status = _safe_get_text(root, "ReportMetaData/ReportInstanceLegalStatusDesc")
    # Primary (older structure): ErrorReport directly under FinalResponse
    error_code = _safe_get_text(root, "ErrorReport/Error/ErrorCode")
    error_description = _safe_get_text(root, "ErrorReport/Error/ErrorDescription")
    # Fallback (prod structure): ErrorReport under Mivzak with namespace
    if not error_code or not error_description:
        ns = {'ns': 'http://www.justice.gov.il/IMPA/RLS/Flash/Responses'}
        try:
            err_elem = root.find(".//Mivzak/ns:ErrorReport/ns:Error", ns)
            if err_elem is not None:
                if not error_code:
                    code_elem = err_elem.find("ns:ErrorCode", ns)
                    if code_elem is not None and code_elem.text:
                        error_code = code_elem.text.strip()
                if not error_description:
                    desc_elem = err_elem.find("ns:ErrorDescription", ns)
                    if desc_elem is not None and desc_elem.text:
                        error_description = desc_elem.text.strip()
        except Exception as e:
            logging.debug("Fallback parsing for ErrorReport under Mivzak failed: {}".format(e))
    is_valid = legal_status == LEGAL_STATUS_OK
    
    # Preserve original ReportNumber for display
    report_number_original = raw_report_number
    data = {
        "ReportInstanceReference": _safe_get_text(root, "ReportMetaData/ReportInstanceReference"),
        "ReportInstanceLegalStatusDesc": legal_status,
        "ReportInstanceStatusSeq": _safe_get_text(root, "ReportMetaData/ReportInstanceLegalStatusSeq"),
        "ReportInstanceLegalStatusSeq": _safe_get_text(root, "ReportMetaData/ReportInstanceLegalStatusSeq"),
        "valid": is_valid
    }
    
    # Always try to extract mispar_tkina, regardless of validity
    mispar_tkina_value = _safe_get_text(root, "Mivzak/GeneralData/Statuses/Status/@id")
    logging.debug("Extracted mispar_tkina from XML for report {}: '{}' (is_valid={})".format(
        normalized_report_number, mispar_tkina_value, is_valid))
    
    if is_valid:
        data.update({
            "ReportInstanceStatusReason": "",
            "mispar_tkina": mispar_tkina_value
        })
    else:
        data.update({
            "ReportInstanceStatusReason": _safe_get_text(root, "ReportMetaData/ReportInstanceStatusReason"),
            "ErrorCode": error_code,
            "ErrorDescription": error_description,
            "mispar_tkina": mispar_tkina_value  # Include mispar_tkina even for invalid responses
        })
    
    logging.debug("FinalResponse data for report {}: mispar_tkina='{}', valid={}".format(
        normalized_report_number, data.get('mispar_tkina', ''), is_valid))
    
    return {normalized_report_number: data}


def _safe_get_text(element: ET.Element, xpath: str) -> str:
    """
    Safely extracts text from an XML element using XPath, returning empty string if not found.
    Handles XML namespaces properly.
    
    Args:
        element: The XML element to search in
        xpath: The XPath expression to find the target element
        
    Returns:
        str: The text content of the found element, or empty string if not found
    """
    # Namespace for Mivzak/GeneralData elements
    namespace = {'ns': 'http://www.justice.gov.il/IMPA/RLS/Flash/Responses'}
    
    # Check if this path involves namespaced elements (GeneralData and its children are namespaced)
    needs_namespace = 'GeneralData' in xpath
    
    if xpath.endswith("/@id"):
        # Handle attribute extraction
        attr_xpath = xpath[:-4]  # Remove /@id
        
        if needs_namespace:
            # Convert path like "Mivzak/GeneralData/Statuses/Status" to namespace-aware
            # Mivzak is not namespaced, but GeneralData and children are
            parts = attr_xpath.split('/')
            ns_path_parts = []
            for part in parts:
                if part == 'Mivzak':
                    ns_path_parts.append(part)
                elif part in ['GeneralData', 'Statuses', 'Status', 'ErrorReport']:
                    # These elements are in the namespace
                    ns_path_parts.append('ns:{}'.format(part))
                else:
                    ns_path_parts.append(part)
            
            # Build the namespace-aware path
            # If starting from root, use absolute path; otherwise use relative
            if attr_xpath.startswith('Mivzak'):
                ns_path = '/'.join(ns_path_parts)
            else:
                ns_path = './/' + '/'.join(ns_path_parts)
            
            logging.debug("Looking for attribute with namespaced path: {}".format(ns_path))
            found_element = element.find(ns_path, namespace)
            result = found_element.get("id", "") if found_element is not None else ""
            logging.debug("Found element: {}, result: '{}'".format(found_element is not None, result))
            return result
        else:
            found_element = element.find(attr_xpath)
            return found_element.get("id", "") if found_element is not None else ""
    
    # For text extraction
    if needs_namespace:
        # Convert path to namespace-aware
        parts = xpath.split('/')
        ns_path_parts = []
        for part in parts:
            if part == 'Mivzak':
                ns_path_parts.append(part)
            elif part in ['GeneralData', 'Statuses', 'Status', 'ErrorReport', 'ReportNumber', 'ReportFileName', 
                          'SourceId', 'SourceName', 'ReportFlashSeq']:
                # These elements are in the namespace
                ns_path_parts.append('ns:{}'.format(part))
            else:
                ns_path_parts.append(part)
        
        # Build the namespace-aware path
        if xpath.startswith('Mivzak'):
            ns_path = '/'.join(ns_path_parts)
        else:
            ns_path = './/' + '/'.join(ns_path_parts)
        
        logging.debug("Looking for text with namespaced path: {}".format(ns_path))
        found_element = element.find(ns_path, namespace)
        result = found_element.text.strip() if found_element is not None and found_element.text else ""
        logging.debug("Found element: {}, result: '{}'".format(found_element is not None, result))
        return result
    else:
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
            # Normalized key as internal ReportNumber
            "ReportNumber": report_number,
            # Preserve original ReportNumber for display (prefer FinalResponse, then FirstResponse)
            "ReportNumberOriginal": (
                (final_data or {}).get("ReportNumberOriginal")
                or (first_data or {}).get("ReportNumberOriginal")
                or report_number
            ),
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

