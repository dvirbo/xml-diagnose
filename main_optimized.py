import logging
from logging.handlers import TimedRotatingFileHandler
import os
import json
import time
from datetime import datetime
from processors.xml_diagnose_optimized import XMLDiagnosePipelineOptimized


def load_config(config_file: str = 'config_optimized.json'):
    """Load configuration from optimized config file with fallback to original."""
    try:
        with open(config_file, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logging.warning(f"Optimized config file {config_file} not found, falling back to config.json")
        with open('config.json', 'r') as f:
            config = json.load(f)
            # Add default performance settings for backward compatibility
            config['performance_settings'] = {
                'xml_processing': {'max_workers': 'auto', 'batch_size': 1000},
                'database': {'max_connections': 5, 'batch_size': 100},
                'api': {'max_workers': 5, 'max_sessions': 3}
            }
            return config


def setup_logging(config):
    """Setup optimized logging configuration."""
    LOG_DIR = config.get('log_directory', 'logs')
    
    # Ensure log directory exists
    os.makedirs(LOG_DIR, exist_ok=True)
    
    # Use base filename, let TimedRotatingFileHandler handle the date
    log_file = os.path.join(LOG_DIR, 'PipelineProcess_Optimized.log')
    
    # Configure logging with performance optimizations
    handler = TimedRotatingFileHandler(
        log_file, when='midnight', interval=1, backupCount=7, encoding='utf-8'
    )
    
    # More detailed formatter for performance tracking
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - [%(funcName)s:%(lineno)d] - %(message)s'
    )
    handler.setFormatter(formatter)
    
    # Clear any existing handlers and set up logging
    logging.getLogger().handlers.clear()
    
    # Set log level based on configuration
    log_level = getattr(logging, config.get('log_level', 'INFO').upper())
    logging.basicConfig(level=log_level, handlers=[handler])
    
    # Test logging
    logging.info("Optimized logging system initialized successfully")


def cleanup_logs(config):
    """Cleanup old log files based on retention policy."""
    LOG_DIR = config.get('log_directory', 'logs')
    RETENTION_DAYS = config.get('retention_days', 90)
    
    if not os.path.exists(LOG_DIR):
        return
    
    now = datetime.now()
    cleaned_count = 0
    
    for filename in os.listdir(LOG_DIR):
        file_path = os.path.join(LOG_DIR, filename)
        if os.path.isfile(file_path):
            file_creation_time = datetime.fromtimestamp(os.path.getctime(file_path))
            if (now - file_creation_time).days > RETENTION_DAYS:
                try:
                    os.remove(file_path)
                    cleaned_count += 1
                    logging.info(f"Removed old log file: {filename}")
                except OSError as e:
                    logging.error(f"Failed to remove log file {filename}: {e}")
    
    if cleaned_count > 0:
        logging.info(f"Log cleanup completed: {cleaned_count} files removed")


def get_date_input(prompt="Enter date (ddmmyyyy): "):
    """Get date input from user as string in ddmmyyyy format."""
    while True:
        date_str = input(prompt).strip()
        
        # Check if input is exactly 8 digits
        if len(date_str) != 8 or not date_str.isdigit():
            print("Error: Date must be exactly 8 digits in ddmmyyyy format")
            continue
        
        return date_str


def configure_pipeline_from_config(config, input_dir, target_date):
    """Configure pipeline with optimized settings from config."""
    perf_settings = config.get('performance_settings', {})
    
    # XML processing settings
    xml_settings = perf_settings.get('xml_processing', {})
    max_xml_workers = xml_settings.get('max_workers', 'auto')
    if max_xml_workers == 'auto':
        max_xml_workers = min(32, (os.cpu_count() or 1) + 4)
    
    # Database settings
    db_settings = perf_settings.get('database', {})
    max_db_connections = db_settings.get('max_connections', 5)
    
    # API settings
    api_settings = perf_settings.get('api', {})
    max_api_workers = api_settings.get('max_workers', 5)
    
    # Create optimized pipeline
    pipeline = XMLDiagnosePipelineOptimized(
        input_dir, 
        target_date,
        max_xml_workers=max_xml_workers,
        max_db_connections=max_db_connections,
        max_api_workers=max_api_workers
    )
    
    logging.info(f"Pipeline configured with: "
                f"XML workers={max_xml_workers}, "
                f"DB connections={max_db_connections}, "
                f"API workers={max_api_workers}")
    
    return pipeline


def check_performance_thresholds(result, config):
    """Check if processing times exceed configured thresholds and log warnings."""
    thresholds = config.get('monitoring', {}).get('performance_threshold_warnings', {})
    
    warnings = []
    
    if result.total_processing_time > thresholds.get('total_processing_time', float('inf')):
        warnings.append(f"Total processing time ({result.total_processing_time:.2f}s) "
                       f"exceeded threshold ({thresholds['total_processing_time']}s)")
    
    if result.xml_processing_time > thresholds.get('xml_processing_time', float('inf')):
        warnings.append(f"XML processing time ({result.xml_processing_time:.2f}s) "
                       f"exceeded threshold ({thresholds['xml_processing_time']}s)")
    
    if result.database_update_time > thresholds.get('database_update_time', float('inf')):
        warnings.append(f"Database update time ({result.database_update_time:.2f}s) "
                       f"exceeded threshold ({thresholds['database_update_time']}s)")
    
    if result.alert_update_time > thresholds.get('api_update_time', float('inf')):
        warnings.append(f"API update time ({result.alert_update_time:.2f}s) "
                       f"exceeded threshold ({thresholds['api_update_time']}s)")
    
    for warning in warnings:
        logging.warning(f"PERFORMANCE WARNING: {warning}")
    
    return warnings


def main():
    """Main execution function with optimized performance monitoring."""
    start_time = time.time()
    
    # Load configuration
    config = load_config()
    
    # Setup optimized logging first
    setup_logging(config)
    
    # Cleanup old logs
    cleanup_logs(config)
    
    # Get date from user
    target_date = get_date_input("Enter report date (ddmmyyyy): ")
    # target_date = '13072025'  # Uncomment for testing
    
    logging.info(f"Starting optimized processing for date: {target_date}")
    logging.info(f"Configuration loaded: {json.dumps(config.get('performance_settings', {}), indent=2)}")
    
    try:
        # Configure and run optimized pipeline
        input_dir = config.get('reports', 'reports')
        pipeline = configure_pipeline_from_config(config, input_dir, target_date)
        
        # Execute pipeline
        result = pipeline.run()
        
        # Check performance thresholds
        if config.get('monitoring', {}).get('enable_performance_logging', True):
            warnings = check_performance_thresholds(result, config)
            if warnings:
                logging.warning(f"Performance issues detected: {len(warnings)} warnings")
        
        # Log final results
        logging.info("=== FINAL RESULTS ===")
        logging.info(f"Processing completed successfully in {result.total_processing_time:.2f} seconds")
        logging.info(f"Error CSV: {result.error_csv}")
        logging.info(f"Valid CSV: {result.valid_csv}")
        logging.info(f"Reports processed: {result.reports_classified}")
        logging.info(f"Database records updated: {result.database_records_updated}")
        logging.info(f"Alerts updated: {result.alerts_updated}")
        
        # Get performance insights
        insights = pipeline.get_performance_insights()
        if insights.get('recommendations'):
            logging.info("=== PERFORMANCE RECOMMENDATIONS ===")
            for recommendation in insights['recommendations']:
                logging.info(f"RECOMMENDATION: {recommendation}")
        
        total_time = time.time() - start_time
        logging.info(f"Total application runtime: {total_time:.2f} seconds")
        
    except Exception as e:
        total_time = time.time() - start_time
        logging.error(f"Optimized pipeline failed after {total_time:.2f} seconds: {e}")
        raise
    
    logging.info("Application completed successfully")


if __name__ == "__main__":
    main()