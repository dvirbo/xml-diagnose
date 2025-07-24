import logging
import time
from typing import List, Dict, Optional
from contextlib import contextmanager
from concurrent.futures import ThreadPoolExecutor
import threading

from database.db_usage import update_db
from database.establish_db import connect_to_database


class ConnectionPool:
    """Simple database connection pool for improved performance"""
    
    def __init__(self, max_connections: int = 5):
        self.max_connections = max_connections
        self.pool = []
        self.used_connections = set()
        self.lock = threading.Lock()
    
    def get_connection(self):
        """Get a connection from the pool"""
        with self.lock:
            if self.pool:
                conn = self.pool.pop()
                self.used_connections.add(conn)
                return conn
            elif len(self.used_connections) < self.max_connections:
                conn = connect_to_database()
                if conn:
                    self.used_connections.add(conn)
                    return conn
        return None
    
    def return_connection(self, conn):
        """Return a connection to the pool"""
        with self.lock:
            if conn in self.used_connections:
                self.used_connections.remove(conn)
                self.pool.append(conn)
    
    def close_all(self):
        """Close all connections in the pool"""
        with self.lock:
            for conn in self.pool + list(self.used_connections):
                try:
                    conn.close()
                except:
                    pass
            self.pool.clear()
            self.used_connections.clear()


class DatabaseManagerOptimized:
    """Optimized database manager with connection pooling and better performance"""
    
    def __init__(self, max_connections: int = 5):
        self.connection_pool = ConnectionPool(max_connections)
        self.primary_connection = None
        self._stats = {
            'successful_operations': 0,
            'failed_operations': 0,
            'total_processing_time': 0.0
        }
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = self.connection_pool.get_connection()
        if not conn:
            # Fallback to creating a new connection
            conn = connect_to_database()
        
        try:
            yield conn
        finally:
            if conn:
                self.connection_pool.return_connection(conn)
    
    def connect(self) -> bool:
        """Establish primary database connection with retry logic"""
        max_retries = 3
        retry_delay = 1.0
        
        for attempt in range(max_retries):
            try:
                self.primary_connection = connect_to_database()
                if self.primary_connection:
                    logging.info("Primary database connection established successfully.")
                    return True
                else:
                    logging.warning(f"Database connection attempt {attempt + 1} failed")
                    if attempt < max_retries - 1:
                        time.sleep(retry_delay)
                        retry_delay *= 2  # Exponential backoff
            except Exception as e:
                logging.error(f"Database connection attempt {attempt + 1} error: {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    retry_delay *= 2
        
        logging.error("Failed to establish database connection after all retries.")
        return False
    
    def update_reports(self, reports: List) -> List[Dict]:
        """Update database with reports using optimized operations"""
        if not self.primary_connection:
            logging.error("No database connection available")
            return []
        
        start_time = time.time()
        summary_report = []
        
        try:
            if reports:
                logging.info(f"Updating database with {len(reports)} reports using optimized operations...")
                
                # Use the existing optimized bulk update function
                summary_report.extend(update_db(self.primary_connection, reports))
                
                self._stats['successful_operations'] += len(reports)
                logging.info(f"Successfully processed {len(reports)} reports")
                
        except Exception as e:
            logging.error(f"Database update failed: {e}")
            self._stats['failed_operations'] += len(reports) if reports else 1
            # Don't raise the exception, return empty list to allow pipeline to continue
            return []
        finally:
            processing_time = time.time() - start_time
            self._stats['total_processing_time'] += processing_time
            logging.info(f"Database operation completed in {processing_time:.2f} seconds")
        
        return summary_report
    
    def update_reports_concurrent(self, reports: List, batch_size: int = 100) -> List[Dict]:
        """
        Update database with reports using concurrent processing for large datasets
        """
        if not reports:
            return []
        
        if len(reports) <= batch_size:
            # Use regular update for small datasets
            return self.update_reports(reports)
        
        logging.info(f"Processing {len(reports)} reports with concurrent batch updates...")
        
        # Split reports into batches
        batches = [reports[i:i + batch_size] for i in range(0, len(reports), batch_size)]
        all_summary_reports = []
        
        # Process batches concurrently
        with ThreadPoolExecutor(max_workers=min(3, len(batches))) as executor:
            futures = []
            for batch in batches:
                future = executor.submit(self._process_batch, batch)
                futures.append(future)
            
            # Collect results
            for future in futures:
                try:
                    batch_summary = future.result(timeout=60)  # 60 second timeout per batch
                    all_summary_reports.extend(batch_summary)
                except Exception as e:
                    logging.error(f"Batch processing failed: {e}")
                    self._stats['failed_operations'] += 1
        
        return all_summary_reports
    
    def _process_batch(self, batch: List) -> List[Dict]:
        """Process a batch of reports with its own connection"""
        with self.get_connection() as conn:
            if conn:
                return update_db(conn, batch)
            else:
                logging.error("Failed to get connection for batch processing")
                return []
    
    def get_performance_stats(self) -> Dict:
        """Get performance statistics"""
        return {
            'successful_operations': self._stats['successful_operations'],
            'failed_operations': self._stats['failed_operations'],
            'total_processing_time': self._stats['total_processing_time'],
            'average_time_per_operation': (
                self._stats['total_processing_time'] / max(1, self._stats['successful_operations'])
                if self._stats['successful_operations'] > 0 else 0
            )
        }
    
    def close(self):
        """Close all database connections"""
        try:
            if self.primary_connection:
                self.primary_connection.close()
                logging.info("Primary database connection closed.")
            
            self.connection_pool.close_all()
            logging.info("All pooled connections closed.")
            
            # Log performance stats
            stats = self.get_performance_stats()
            logging.info(f"Database performance stats: {stats}")
            
        except Exception as e:
            logging.error(f"Error closing database connections: {e}")


# Backward compatibility
class DatabaseManager(DatabaseManagerOptimized):
    """Backward compatibility alias"""
    pass