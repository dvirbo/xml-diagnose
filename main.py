import os
import xml.etree.ElementTree as ET
import csv

INPUT_DIR = "C:\\Users\\dvirbo\\mizrahi\\documents_20250527"

def parse_xml_files(directory):
    """Parse all XML files in the directory and group by response type."""
    first_responses = {}
    final_responses = {}

    for filename in os.listdir(directory):
        if not filename.endswith(".XML"):
            continue
        path = os.path.join(directory, filename)
        tree = ET.parse(path)
        root = tree.getroot()

        if root.tag == "FirstResponse":
            report_number = root.findtext("ReportNumber", "").strip()
            report_ref = root.findtext("ReportInstanceReference", "").strip()
            first_responses[report_number] = {
                "xml": root,
                "reference": report_ref,
                "filename": filename
            }

        elif root.tag == "FinalResponse":
            ref = root.findtext("ReportMetaData/ReportInstanceReference", "").strip() 
            # Use ReportInstanceReference from metadata - **assume it matches FirstResponse***
            final_responses[ref] = {
                "xml": root,
                "filename": filename
            }

    return first_responses, final_responses


def build_report_data(first_responses, final_responses):
    """Combine data from matching FirstResponse and FinalResponse files."""
    error_reports = []
    valid_reports = []

    for report_number, first_data in first_responses.items():
        report_info = {
            "ReportNumber": report_number,
            "FirstResponseFile": first_data["filename"],
        }

        root = first_data["xml"]
        report_ref = first_data["reference"]
        status = root.findtext("ReportInstanceLegalStatusDesc", "").strip()
        report_info["FirstResponseStatus"] = status

        # Try to find a matching FinalResponse using the shared ReportInstanceReference
        final_data = final_responses.get(report_ref)
        if final_data:
            final_root = final_data["xml"]
            meta = final_root.find("ReportMetaData")
            report_info["FinalResponseFile"] = final_data["filename"]
            report_info["FinalResponseStatus"] = meta.findtext("ReportInstanceLegalStatusDesc", "").strip()
            report_info["FinalResponseReason"] = meta.findtext("ReportInstanceStatusReason", "").strip()

            error = final_root.find("ErrorReport/Error")
            if error is not None:
                report_info["ErrorCode"] = error.findtext("ErrorCode", "").strip()
                report_info["ErrorDescription"] = error.findtext("ErrorDescription", "").strip()

        # Separate valid and error reports
        if report_info.get("FinalResponseStatus") == "לא תקין":
            error_reports.append(report_info)
        else:
            valid_reports.append(report_info)

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
    error_reports, valid_reports = build_report_data(first_responses, final_responses)

    save_csv(error_reports, "error_reports.csv")
    save_csv(valid_reports, "valid_reports.csv")
    
    print(f"Total valid reports: {len(valid_reports)}")
    print(f"Total error reports: {len(error_reports)}")


if __name__ == "__main__":
    main()
