"""
DASAS Database Manager Module
==============================
Provides database management for the DASAS Admin Dashboard.

Author: DASAS Team
Version: 1.0.0
"""

import sqlite3
import threading
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from contextlib import contextmanager
import json

# Handle relative imports for both direct and package usage
try:
    from ..core.logging_config import logger
    from ..core.config import settings
except ImportError:
    from core.logging_config import logger
    from core.config import settings


class DatabaseManager:
    """
    Database manager for DASAS Admin Dashboard.
    
    Handles all database operations including CRUD operations,
    transactions, and connection pooling.
    """
    
    def __init__(self, db_path: str = None):
        """
        Initialize database manager.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path or settings.database.path
        self._lock = threading.Lock()
        self._connection_pool = []
        self._max_pool_size = settings.database.pool_size
        self._initialized = False
        
        # Ensure data directory exists
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
    
    def initialize(self):
        """Initialize database tables"""
        if self._initialized:
            return
        
        self._create_tables()
        self._initialized = True
        logger.info("Database initialized successfully")
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get a database connection"""
        if self._connection_pool:
            conn = self._connection_pool.pop()
            # Check if connection is still valid
            try:
                conn.execute("SELECT 1")
                return conn
            except Exception:
                pass
        
        conn = sqlite3.connect(
            self.db_path,
            check_same_thread=False,
            timeout=30.0
        )
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn
    
    def _return_connection(self, conn: sqlite3.Connection):
        """Return connection to pool"""
        if len(self._connection_pool) < self._max_pool_size:
            self._connection_pool.append(conn)
        else:
            conn.close()
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = self._get_connection()
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            self._return_connection(conn)
    
    def _create_tables(self):
        """Create all required database tables"""
        with self.get_connection() as conn:
            # Devices table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS devices (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    device_type TEXT DEFAULT 'android',
                    status TEXT DEFAULT 'offline',
                    cluster_id TEXT,
                    ip_address TEXT,
                    mac_address TEXT,
                    cpu_cores INTEGER,
                    total_memory BIGINT,
                    android_version TEXT,
                    last_heartbeat DATETIME,
                    registration_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                    metadata TEXT,
                    FOREIGN KEY (cluster_id) REFERENCES clusters(id)
                )
            """)
            
            # Clusters table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS clusters (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    status TEXT DEFAULT 'forming',
                    leader_id TEXT,
                    member_count INTEGER DEFAULT 0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    last_activity DATETIME,
                    configuration TEXT,
                    FOREIGN KEY (leader_id) REFERENCES devices(id)
                )
            """)
            
            # Device metrics table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS device_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    device_id TEXT NOT NULL,
                    metric_name TEXT NOT NULL,
                    metric_value REAL NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (device_id) REFERENCES devices(id)
                )
            """)
            
            # Checkpoints table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS checkpoints (
                    id TEXT PRIMARY KEY,
                    cluster_id TEXT NOT NULL,
                    checkpoint_data TEXT NOT NULL,
                    sequence_number INTEGER NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (cluster_id) REFERENCES clusters(id)
                )
            """)
            
            # Events table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_type TEXT NOT NULL,
                    source_id TEXT,
                    severity TEXT DEFAULT 'info',
                    message TEXT,
                    metadata TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Alerts table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    alert_type TEXT NOT NULL,
                    source_id TEXT,
                    severity TEXT DEFAULT 'warning',
                    message TEXT,
                    status TEXT DEFAULT 'active',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    resolved_at DATETIME
                )
            """)
            
            # Create indexes
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_devices_cluster
                ON devices(cluster_id)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_metrics_device
                ON device_metrics(device_id, timestamp)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_events_timestamp
                ON events(timestamp)
            """)
    
    # ==================== Device Operations ====================
    
    def add_device(
        self,
        device_id: str,
        name: str,
        device_type: str = "android",
        **kwargs
    ) -> bool:
        """
        Add a new device to the database.
        
        Args:
            device_id: Unique device identifier
            name: Device name
            device_type: Type of device
            **kwargs: Additional device properties
            
        Returns:
            True if successful
        """
        with self.get_connection() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO devices
                (id, name, device_type, status, cluster_id, ip_address,
                 mac_address, cpu_cores, total_memory, android_version, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    device_id,
                    name,
                    device_type,
                    kwargs.get("status", "offline"),
                    kwargs.get("cluster_id"),
                    kwargs.get("ip_address"),
                    kwargs.get("mac_address"),
                    kwargs.get("cpu_cores"),
                    kwargs.get("total_memory"),
                    kwargs.get("android_version"),
                    json.dumps(kwargs.get("metadata", {}))
                )
            )
            return True
    
    def update_device_status(
        self,
        device_id: str,
        status: str,
        **kwargs
    ) -> bool:
        """
        Update device status.
        
        Args:
            device_id: Device identifier
            status: New status
            **kwargs: Additional fields to update
            
        Returns:
            True if successful
        """
        with self.get_connection() as conn:
            updates = ["status = ?", "last_heartbeat = ?"]
            values = [status, datetime.now().isoformat()]
            
            for key, value in kwargs.items():
                updates.append(f"{key} = ?")
                values.append(value)
            
            values.append(device_id)
            
            conn.execute(
                f"UPDATE devices SET {', '.join(updates)} WHERE id = ?",
                values
            )
            return True
    
    def get_device(self, device_id: str) -> Optional[Dict[str, Any]]:
        """
        Get device information.
        
        Args:
            device_id: Device identifier
            
        Returns:
            Device dictionary or None
        """
        with self.get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM devices WHERE id = ?",
                (device_id,)
            ).fetchone()
            
            if row:
                return dict(row)
            return None
    
    def get_all_devices(
        self,
        status: str = None,
        cluster_id: str = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get all devices with optional filters.
        
        Args:
            status: Filter by status
            cluster_id: Filter by cluster
            limit: Maximum number of results
            offset: Offset for pagination
            
        Returns:
            List of device dictionaries
        """
        with self.get_connection() as conn:
            query = "SELECT * FROM devices WHERE 1=1"
            params = []
            
            if status:
                query += " AND status = ?"
                params.append(status)
            
            if cluster_id:
                query += " AND cluster_id = ?"
                params.append(cluster_id)
            
            query += " LIMIT ? OFFSET ?"
            params.extend([limit, offset])
            
            rows = conn.execute(query, params).fetchall()
            return [dict(row) for row in rows]
    
    def get_device_count(self, status: str = None) -> int:
        """Get device count with optional status filter"""
        with self.get_connection() as conn:
            query = "SELECT COUNT(*) FROM devices WHERE 1=1"
            params = []
            
            if status:
                query += " AND status = ?"
                params.append(status)
            
            return conn.execute(query, params).fetchone()[0]
    
    # ==================== Cluster Operations ====================
    
    def add_cluster(
        self,
        cluster_id: str,
        name: str,
        **kwargs
    ) -> bool:
        """
        Add a new cluster.
        
        Args:
            cluster_id: Unique cluster identifier
            name: Cluster name
            **kwargs: Additional cluster properties
            
        Returns:
            True if successful
        """
        with self.get_connection() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO clusters
                (id, name, status, leader_id, member_count, configuration)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    cluster_id,
                    name,
                    kwargs.get("status", "forming"),
                    kwargs.get("leader_id"),
                    kwargs.get("member_count", 0),
                    json.dumps(kwargs.get("configuration", {}))
                )
            )
            return True
    
    def get_cluster(self, cluster_id: str) -> Optional[Dict[str, Any]]:
        """Get cluster information"""
        with self.get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM clusters WHERE id = ?",
                (cluster_id,)
            ).fetchone()
            
            if row:
                return dict(row)
            return None
    
    def get_all_clusters(self) -> List[Dict[str, Any]]:
        """Get all clusters"""
        with self.get_connection() as conn:
            rows = conn.execute("SELECT * FROM clusters").fetchall()
            return [dict(row) for row in rows]
    
    def update_cluster_member_count(self, cluster_id: str, count: int) -> bool:
        """Update cluster member count"""
        with self.get_connection() as conn:
            conn.execute(
                "UPDATE clusters SET member_count = ?, last_activity = ? WHERE id = ?",
                (count, datetime.now().isoformat(), cluster_id)
            )
            return True
    
    # ==================== Metrics Operations ====================
    
    def record_device_metric(
        self,
        device_id: str,
        metric_name: str,
        metric_value: float
    ) -> bool:
        """
        Record a device metric.
        
        Args:
            device_id: Device identifier
            metric_name: Name of the metric
            metric_value: Value of the metric
            
        Returns:
            True if successful
        """
        with self.get_connection() as conn:
            conn.execute(
                """
                INSERT INTO device_metrics
                (device_id, metric_name, metric_value)
                VALUES (?, ?, ?)
                """,
                (device_id, metric_name, metric_value)
            )
            return True
    
    def get_device_metrics(
        self,
        device_id: str,
        metric_name: str = None,
        since: datetime = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get device metrics.
        
        Args:
            device_id: Device identifier
            metric_name: Optional metric name filter
            since: Optional start time filter
            limit: Maximum results
            
        Returns:
            List of metric records
        """
        with self.get_connection() as conn:
            query = "SELECT * FROM device_metrics WHERE device_id = ?"
            params = [device_id]
            
            if metric_name:
                query += " AND metric_name = ?"
                params.append(metric_name)
            
            if since:
                query += " AND timestamp >= ?"
                params.append(since.isoformat())
            
            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)
            
            rows = conn.execute(query, params).fetchall()
            return [dict(row) for row in rows]
    
    # ==================== Checkpoint Operations ====================
    
    def save_checkpoint(
        self,
        checkpoint_id: str,
        cluster_id: str,
        checkpoint_data: Dict[str, Any],
        sequence_number: int
    ) -> bool:
        """
        Save a cluster checkpoint.
        
        Args:
            checkpoint_id: Unique checkpoint identifier
            cluster_id: Cluster identifier
            checkpoint_data: Checkpoint data dictionary
            sequence_number: Sequence number
            
        Returns:
            True if successful
        """
        with self.get_connection() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO checkpoints
                (id, cluster_id, checkpoint_data, sequence_number)
                VALUES (?, ?, ?, ?)
                """,
                (
                    checkpoint_id,
                    cluster_id,
                    json.dumps(checkpoint_data),
                    sequence_number
                )
            )
            return True
    
    def get_latest_checkpoint(self, cluster_id: str) -> Optional[Dict[str, Any]]:
        """Get the latest checkpoint for a cluster"""
        with self.get_connection() as conn:
            row = conn.execute(
                """
                SELECT * FROM checkpoints
                WHERE cluster_id = ?
                ORDER BY sequence_number DESC
                LIMIT 1
                """,
                (cluster_id,)
            ).fetchone()
            
            if row:
                return dict(row)
            return None
    
    def get_checkpoint_history(
        self,
        cluster_id: str = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get checkpoint history"""
        with self.get_connection() as conn:
            query = "SELECT * FROM checkpoints"
            params = []
            
            if cluster_id:
                query += " WHERE cluster_id = ?"
                params.append(cluster_id)
            
            query += " ORDER BY created_at DESC LIMIT ?"
            params.append(limit)
            
            rows = conn.execute(query, params).fetchall()
            return [dict(row) for row in rows]
    
    # ==================== Event Operations ====================
    
    def log_event(
        self,
        event_type: str,
        message: str,
        source_id: str = None,
        severity: str = "info",
        metadata: Dict = None
    ) -> bool:
        """
        Log an event.
        
        Args:
            event_type: Type of event
            message: Event message
            source_id: Source device/cluster ID
            severity: Event severity
            metadata: Additional metadata
            
        Returns:
            True if successful
        """
        with self.get_connection() as conn:
            conn.execute(
                """
                INSERT INTO events
                (event_type, source_id, severity, message, metadata)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    event_type,
                    source_id,
                    severity,
                    message,
                    json.dumps(metadata or {})
                )
            )
            return True
    
    def get_events(
        self,
        event_type: str = None,
        severity: str = None,
        since: datetime = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get events with optional filters"""
        with self.get_connection() as conn:
            query = "SELECT * FROM events WHERE 1=1"
            params = []
            
            if event_type:
                query += " AND event_type = ?"
                params.append(event_type)
            
            if severity:
                query += " AND severity = ?"
                params.append(severity)
            
            if since:
                query += " AND timestamp >= ?"
                params.append(since.isoformat())
            
            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)
            
            rows = conn.execute(query, params).fetchall()
            return [dict(row) for row in rows]
    
    # ==================== Alert Operations ====================
    
    def create_alert(
        self,
        alert_type: str,
        message: str,
        source_id: str = None,
        severity: str = "warning"
    ) -> int:
        """Create a new alert"""
        with self.get_connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO alerts
                (alert_type, source_id, severity, message)
                VALUES (?, ?, ?, ?)
                """,
                (alert_type, source_id, severity, message)
            )
            return cursor.lastrowid
    
    def get_active_alerts(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get active alerts"""
        with self.get_connection() as conn:
            rows = conn.execute(
                """
                SELECT * FROM alerts
                WHERE status = 'active'
                ORDER BY created_at DESC
                LIMIT ?
                """,
                (limit,)
            ).fetchall()
            return [dict(row) for row in rows]
    
    def resolve_alert(self, alert_id: int) -> bool:
        """Resolve an alert"""
        with self.get_connection() as conn:
            conn.execute(
                """
                UPDATE alerts
                SET status = 'resolved', resolved_at = ?
                WHERE id = ?
                """,
                (datetime.now().isoformat(), alert_id)
            )
            return True
    
    # ==================== Utility Methods ====================
    
    def cleanup_old_data(self, days: int = 30):
        """
        Remove data older than specified days.
        
        Args:
            days: Number of days to retain data
        """
        with self.get_connection() as conn:
            cutoff = datetime.now().isoformat()
            
            conn.execute(
                "DELETE FROM device_metrics WHERE timestamp < ?",
                (cutoff,)
            )
            
            conn.execute(
                "DELETE FROM events WHERE timestamp < ?",
                (cutoff,)
            )
            
            logger.info(f"Cleaned up data older than {days} days")
    
    def backup_database(self, backup_path: str) -> bool:
        """
        Create a database backup.
        
        Args:
            backup_path: Path for backup file
            
        Returns:
            True if successful
        """
        import shutil
        
        try:
            shutil.copy(self.db_path, backup_path)
            logger.info(f"Database backup created: {backup_path}")
            return True
        except Exception as e:
            logger.error(f"Database backup failed: {e}")
            return False


# Global database manager instance
db_manager = DatabaseManager()
