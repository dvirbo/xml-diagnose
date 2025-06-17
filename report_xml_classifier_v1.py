import os
import xml.etree.ElementTree as ET
import csv


INPUT_DIR = "C:\\Users\\dvirbo\\Desktop\\mizrahi\\documents_20250527"

def parse_xml_files(directory):
    """
    Parses XML files in the specified directory and extracts information from files with root tags
    "FirstResponse" and "FinalResponse".
    Args:
        directory (str): The path to the directory containing XML files.
    Returns:
        tuple: A tuple containing two dictionaries:
            - first_responses (dict): Maps ReportNumber to a dictionary with keys:
                - "ReportDate"
                - "ReportInstanceReference"
                - "ReportInstanceLegalStatusDesc"
                - "ReportInstanceStatusReason"
              Extracted from XML files with root tag "FirstResponse".
            - final_responses (dict): Maps ReportNumber to a dictionary with keys:
                - "ReportInstanceReference"
                - "ReportInstanceLegalStatusDesc"
                - "ReportInstanceStatusReason"
              Extracted from XML files with root tag "FinalResponse".
    Notes:
        - Only files ending with ".XML" are processed.
        - Assumes that the ReportNumber in "FinalResponse" matches the one in "FirstResponse".
        - If "ReportInstanceLegalStatusDesc" is "תקין" in "FinalResponse", "ReportInstanceStatusReason" is set to an empty string.
    """

    first_responses = {}
    final_responses = {}

    for filename in os.listdir(directory):
        if not filename.endswith(".XML"):
            continue
        path = os.path.join(directory, filename)
        tree = ET.parse(path)
        root = tree.getroot()

        if root.tag == "FirstResponse":
            ReportNumber = root.findtext("ReportNumber", "").strip()
            first_responses[ReportNumber] = {
                "ReportDate": root.findtext("ReportDate", "").strip(),
                "ReportInstanceReference": root.findtext("ReportInstanceReference", "").strip(),
                "ReportInstanceLegalStatusDesc": root.findtext("ReportInstanceLegalStatusDesc", "").strip(),
                "ReportInstanceStatusReason": root.findtext("ReportInstanceStatusReason", "").strip()
            }

        elif root.tag == "FinalResponse":
            ReportNumber = root.findtext("ReportMetaData/ReportNumber", "").strip()
            ReportInstanceLegalStatusDesc = root.findtext("ReportMetaData/ReportInstanceLegalStatusDesc", "").strip()
            if ReportInstanceLegalStatusDesc !=  "תקין":
                ReportInstanceStatusReason = root.findtext("ReportMetaData/ReportInstanceStatusReason", "").strip()
            else:
                ReportInstanceStatusReason = ""    
            # Use ReportNumber from metadata - **assume it matches FirstResponse***
            final_responses[ReportNumber] = {
                "ReportInstanceReference" : root.findtext("ReportMetaData/ReportInstanceReference", "").strip(),
                "ReportInstanceLegalStatusDesc": root.findtext("ReportMetaData/ReportInstanceLegalStatusDesc", "").strip(),
                "ReportInstanceStatusReason": ReportInstanceStatusReason
            }

    return first_responses, final_responses


def classify_reports_by_status(first_responses, final_responses):
    """
    Classifies merged responses into valid and error reports based on ReportInstanceLegalStatusDesc.

    Args:
        first_responses (dict): Output from parse_xml_files (FirstResponse data).
        final_responses (dict): Output from parse_xml_files (FinalResponse data).

    Returns:
        tuple: (error_reports, valid_reports), where each is a dict mapping ReportNumber to combined data.
    """
    error_reports = {}
    valid_reports = {}

    for report_number, first_data in first_responses.items():
        final_data = final_responses.get(report_number)
        if not final_data:
            continue  # No matching final response

        first_status = first_data.get("ReportInstanceLegalStatusDesc", "").strip()
        final_status = final_data.get("ReportInstanceLegalStatusDesc", "").strip()

        if not first_status or not final_status:
            continue  # Incomplete data, skip

        combined_data = {
            "ReportNumber": report_number,
            "FirstResponse": first_data,
            "FinalResponse": final_data
        }

        if final_status == "תקין":
            valid_reports[report_number] = combined_data
        else:
            error_reports[report_number] = combined_data

    return error_reports, valid_reports



def save_csv(data, filename):
    """Save list of report data to a CSV file."""
    if not data:
        print(f"No data to save to {filename}")
        return

    with open(filename, "w", newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
    print(f"Saved {len(data)} records to {filename}")


def main():
    first_responses, final_responses = parse_xml_files(INPUT_DIR)
    error_reports, valid_reports = classify_reports_by_status(first_responses, final_responses)

    save_csv(error_reports, "error_reports.csv")
    save_csv(valid_reports, "valid_reports.csv")
    
    print(f"Total valid reports: {len(valid_reports)}")
    print(f"Total error reports: {len(error_reports)}")


if __name__ == "__main__":
    main()
