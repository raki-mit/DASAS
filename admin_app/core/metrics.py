"""
DASAS Metrics Collector Module
================================
Provides metrics collection and monitoring for the DASAS Admin Dashboard.

Author: DASAS Team
Version: 1.0.0
"""

import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from collections import defaultdict
from dataclasses import dataclass, field
import json

from .logging_config import logger


@dataclass
class Metric:
    """Data class representing a single metric"""
    name: str
    value: float
    timestamp: datetime = field(default_factory=datetime.now)
    tags: Dict[str, str] = field(default_factory=dict)
    metric_type: str = "gauge"  # gauge, counter, histogram


@dataclass
class DeviceMetrics:
    """Data class for device-specific metrics"""
    device_id: str
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    battery_level: float = 100.0
    network_latency: float = 0.0
    screen_capture_fps: float = 0.0
    ml_inference_time: float = 0.0
    last_heartbeat: datetime = field(default_factory=datetime.now)
    status: str = "unknown"


class MetricsCollector:
    """
    Central metrics collector for DASAS.
    
    Collects, aggregates, and provides metrics from various sources
    including devices, clusters, and system resources.
    """
    
    def __init__(self):
        self._lock = threading.Lock()
        self._metrics: Dict[str, List[Metric]] = defaultdict(list)
        self._device_metrics: Dict[str, DeviceMetrics] = {}
        self._system_metrics: Dict[str, Any] = {}
        self._start_time = datetime.now()
        self._initialized = False
    
    def initialize(self):
        """Initialize the metrics collector"""
        if self._initialized:
            return
        
        self._start_time = datetime.now()
        self._initialized = True
        logger.info("Metrics collector initialized")
    
    # ==================== Metric Recording ====================
    
    def record_metric(
        self,
        name: str,
        value: float,
        tags: Dict[str, str] = None,
        metric_type: str = "gauge"
    ):
        """
        Record a single metric.
        
        Args:
            name: Name of the metric
            value: Value to record
            tags: Optional tags for categorization
            metric_type: Type of metric (gauge, counter, histogram)
        """
        with self._lock:
            metric = Metric(
                name=name,
                value=value,
                tags=tags or {},
                metric_type=metric_type
            )
            self._metrics[name].append(metric)
            
            # Keep only last 1000 entries per metric
            if len(self._metrics[name]) > 1000:
                self._metrics[name] = self._metrics[name][-1000:]
    
    def record_device_metrics(self, device_id: str, metrics: DeviceMetrics):
        """
        Record metrics for a specific device.
        
        Args:
            device_id: Unique device identifier
            metrics: DeviceMetrics object with device metrics
        """
        with self._lock:
            self._device_metrics[device_id] = metrics
    
    def record_counter(
        self,
        name: str,
        value: float = 1,
        tags: Dict[str, str] = None
    ):
        """Record a counter metric (monotonically increasing)"""
        self.record_metric(name, value, tags, "counter")
    
    def record_histogram(
        self,
        name: str,
        value: float,
        tags: Dict[str, str] = None
    ):
        """Record a histogram metric"""
        self.record_metric(name, value, tags, "histogram")
    
    # ==================== Metric Retrieval ====================
    
    def get_metric(self, name: str, last_n: int = 1) -> List[Metric]:
        """
        Get recent values for a metric.
        
        Args:
            name: Name of the metric
            last_n: Number of recent values to return
            
        Returns:
            List of Metric objects
        """
        with self._lock:
            return self._metrics[name][-last_n:]
    
    def get_metric_value(self, name: str, default: float = 0.0) -> float:
        """
        Get the latest value of a metric.
        
        Args:
            name: Name of the metric
            default: Default value if metric not found
            
        Returns:
            Latest metric value or default
        """
        metrics = self.get_metric(name, last_n=1)
        if metrics:
            return metrics[0].value
        return default
    
    def get_all_metrics(self) -> Dict[str, List[Metric]]:
        """Get all collected metrics"""
        with self._lock:
            return dict(self._metrics)
    
    # ==================== Device Metrics ====================
    
    def get_device_metrics(self, device_id: str) -> Optional[DeviceMetrics]:
        """
        Get metrics for a specific device.
        
        Args:
            device_id: Unique device identifier
            
        Returns:
            DeviceMetrics object or None
        """
        return self._device_metrics.get(device_id)
    
    def get_all_device_metrics(self) -> Dict[str, DeviceMetrics]:
        """Get metrics for all devices"""
        with self._lock:
            return dict(self._device_metrics)
    
    def get_device_count(self) -> int:
        """Get total number of tracked devices"""
        return len(self._device_metrics)
    
    def get_active_device_count(self) -> int:
        """Get number of active devices (recent heartbeat)"""
        active_count = 0
        timeout = timedelta(seconds=60)
        now = datetime.now()
        
        for metrics in self._device_metrics.values():
            if now - metrics.last_heartbeat < timeout:
                active_count += 1
        
        return active_count
    
    # ==================== System Metrics ====================
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """
        Get system-wide metrics.
        
        Returns:
            Dictionary of system metrics
        """
        uptime = (datetime.now() - self._start_time).total_seconds()
        
        return {
            "status": self._get_health_status(),
            "uptime_seconds": uptime,
            "uptime_formatted": self._format_uptime(uptime),
            "total_devices": self.get_device_count(),
            "active_devices": self.get_active_device_count(),
            "total_metrics": sum(len(m) for m in self._metrics.values()),
            "timestamp": datetime.now().isoformat()
        }
    
    def record_system_metric(self, key: str, value: Any):
        """
        Record a system-wide metric.
        
        Args:
            key: Metric key
            value: Metric value
        """
        with self._lock:
            self._system_metrics[key] = {
                "value": value,
                "timestamp": datetime.now().isoformat()
            }
    
    # ==================== Aggregations ====================
    
    def get_metric_statistics(self, name: str) -> Dict[str, float]:
        """
        Get statistical summary of a metric.
        
        Args:
            name: Name of the metric
            
        Returns:
            Dictionary with count, sum, mean, min, max, std
        """
        with self._lock:
            metrics = self._metrics.get(name, [])
            if not metrics:
                return {}
            
            values = [m.value for m in metrics]
            
            import statistics
            
            return {
                "count": len(values),
                "sum": sum(values),
                "mean": statistics.mean(values),
                "min": min(values),
                "max": max(values),
                "stdev": statistics.stdev(values) if len(values) > 1 else 0,
                "median": statistics.median(values)
            }
    
    def get_time_series_data(
        self,
        name: str,
        time_range: timedelta = timedelta(hours=1)
    ) -> List[Dict[str, Any]]:
        """
        Get time series data for a metric.
        
        Args:
            name: Name of the metric
            time_range: Time range to retrieve
            
        Returns:
            List of {timestamp, value} dictionaries
        """
        cutoff = datetime.now() - time_range
        
        with self._lock:
            metrics = [
                m for m in self._metrics.get(name, [])
                if m.timestamp >= cutoff
            ]
            
            return [
                {
                    "timestamp": m.timestamp.isoformat(),
                    "value": m.value,
                    "tags": m.tags
                }
                for m in metrics
            ]
    
    # ==================== Health Checks ====================
    
    def _get_health_status(self) -> str:
        """Determine overall system health status"""
        active_ratio = self.get_active_device_count() / max(1, self.get_device_count())
        
        if active_ratio >= 0.9:
            return "healthy"
        elif active_ratio >= 0.5:
            return "degraded"
        else:
            return "critical"
    
    def health_check(self) -> Dict[str, Any]:
        """
        Perform a health check.
        
        Returns:
            Health check results
        """
        return {
            "status": self._get_health_status(),
            "checks": {
                "database": self._check_database(),
                "cache": self._check_cache(),
                "devices": self._check_devices()
            },
            "timestamp": datetime.now().isoformat()
        }
    
    def _check_database(self) -> Dict[str, Any]:
        """Check database health"""
        # Placeholder - implement actual check
        return {"status": "healthy", "latency_ms": 0}
    
    def _check_cache(self) -> Dict[str, Any]:
        """Check cache health"""
        # Placeholder - implement actual check
        return {"status": "healthy", "latency_ms": 0}
    
    def _check_devices(self) -> Dict[str, Any]:
        """Check device connectivity"""
        total = self.get_device_count()
        active = self.get_active_device_count()
        
        return {
            "status": "healthy" if active >= total * 0.5 else "degraded",
            "total": total,
            "active": active
        }
    
    # ==================== Utility Methods ====================
    
    def _format_uptime(self, seconds: float) -> str:
        """Format uptime in human-readable format"""
        if seconds < 60:
            return f"{seconds:.0f}s"
        elif seconds < 3600:
            return f"{seconds/60:.1f}m"
        elif seconds < 86400:
            return f"{seconds/3600:.1f}h"
        else:
            return f"{seconds/86400:.1f}d"
    
    def reset_metrics(self):
        """Reset all metrics (use with caution)"""
        with self._lock:
            self._metrics.clear()
            self._device_metrics.clear()
            self._system_metrics.clear()
            self._start_time = datetime.now()
        logger.info("All metrics reset")
    
    def export_metrics(self, format: str = "json") -> str:
        """
        Export all metrics in specified format.
        
        Args:
            format: Export format (json, prometheus)
            
        Returns:
            Exported metrics string
        """
        if format == "json":
            return self._export_json()
        elif format == "prometheus":
            return self._export_prometheus()
        return ""
    
    def _export_json(self) -> str:
        """Export metrics as JSON"""
        data = {
            "timestamp": datetime.now().isoformat(),
            "metrics": {
                name: [
                    {
                        "timestamp": m.timestamp.isoformat(),
                        "value": m.value,
                        "tags": m.tags
                    }
                    for m in metrics
                ]
                for name, metrics in self._metrics.items()
            }
        }
        return json.dumps(data, indent=2)
    
    def _export_prometheus(self) -> str:
        """Export metrics in Prometheus format"""
        lines = []
        
        for name, metrics in self._metrics.items():
            for metric in metrics[-1:]:  # Only latest value
                tags_str = ",".join(
                    f'{k}="{v}"' for k, v in metric.tags.items()
                )
                lines.append(
                    f'dasas_{name}{"{" + tags_str + "}" if tags_str else ""} '
                    f'{metric.value} {int(metric.timestamp.timestamp())}'
                )
        
        return "\n".join(lines)


# Global metrics collector instance
metrics_collector = MetricsCollector()
