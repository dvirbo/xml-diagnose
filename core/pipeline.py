"""Main pipeline for processing XML reports."""
import logging
from typing import List, Dict, Optional, Set
from database.manager import DatabaseManager
from processors.xml_processor import XMLReportProcessor
from utils.config_loader import load_config
from utils.report_exporter import export_reports_to_csv
from utils.report_utils import report_number_to_int, report_id_to_rashut_display


logging.basicConfig(level=logging.INFO)

NO_RESPONSE_ERROR_DESCRIPTION = 'לא התקבלה תגובה מהרשות'


class ProcessingResult:
    """Data class to hold processing results (Python 3.6 compatible)"""
    def __init__(self, summary_reports=None, reports=None):
        self.summary_reports = summary_reports
        self.reports = reports


def _report_ids_from_export_rows(export_rows: List[Dict]) -> Set[int]:
    ids = set()
    for row in export_rows:
        rid = report_number_to_int(row.get('report_id'))
        if rid is not None:
            ids.add(rid)
    return ids


def _yn_char_to_status(value) -> str:
    if value is None:
        return ''
    normalized = str(value).strip().upper()
    if normalized == 'Y':
        return 'תקין'
    if normalized == 'N':
        return 'לא תקין'
    return ''


def _build_export_row_from_log(log_row: Dict) -> Dict:
    """Build a CSV row from IMP_REPORT_LOG for reports answered in a prior run."""
    first_orig = log_row.get('first_response_orig')
    final_valid = log_row.get('final_response_valid')
    first_status = _yn_char_to_status(first_orig)
    final_status = _yn_char_to_status(final_valid)
    overall_valid = (
        str(first_orig or '').strip().upper() == 'Y'
        and str(final_valid or '').strip().upper() == 'Y'
    )
    report_id = log_row['report_id']
    return {
        'first_status': first_status,
        'final_status': final_status,
        'error_code': '',
        'error_description': '' if overall_valid else (log_row.get('status_desc') or ''),
        'report_folder': log_row.get('sar_folder_name') or '',
        'report_id': report_id_to_rashut_display(report_id),
        'alert_id': str(log_row.get('alert_id') or ''),
    }


def _build_no_response_placeholders(
    missing_ids: Set[int],
    report_metadata: Dict[int, Dict],
) -> List[Dict]:
    placeholder_rows = []
    for rid in sorted(missing_ids):
        meta = report_metadata.get(rid, {})
        placeholder_rows.append({
            'first_status': '',
            'final_status': '',
            'error_code': '',
            'error_description': NO_RESPONSE_ERROR_DESCRIPTION,
            'report_folder': meta.get('report_folder', ''),
            'report_id': report_id_to_rashut_display(rid),
            'alert_id': str(meta.get('alert_id', '') or ''),
        })
    return placeholder_rows


def _sort_export_rows(export_rows: List[Dict]) -> List[Dict]:
    return sorted(
        export_rows,
        key=lambda row: report_number_to_int(row.get('report_id')) or 0,
    )


class XMLDiagnosePipeline:
    """Main pipeline for processing XML reports"""
    
    def __init__(self, input_directory: str, date_filter: str = None, use_query_filter: bool = True):
        self.input_directory = input_directory
        self.date_filter = date_filter
        self.use_query_filter = use_query_filter
        self.db_manager = DatabaseManager()
        self.xml_processor = None  # Will be initialized after getting report_ids
    
    def run(self) -> ProcessingResult:
        """Execute the complete processing pipeline"""
        result = ProcessingResult()
        
        try:
            # Step 0: Get report_ids for XML filtering and CSV scope
            allowed_report_ids = None
            latest_process_ids = set()
            initial_pending_ids = set()
            reports_sent_count = 0
            if self.use_query_filter:
                if not self.db_manager.connect():
                    logging.error("Failed to connect to database. Cannot filter by query results.")
                    logging.info("Continuing without query filter...")
                else:
                    try:
                        scope = self.db_manager.get_reports_to_process()
                        allowed_report_ids = scope['allowed_report_ids']
                        latest_process_ids = scope['latest_process_ids']
                        initial_pending_ids = scope['no_response_ids']
                        if allowed_report_ids:
                            logging.info(
                                "Using query filter: {} report_ids (latest + no-response)".format(
                                    len(allowed_report_ids)
                                )
                            )
                        else:
                            logging.warning(
                                "No reports found from latest process or no-response query. "
                                "Processing all files."
                            )
                    except Exception as e:
                        logging.error("Error getting reports to process: {}".format(e))
                        logging.info("Continuing without query filter...")
            
            # Step 1: Process XML files (filtering by allowed_report_ids)
            # Date filter is no longer used for XML selection; we keep the CLI date parameter
            # only for compatibility and logging.
            self.xml_processor = XMLReportProcessor(self.input_directory, None, allowed_report_ids)
            result.reports = self.xml_processor.process_xml_files()
            
            # Step 2: Update database with filtered results
            if not self.db_manager.connection:
                if not self.db_manager.connect():
                    logging.error("Skipping database update due to connection failure")
                    return result
            
            all_reports = result.reports if isinstance(result.reports, list) else [result.reports] if result.reports else []
            result.summary_reports = self.db_manager.update_reports(all_reports)
            
            # Step 3: Build CSV for latest process + initial pending pool (both NULL at run start)
            parsed_rows = list(result.summary_reports) if isinstance(result.summary_reports, list) else []
            reports_received_count = 0

            if self.use_query_filter and self.db_manager.connection:
                csv_scope_ids = latest_process_ids | initial_pending_ids
                if csv_scope_ids:
                    still_no_response_ids, no_response_metadata = (
                        self.db_manager.get_reports_no_response()
                    )

                    export_rows = [
                        row for row in parsed_rows
                        if report_number_to_int(row.get('report_id')) in csv_scope_ids
                    ]
                    existing_ids = _report_ids_from_export_rows(export_rows)

                    # Answered in scope but not parsed this run → load from IMP_REPORT_LOG
                    answered_missing = (csv_scope_ids - still_no_response_ids) - existing_ids
                    if answered_missing:
                        log_rows = self.db_manager.get_report_log_by_ids(sorted(answered_missing))
                        for log_row in log_rows:
                            export_rows.append(_build_export_row_from_log(log_row))
                            existing_ids.add(log_row['report_id'])

                    # Still no response (both NULL after update) within CSV scope → placeholders
                    placeholder_ids = (csv_scope_ids & still_no_response_ids) - existing_ids
                    if placeholder_ids:
                        export_rows.extend(
                            _build_no_response_placeholders(placeholder_ids, no_response_metadata)
                        )

                    reports_sent_count = len(latest_process_ids)
                    reports_received_count = len(initial_pending_ids - still_no_response_ids)
                    logging.info(
                        "CSV scope: {} rows ({} latest + {} pending at start), "
                        "{} sent, {} pending received from Rashut".format(
                            len(export_rows),
                            len(latest_process_ids),
                            len(initial_pending_ids),
                            reports_sent_count,
                            reports_received_count,
                        )
                    )
                else:
                    export_rows = []
            else:
                export_rows = parsed_rows
                reports_received_count = len(export_rows)

            export_rows = _sort_export_rows(export_rows)

            if export_rows:
                config = load_config()
                export_dir = config.get('export_directory', '/var/Reports_To_Send')
                try:
                    export_reports_to_csv(
                        export_rows,
                        export_dir,
                        reports_sent_to_rashut=reports_sent_count,
                        reports_parsed=reports_received_count,
                    )
                except Exception as e:
                    logging.error("CSV export failed: {}".format(e))
            else:
                logging.info("No reports to export, skipping CSV export")
            
            logging.info("Pipeline execution completed successfully")
            
        except Exception as e:
            logging.error("Pipeline execution failed: {}".format(str(e)))
            raise
        
        finally:
            self.db_manager.close()
        
        return result
