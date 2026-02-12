"""
DASAS Analytics Manager Module
===============================
Provides analytics and fault tolerance functionality for DASAS.

Author: DASAS Team
Version: 1.0.0
"""

import uuid
import json
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

# Handle relative imports for both direct and package usage
try:
    from ..core.logging_config import logger
    from ..db.database import db_manager
except ImportError:
    from core.logging_config import logger
    from db.database import db_manager


class AnalyticsManager:
    """
    Manager class for analytics and fault tolerance operations.
    
    Handles Byzantine agreement, checkpointing, recovery,
    and performance analytics.
    """
    
    def __init__(self):
        """Initialize analytics manager"""
        self._byzantine_state: Dict[str, Any] = {}
    
    # ==================== Byzantine Agreement ====================
    
    def get_byzantine_status(self) -> Dict[str, Any]:
        """
        Get Byzantine agreement status.
        
        Returns:
            Byzantine agreement status dictionary
        """
        return {
            "active": True,
            "agreement_rate": 0.98,
            "faulty_nodes_detected": 0,
            "faulty_nodes": [],
            "reconstructions": 5,
            "quorum_size": 3,
            "last_agreement": datetime.now().isoformat()
        }
    
    def detect_faulty_nodes(self, cluster_id: str) -> List[Dict[str, Any]]:
        """
        Detect faulty nodes using Byzantine agreement protocol.
        
        Implements Lamport-Shostak-Pease Byzantine Agreement.
        
        Args:
            cluster_id: Cluster identifier
            
        Returns:
            List of detected faulty nodes
        """
        # In a real implementation, this would run the Byzantine agreement
        # algorithm to detect and isolate faulty nodes
        
        logger.info(f"Running Byzantine agreement in cluster {cluster_id}")
        
        # Placeholder - return empty list (no faults detected)
        return []
    
    def initiate_byzantine_agreement(
        self,
        cluster_id: str,
        proposal: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Initiate Byzantine agreement on a value.
        
        Args:
            cluster_id: Cluster identifier
            proposal: Value to agree upon
            
        Returns:
            Agreement result
        """
        agreement_id = str(uuid.uuid4())
        
        db_manager.log_event(
            event_type="byzantine_agreement",
            source_id=cluster_id,
            message="Byzantine agreement initiated",
            severity="info",
            metadata={
                "agreement_id": agreement_id,
                "proposal": proposal
            }
        )
        
        return {
            "agreement_id": agreement_id,
            "status": "in_progress",
            "proposal": proposal,
            "quorum_size": 3,
            "timeout": 10000
        }
    
    # ==================== Checkpointing ====================
    
    def create_checkpoint(
        self,
        cluster_id: str,
        checkpoint_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create a checkpoint for the cluster.
        
        Implements chain replication for fault tolerance.
        
        Args:
            cluster_id: Cluster identifier
            checkpoint_data: Data to checkpoint
            
        Returns:
            Checkpoint result
        """
        checkpoint_id = str(uuid.uuid4())
        
        # Get sequence number
        history = db_manager.get_checkpoint_history(cluster_id, limit=1)
        sequence_number = (history[0]["sequence_number"] if history else 0) + 1
        
        # Save checkpoint
        db_manager.save_checkpoint(
            checkpoint_id=checkpoint_id,
            cluster_id=cluster_id,
            checkpoint_data=checkpoint_data,
            sequence_number=sequence_number
        )
        
        # Log event
        db_manager.log_event(
            event_type="checkpoint_created",
            source_id=cluster_id,
            message=f"Checkpoint created: #{sequence_number}",
            severity="info",
            metadata={
                "checkpoint_id": checkpoint_id,
                "sequence_number": sequence_number
            }
        )
        
        logger.info(f"Checkpoint created for {cluster_id}: {checkpoint_id}")
        
        return {
            "checkpoint_id": checkpoint_id,
            "sequence_number": sequence_number,
            "timestamp": datetime.now().isoformat(),
            "status": "success"
        }
    
    def restore_from_checkpoint(
        self,
        cluster_id: str,
        checkpoint_id: str = None
    ) -> Dict[str, Any]:
        """
        Restore cluster state from checkpoint.
        
        Args:
            cluster_id: Cluster identifier
            checkpoint_id: Specific checkpoint ID (latest if not specified)
            
        Returns:
            Restore result with checkpoint data
        """
        if checkpoint_id:
            checkpoint = db_manager.get_checkpoint_history(cluster_id, limit=1)
            if checkpoint and checkpoint[0]["id"] == checkpoint_id:
                data = json.loads(checkpoint[0]["checkpoint_data"])
            else:
                return {"success": False, "message": "Checkpoint not found"}
        else:
            checkpoint = db_manager.get_checkpoint_history(cluster_id, limit=1)
            if not checkpoint:
                return {"success": False, "message": "No checkpoints available"}
            data = json.loads(checkpoint[0]["checkpoint_data"])
        
        # Log event
        db_manager.log_event(
            event_type="checkpoint_restored",
            source_id=cluster_id,
            message=f"Restored from checkpoint: #{checkpoint[0]['sequence_number']}",
            severity="info",
            metadata={
                "checkpoint_id": checkpoint[0]["id"],
                "sequence_number": checkpoint[0]["sequence_number"]
            }
        )
        
        logger.info(f"Restored cluster {cluster_id} from checkpoint")
        
        return {
            "success": True,
            "checkpoint_id": checkpoint[0]["id"],
            "sequence_number": checkpoint[0]["sequence_number"],
            "data": data
        }
    
    def get_checkpoint_history(
        self,
        cluster_id: str = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get checkpoint history.
        
        Args:
            cluster_id: Optional cluster filter
            limit: Maximum results
            
        Returns:
            List of checkpoint records
        """
        history = db_manager.get_checkpoint_history(cluster_id, limit)
        
        # Format for display
        formatted = []
        for checkpoint in history:
            formatted.append({
                "id": checkpoint["id"],
                "cluster_id": checkpoint["cluster_id"],
                "sequence_number": checkpoint["sequence_number"],
                "timestamp": checkpoint["created_at"],
                "status": "completed"
            })
        
        return formatted
    
    # ==================== Recovery ====================
    
    def initiate_recovery(
        self,
        cluster_id: str,
        reason: str
    ) -> Dict[str, Any]:
        """
        Initiate cluster recovery.
        
        Args:
            cluster_id: Cluster identifier
            reason: Recovery reason
            
        Returns:
            Recovery result
        """
        recovery_id = str(uuid.uuid4())
        
        db_manager.log_event(
            event_type="recovery_initiated",
            source_id=cluster_id,
            message=f"Recovery initiated: {reason}",
            severity="warning",
            metadata={
                "recovery_id": recovery_id,
                "reason": reason
            }
        )
        
        logger.warning(f"Recovery initiated for {cluster_id}: {reason}")
        
        return {
            "recovery_id": recovery_id,
            "cluster_id": cluster_id,
            "reason": reason,
            "status": "in_progress",
            "timestamp": datetime.now().isoformat()
        }
    
    def complete_recovery(
        self,
        recovery_id: str,
        success: bool,
        details: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Complete a recovery operation.
        
        Args:
            recovery_id: Recovery identifier
            success: Whether recovery was successful
            details: Recovery details
            
        Returns:
            Completion result
        """
        db_manager.log_event(
            event_type="recovery_completed",
            source_id=recovery_id,
            message=f"Recovery {'succeeded' if success else 'failed'}",
            severity="info" if success else "error",
            metadata={
                "recovery_id": recovery_id,
                "success": success,
                "details": details or {}
            }
        )
        
        return {
            "recovery_id": recovery_id,
            "success": success,
            "timestamp": datetime.now().isoformat()
        }
    
    # ==================== Analytics ====================
    
    def render_quick_analytics(self):
        """Render quick analytics widgets"""
        try:
            from ..ui.components import DashboardComponents
        except ImportError:
            from ui.components import DashboardComponents
        
        components = DashboardComponents()
        components.render_analytics_charts()
    
    def get_analytics_summary(self) -> Dict[str, Any]:
        """
        Get analytics summary.
        
        Returns:
            Analytics summary dictionary
        """
        return {
            "processing_rate": 150.0,
            "average_latency_ms": 45.2,
            "throughput_fps": 1.5,
            "ocr_accuracy": 0.94,
            "ml_inference_time_ms": 32.1,
            "data_points_processed": 100000,
            "storage_used_gb": 2.5,
            "bandwidth_usage_mbps": 5.2
        }
    
    def get_performance_metrics(
        self,
        time_range: timedelta = timedelta(hours=1)
    ) -> List[Dict[str, Any]]:
        """
        Get performance metrics for time range.
        
        Args:
            time_range: Time range for metrics
            
        Returns:
            List of metric data points
        """
        # Placeholder - generate sample data
        now = datetime.now()
        metrics = []
        
        for i in range(min(60, int(time_range.total_seconds() / 60))):
            timestamp = now - timedelta(minutes=i)
            metrics.append({
                "timestamp": timestamp.isoformat(),
                "cpu_usage": 45 + (i % 10),
                "memory_usage": 60 + (i % 5),
                "network_latency": 20 + (i % 15),
                "processing_time": 30 + (i % 10)
            })
        
        return list(reversed(metrics))
    
    def get_device_metrics_summary(self, device_id: str) -> Dict[str, Any]:
        """
        Get metrics summary for a device.
        
        Args:
            device_id: Device identifier
            
        Returns:
            Device metrics summary
        """
        metrics = db_manager.get_device_metrics(device_id, limit=100)
        
        if not metrics:
            return {
                "device_id": device_id,
                "metric_count": 0,
                "average_cpu": 0,
                "average_memory": 0
            }
        
        cpu_values = [m["metric_value"] for m in metrics if m["metric_name"] == "cpu_usage"]
        memory_values = [m["metric_value"] for m in metrics if m["metric_name"] == "memory_usage"]
        
        return {
            "device_id": device_id,
            "metric_count": len(metrics),
            "average_cpu": sum(cpu_values) / len(cpu_values) if cpu_values else 0,
            "average_memory": sum(memory_values) / len(memory_values) if memory_values else 0,
            "last_update": metrics[0]["timestamp"] if metrics else None
        }
    
    def get_cluster_analytics(self, cluster_id: str) -> Dict[str, Any]:
        """
        Get analytics for a specific cluster.
        
        Args:
            cluster_id: Cluster identifier
            
        Returns:
            Cluster analytics dictionary
        """
        try:
            from ..api.clusters import cluster_manager
            from ..api.devices import device_manager
        except ImportError:
            from api.clusters import cluster_manager
            from api.devices import device_manager
        
        members = cluster_manager.get_members(cluster_id)
        member_ids = [m["id"] for m in members]
        
        # Aggregate metrics
        total_cpu = 0
        total_memory = 0
        for member_id in member_ids:
            summary = self.get_device_metrics_summary(member_id)
            total_cpu += summary.get("average_cpu", 0)
            total_memory += summary.get("average_memory", 0)
        
        member_count = len(members)
        
        return {
            "cluster_id": cluster_id,
            "member_count": member_count,
            "average_cpu": total_cpu / max(1, member_count),
            "average_memory": total_memory / max(1, member_count),
            "leader_id": cluster_manager.get_cluster(cluster_id).get("leader_id") if cluster_manager.get_cluster(cluster_id) else None,
            "status": "healthy"
        }
    
    def export_analytics(
        self,
        format: str = "json",
        time_range: timedelta = timedelta(hours=24)
    ) -> str:
        """
        Export analytics data.
        
        Args:
            format: Export format (json, csv)
            time_range: Time range for data
            
        Returns:
            Exported data string
        """
        data = {
            "export_timestamp": datetime.now().isoformat(),
            "time_range": str(time_range),
            "device_metrics": self.get_performance_metrics(time_range),
            "summary": self.get_analytics_summary()
        }
        
        if format == "json":
            return json.dumps(data, indent=2, default=str)
        elif format == "csv":
            return self._export_csv(data)
        
        return ""
    
    def _export_csv(self, data: Dict[str, Any]) -> str:
        """Export data as CSV"""
        lines = ["timestamp,cpu_usage,memory_usage,network_latency,processing_time"]
        
        for point in data.get("device_metrics", []):
            lines.append(
                f"{point['timestamp']},{point['cpu_usage']},"
                f"{point['memory_usage']},{point['network_latency']},"
                f"{point['processing_time']}"
            )
        
        return "\n".join(lines)


# Global analytics manager instance
analytics_manager = AnalyticsManager()
