import logging
import time
from typing import Dict, List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from api.update_alert_rest import process_alert
from api.api_session import login_and_get_session


class SessionPool:
    """Session pool for API connections with connection reuse"""
    
    def __init__(self, max_sessions: int = 3):
        self.max_sessions = max_sessions
        self.sessions = []
        self.session_stats = {}
        
    def create_optimized_session(self) -> requests.Session:
        """Create an optimized session with connection pooling and retry logic"""
        session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        
        # Configure HTTP adapter with connection pooling
        adapter = HTTPAdapter(
            pool_connections=10,
            pool_maxsize=20,
            max_retries=retry_strategy
        )
        
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # Set reasonable timeouts
        session.timeout = (5, 30)  # (connect timeout, read timeout)
        
        return session
    
    def get_session(self) -> Optional[requests.Session]:
        """Get an authenticated session from the pool"""
        if self.sessions:
            return self.sessions.pop()
        
        if len(self.session_stats) < self.max_sessions:
            # Try to create a new session
            session = login_and_get_session()
            if session:
                # Apply optimizations to the existing session
                session = self._optimize_existing_session(session)
                session_id = id(session)
                self.session_stats[session_id] = {
                    'requests_made': 0,
                    'created_at': time.time()
                }
                return session
        
        return None
    
    def _optimize_existing_session(self, session: requests.Session) -> requests.Session:
        """Apply optimizations to an existing session"""
        # Configure retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        
        # Configure HTTP adapter with connection pooling
        adapter = HTTPAdapter(
            pool_connections=10,
            pool_maxsize=20,
            max_retries=retry_strategy
        )
        
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        return session
    
    def return_session(self, session: requests.Session):
        """Return a session to the pool"""
        session_id = id(session)
        if session_id in self.session_stats:
            self.session_stats[session_id]['requests_made'] += 1
            
            # Only keep sessions that are still fresh (less than 30 minutes old)
            if (time.time() - self.session_stats[session_id]['created_at']) < 1800:
                self.sessions.append(session)
            else:
                # Session is too old, close it
                session.close()
                del self.session_stats[session_id]
    
    def close_all_sessions(self):
        """Close all sessions in the pool"""
        for session in self.sessions:
            try:
                session.close()
            except:
                pass
        self.sessions.clear()
        self.session_stats.clear()


class AlertUpdaterOptimized:
    """Optimized alert updater with concurrent processing and session pooling"""
    
    def __init__(self, max_workers: int = 5, max_sessions: int = 3):
        self.session_pool = SessionPool(max_sessions)
        self.primary_session = None
        self.max_workers = max_workers
        self._stats = {
            'successful_updates': 0,
            'failed_updates': 0,
            'total_processing_time': 0.0,
            'average_request_time': 0.0
        }
    
    def initialize_session(self) -> bool:
        """Create and validate primary session with optimization"""
        try:
            self.primary_session = self.session_pool.get_session()
            if not self.primary_session:
                logging.error("Failed to create or validate session")
                return False
            
            logging.info("Optimized session established successfully.")
            return True
            
        except Exception as e:
            logging.error(f"Session initialization failed: {e}")
            return False
    
    def update_alerts(self, summary_report: List[Dict]) -> bool:
        """Update alerts with concurrent processing for better performance"""
        if not summary_report:
            logging.info("No alerts to update")
            return True
        
        start_time = time.time()
        
        # For small batches, use sequential processing to avoid overhead
        if len(summary_report) <= 5:
            return self._update_alerts_sequential(summary_report)
        
        # For larger batches, use concurrent processing
        return self._update_alerts_concurrent(summary_report, start_time)
    
    def _update_alerts_sequential(self, summary_report: List[Dict]) -> bool:
        """Update alerts sequentially for small batches"""
        if not self.primary_session:
            logging.error("No valid session available")
            return False
        
        success_count = 0
        start_time = time.time()
        
        for report in summary_report:
            request_start = time.time()
            update_status = process_alert(self.primary_session, report)
            request_time = time.time() - request_start
            
            if update_status:
                success_count += 1
                self._stats['successful_updates'] += 1
                logging.info(f"Successfully updated alert for report: {report.get('report_id')} "
                           f"with status {report.get('status_divuah')} "
                           f"and mispar_tkina {report.get('mispar_tkina')} "
                           f"(took {request_time:.2f}s)")
            else:
                self._stats['failed_updates'] += 1
                logging.error(f"Failed to update alert for report: {report.get('report_id')}")
        
        total_time = time.time() - start_time
        self._stats['total_processing_time'] += total_time
        
        logging.info(f"Sequential alert updates completed: {success_count}/{len(summary_report)} "
                    f"successful in {total_time:.2f}s")
        
        return success_count == len(summary_report)
    
    def _update_alerts_concurrent(self, summary_report: List[Dict], start_time: float) -> bool:
        """Update alerts concurrently for larger batches"""
        logging.info(f"Updating {len(summary_report)} alerts concurrently with {self.max_workers} workers...")
        
        successful_updates = 0
        failed_updates = 0
        
        # Use ThreadPoolExecutor for concurrent processing
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all alert update tasks
            future_to_report = {
                executor.submit(self._process_alert_with_session, report): report 
                for report in summary_report
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_report):
                report = future_to_report[future]
                try:
                    request_time, success = future.result(timeout=60)  # 60 second timeout per request
                    
                    if success:
                        successful_updates += 1
                        self._stats['successful_updates'] += 1
                        logging.info(f"Successfully updated alert for report: {report.get('report_id')} "
                                   f"(took {request_time:.2f}s)")
                    else:
                        failed_updates += 1
                        self._stats['failed_updates'] += 1
                        logging.error(f"Failed to update alert for report: {report.get('report_id')}")
                        
                except Exception as e:
                    failed_updates += 1
                    self._stats['failed_updates'] += 1
                    logging.error(f"Exception updating alert for report {report.get('report_id')}: {e}")
        
        total_time = time.time() - start_time
        self._stats['total_processing_time'] += total_time
        
        logging.info(f"Concurrent alert updates completed: {successful_updates}/{len(summary_report)} "
                    f"successful in {total_time:.2f}s")
        
        return failed_updates == 0
    
    def _process_alert_with_session(self, report: Dict) -> tuple[float, bool]:
        """Process a single alert update with its own session"""
        session = self.session_pool.get_session()
        if not session:
            logging.error("Failed to get session for alert processing")
            return 0.0, False
        
        try:
            request_start = time.time()
            success = process_alert(session, report)
            request_time = time.time() - request_start
            
            return request_time, success
            
        except Exception as e:
            logging.error(f"Error processing alert: {e}")
            return 0.0, False
        finally:
            # Return session to pool
            self.session_pool.return_session(session)
    
    def get_performance_stats(self) -> Dict:
        """Get performance statistics"""
        total_updates = self._stats['successful_updates'] + self._stats['failed_updates']
        return {
            'successful_updates': self._stats['successful_updates'],
            'failed_updates': self._stats['failed_updates'],
            'success_rate': (
                self._stats['successful_updates'] / max(1, total_updates) * 100
                if total_updates > 0 else 0
            ),
            'total_processing_time': self._stats['total_processing_time'],
            'average_time_per_update': (
                self._stats['total_processing_time'] / max(1, total_updates)
                if total_updates > 0 else 0
            )
        }
    
    def close(self):
        """Close all sessions and cleanup resources"""
        try:
            if self.primary_session:
                self.primary_session.close()
            
            self.session_pool.close_all_sessions()
            
            # Log performance stats
            stats = self.get_performance_stats()
            logging.info(f"Alert updater performance stats: {stats}")
            
        except Exception as e:
            logging.error(f"Error closing alert updater resources: {e}")


# Backward compatibility
class AlertUpdater(AlertUpdaterOptimized):
    """Backward compatibility alias"""
    pass