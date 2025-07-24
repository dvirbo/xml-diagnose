import logging
import time
import gc
from typing import List, Dict, Optional
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed

from api.alert_updater_optimized import AlertUpdaterOptimized
from api.api_session import end_session
from database.db_manager_optimized import DatabaseManagerOptimized
from processors.xml_processor_optimized import XMLReportProcessorOptimized


logging.basicConfig(level=logging.INFO)


@dataclass
class ProcessingResult:
    """Data class to hold processing results with performance metrics"""
    error_csv: Optional[str] = None
    valid_csv: Optional[str] = None
    summary_report: List[Dict] = None
    error_reports: List[Dict] = None
    valid_reports: List[Dict] = None
    
    # Performance metrics
    xml_processing_time: float = 0.0
    csv_export_time: float = 0.0
    database_update_time: float = 0.0
    alert_update_time: float = 0.0
    total_processing_time: float = 0.0
    
    # Statistics
    files_processed: int = 0
    reports_classified: int = 0
    database_records_updated: int = 0
    alerts_updated: int = 0


class XMLDiagnosePipelineOptimized:
    """Optimized main pipeline with concurrent processing and performance monitoring"""
    
    def __init__(self, input_directory: str, target_date: str, 
                 max_xml_workers: int = None, max_db_connections: int = 5,
                 max_api_workers: int = 5):
        self.input_date = target_date
        self.input_directory = input_directory
        
        # Initialize optimized components
        self.xml_processor = XMLReportProcessorOptimized(
            input_directory, 
            target_date, 
            max_workers=max_xml_workers
        )
        self.db_manager = DatabaseManagerOptimized(max_connections=max_db_connections)
        self.alert_updater = AlertUpdaterOptimized(
            max_workers=max_api_workers, 
            max_sessions=min(3, max_api_workers)
        )
        
        # Performance tracking
        self.pipeline_start_time = None
        
    def run(self) -> ProcessingResult:
        """Execute the complete optimized processing pipeline"""
        self.pipeline_start_time = time.time()
        result = ProcessingResult()
        
        try:
            logging.info("Starting optimized XML diagnosis pipeline...")
            
            # Step 1: Process XML files with timing
            xml_start = time.time()
            result.error_reports, result.valid_reports = self.xml_processor.process_xml_files(self.input_date)
            result.xml_processing_time = time.time() - xml_start
            result.reports_classified = len(result.error_reports) + len(result.valid_reports)
            
            # Step 2: Export reports to CSV with timing
            csv_start = time.time()
            result.error_csv, result.valid_csv = self.xml_processor.export_reports(
                result.error_reports, result.valid_reports
            )
            result.csv_export_time = time.time() - csv_start
            
            # Step 3: Update database with timing
            db_start = time.time()
            if self.db_manager.connect():
                # Convert to lists if they're dictionaries, or use as-is if already lists
                valid_reports = (result.valid_reports if isinstance(result.valid_reports, list) 
                               else [result.valid_reports] if result.valid_reports else [])
                error_reports = (result.error_reports if isinstance(result.error_reports, list) 
                               else [result.error_reports] if result.error_reports else [])
                all_reports = valid_reports + error_reports
                
                # Use concurrent database updates for large datasets
                if len(all_reports) > 100:
                    result.summary_report = self.db_manager.update_reports_concurrent(all_reports)
                else:
                    result.summary_report = self.db_manager.update_reports(all_reports)
                    
                result.database_records_updated = len(result.summary_report)
            else:
                logging.error("Skipping database update due to connection failure")
                result.summary_report = []
            
            result.database_update_time = time.time() - db_start
            
            # Step 4: Update alerts with timing
            alert_start = time.time()
            if result.summary_report and self.alert_updater.initialize_session():
                self.alert_updater.update_alerts(result.summary_report)
                result.alerts_updated = len(result.summary_report)
            else:
                if not result.summary_report:
                    logging.info("No alerts to update (empty summary report)")
                else:
                    logging.error("Skipping alert updates due to session failure")
            
            result.alert_update_time = time.time() - alert_start
            result.total_processing_time = time.time() - self.pipeline_start_time
            
            # Log performance summary
            self._log_performance_summary(result)
            
            logging.info("Optimized pipeline execution completed successfully")
            
        except Exception as e:
            logging.error(f"Optimized pipeline execution failed: {str(e)}")
            result.total_processing_time = time.time() - self.pipeline_start_time if self.pipeline_start_time else 0
            raise
        
        finally:
            # Cleanup resources
            self._cleanup_resources()
            
            # Force garbage collection to free memory
            gc.collect()
        
        return result
    
    def _log_performance_summary(self, result: ProcessingResult):
        """Log detailed performance metrics"""
        logging.info("=== PERFORMANCE SUMMARY ===")
        logging.info(f"Total Processing Time: {result.total_processing_time:.2f}s")
        logging.info(f"XML Processing Time: {result.xml_processing_time:.2f}s "
                    f"({result.xml_processing_time/result.total_processing_time*100:.1f}%)")
        logging.info(f"CSV Export Time: {result.csv_export_time:.2f}s "
                    f"({result.csv_export_time/result.total_processing_time*100:.1f}%)")
        logging.info(f"Database Update Time: {result.database_update_time:.2f}s "
                    f"({result.database_update_time/result.total_processing_time*100:.1f}%)")
        logging.info(f"Alert Update Time: {result.alert_update_time:.2f}s "
                    f"({result.alert_update_time/result.total_processing_time*100:.1f}%)")
        
        logging.info(f"Reports Classified: {result.reports_classified}")
        logging.info(f"Database Records Updated: {result.database_records_updated}")
        logging.info(f"Alerts Updated: {result.alerts_updated}")
        
        # Calculate throughput metrics
        if result.total_processing_time > 0:
            reports_per_second = result.reports_classified / result.total_processing_time
            logging.info(f"Processing Throughput: {reports_per_second:.2f} reports/second")
        
        # Log component-specific performance stats
        db_stats = self.db_manager.get_performance_stats()
        alert_stats = self.alert_updater.get_performance_stats()
        
        logging.info(f"Database Stats: {db_stats}")
        logging.info(f"Alert Updater Stats: {alert_stats}")
        logging.info("=== END PERFORMANCE SUMMARY ===")
    
    def _cleanup_resources(self):
        """Clean up all resources and connections"""
        try:
            # Close database connections
            self.db_manager.close()
            
            # Close API sessions
            if hasattr(self.alert_updater, 'primary_session') and self.alert_updater.primary_session:
                end_session(self.alert_updater.primary_session)
            
            # Close session pool
            self.alert_updater.close()
            
            logging.info("Resource cleanup completed")
            
        except Exception as e:
            logging.error(f"Error during resource cleanup: {e}")
    
    def get_performance_insights(self) -> Dict:
        """Get performance insights and recommendations"""
        db_stats = self.db_manager.get_performance_stats()
        alert_stats = self.alert_updater.get_performance_stats()
        
        insights = {
            'database_performance': db_stats,
            'api_performance': alert_stats,
            'recommendations': []
        }
        
        # Generate recommendations based on performance data
        if db_stats.get('average_time_per_operation', 0) > 1.0:
            insights['recommendations'].append(
                "Database operations are slow. Consider optimizing queries or increasing connection pool size."
            )
        
        if alert_stats.get('success_rate', 100) < 95:
            insights['recommendations'].append(
                f"API success rate is {alert_stats.get('success_rate', 0):.1f}%. "
                "Consider implementing better retry logic or checking API endpoint health."
            )
        
        if alert_stats.get('average_time_per_update', 0) > 5.0:
            insights['recommendations'].append(
                "API calls are slow. Consider increasing concurrent workers or optimizing request payload."
            )
        
        return insights


# Backward compatibility
class XMLDiagnosePipeline(XMLDiagnosePipelineOptimized):
    """Backward compatibility alias"""
    
    def __init__(self, input_directory: str, target_date: str):
        # Use default optimization settings for backward compatibility
        super().__init__(input_directory, target_date)