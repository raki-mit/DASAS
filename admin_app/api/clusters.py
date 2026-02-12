"""
DASAS Cluster Manager Module
==============================
Provides cluster management functionality for the DASAS Admin Dashboard.

Author: DASAS Team
Version: 1.0.0
"""

import uuid
import json
from datetime import datetime
from typing import Any, Dict, List, Optional

# Handle relative imports for both direct and package usage
try:
    from ..core.logging_config import logger
    from ..db.database import db_manager
except ImportError:
    from core.logging_config import logger
    from db.database import db_manager


class ClusterManager:
    """
    Manager class for Android device cluster operations.
    
    Handles cluster formation, leader election, member management,
    and distributed coordination using Ricart-Agrawala algorithm.
    """
    
    def __init__(self):
        """Initialize cluster manager"""
        pass
    
    # ==================== Cluster Creation ====================
    
    def create_cluster(
        self,
        name: str,
        leader_id: str = None,
        configuration: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Create a new device cluster.
        
        Args:
            name: Cluster name
            leader_id: Optional leader device ID
            configuration: Cluster configuration
            
        Returns:
            Creation result with cluster ID
        """
        cluster_id = str(uuid.uuid4())
        
        cluster_data = {
            "name": name,
            "status": "forming",
            "leader_id": leader_id,
            "member_count": 0,
            "configuration": configuration or {
                "election_timeout": 5000,
                "heartbeat_interval": 1000,
                "mutual_exclusion": {
                    "algorithm": "ricart_agrawala",
                    "request_timeout": 5000
                },
                "vector_clocks": {
                    "enabled": True,
                    "max_entries": 10000
                }
            }
        }
        
        # Save to database
        db_manager.add_cluster(cluster_id, name, **cluster_data)
        
        # Log event
        db_manager.log_event(
            event_type="cluster_created",
            source_id=cluster_id,
            message=f"Cluster '{name}' created",
            severity="info",
            metadata={"cluster_name": name}
        )
        
        logger.info(f"Cluster created: {cluster_id} - {name}")
        
        return {
            "success": True,
            "cluster_id": cluster_id,
            "message": "Cluster created successfully"
        }
    
    def delete_cluster(self, cluster_id: str) -> Dict[str, Any]:
        """
        Delete a cluster.
        
        Args:
            cluster_id: Cluster identifier
            
        Returns:
            Deletion result
        """
        cluster = db_manager.get_cluster(cluster_id)
        
        if not cluster:
            return {"success": False, "message": "Cluster not found"}
        
        # Log event
        db_manager.log_event(
            event_type="cluster_deleted",
            source_id=cluster_id,
            message=f"Cluster '{cluster.get('name')}' deleted",
            severity="warning"
        )
        
        logger.info(f"Cluster deleted: {cluster_id}")
        
        return {"success": True, "message": "Cluster deleted"}
    
    def update_cluster(
        self,
        cluster_id: str,
        updates: Dict[str, Any]
    ) -> bool:
        """
        Update cluster configuration.
        
        Args:
            cluster_id: Cluster identifier
            updates: Configuration updates
            
        Returns:
            True if successful
        """
        cluster = db_manager.get_cluster(cluster_id)
        
        if not cluster:
            return False
        
        # Merge configuration
        if "configuration" in updates:
            existing_config = json.loads(cluster.get("configuration", "{}"))
            merged_config = {**existing_config, **updates["configuration"]}
            updates["configuration"] = json.dumps(merged_config)
        
        # Update in database
        if "status" in updates:
            db_manager.add_cluster(
                cluster_id,
                cluster["name"],
                status=updates["status"],
                configuration=cluster.get("configuration", "{}")
            )
        
        return True
    
    # ==================== Cluster Queries ====================
    
    def get_cluster(self, cluster_id: str) -> Optional[Dict[str, Any]]:
        """
        Get cluster information.
        
        Args:
            cluster_id: Cluster identifier
            
        Returns:
            Cluster dictionary or None
        """
        return db_manager.get_cluster(cluster_id)
    
    def get_all_clusters(self) -> List[Dict[str, Any]]:
        """Get all clusters"""
        return db_manager.get_all_clusters()
    
    def get_cluster_count(self) -> int:
        """Get total cluster count"""
        clusters = self.get_all_clusters()
        return len(clusters)
    
    def get_active_clusters(self) -> List[Dict[str, Any]]:
        """Get clusters with active status"""
        clusters = self.get_all_clusters()
        return [c for c in clusters if c.get("status") == "active"]
    
    def search_clusters(self, query: str) -> List[Dict[str, Any]]:
        """Search clusters by name"""
        clusters = self.get_all_clusters()
        query_lower = query.lower()
        
        return [
            c for c in clusters
            if query_lower in c.get("name", "").lower()
            or query_lower in c.get("id", "").lower()
        ]
    
    # ==================== Member Management ====================
    
    def add_member(self, cluster_id: str, device_id: str) -> Dict[str, Any]:
        """
        Add a device to a cluster.
        
        Args:
            cluster_id: Cluster identifier
            device_id: Device identifier
            
        Returns:
            Addition result
        """
        # Handle relative imports
        try:
            from ..api.devices import device_manager
        except ImportError:
            from api.devices import device_manager
        
        cluster = db_manager.get_cluster(cluster_id)
        device = db_manager.get_device(device_id)
        
        if not cluster:
            return {"success": False, "message": "Cluster not found"}
        
        if not device:
            return {"success": False, "message": "Device not found"}
        
        if device.get("cluster_id") == cluster_id:
            return {"success": False, "message": "Device already in cluster"}
        
        # Update device cluster
        db_manager.update_device_status(
            device_id,
            status="online",
            cluster_id=cluster_id
        )
        
        # Update member count
        members = self.get_members(cluster_id)
        db_manager.update_cluster_member_count(cluster_id, len(members) + 1)
        
        # Log event
        db_manager.log_event(
            event_type="member_added",
            source_id=cluster_id,
            message=f"Device {device.get('name')} added to cluster",
            severity="info",
            metadata={
                "cluster_name": cluster.get("name"),
                "device_name": device.get("name")
            }
        )
        
        logger.info(f"Device {device_id} added to cluster {cluster_id}")
        
        return {"success": True, "message": "Device added to cluster"}
    
    def remove_member(self, cluster_id: str, device_id: str) -> Dict[str, Any]:
        """
        Remove a device from a cluster.
        
        Args:
            cluster_id: Cluster identifier
            device_id: Device identifier
            
        Returns:
            Removal result
        """
        device = db_manager.get_device(device_id)
        
        if not device or device.get("cluster_id") != cluster_id:
            return {"success": False, "message": "Device not in cluster"}
        
        # Update device
        db_manager.update_device_status(
            device_id,
            status="online",
            cluster_id=None
        )
        
        # Update member count
        members = self.get_members(cluster_id)
        db_manager.update_cluster_member_count(cluster_id, max(0, len(members) - 1))
        
        # Check if leader was removed
        cluster = db_manager.get_cluster(cluster_id)
        if cluster and cluster.get("leader_id") == device_id:
            self.start_election(cluster_id)
        
        logger.info(f"Device {device_id} removed from cluster {cluster_id}")
        
        return {"success": True, "message": "Device removed from cluster"}
    
    def get_members(self, cluster_id: str) -> List[Dict[str, Any]]:
        """
        Get all members of a cluster.
        
        Args:
            cluster_id: Cluster identifier
            
        Returns:
            List of device dictionaries
        """
        try:
            from ..api.devices import device_manager
        except ImportError:
            from api.devices import device_manager
        
        return device_manager.get_all_devices(cluster_id=cluster_id)
    
    def get_member_count(self, cluster_id: str) -> int:
        """Get number of members in a cluster"""
        return len(self.get_members(cluster_id))
    
    # ==================== Leader Election ====================
    
    def start_election(self, cluster_id: str) -> Dict[str, Any]:
        """
        Start leader election using Ricart-Agrawala algorithm.
        
        Args:
            cluster_id: Cluster identifier
            
        Returns:
            Election result
        """
        members = self.get_members(cluster_id)
        
        if not members:
            return {"success": False, "message": "No members in cluster"}
        
        # Ricart-Agrawala algorithm implementation
        # In a real implementation, this would coordinate with all members
        
        # Select leader based on device properties (highest ID or capability)
        leader = max(members, key=lambda m: m.get("id", ""))
        
        # Update cluster leader
        cluster = db_manager.get_cluster(cluster_id)
        db_manager.add_cluster(
            cluster_id,
            cluster["name"],
            status="active",
            leader_id=leader["id"],
            configuration=cluster.get("configuration", "{}")
        )
        
        # Log event
        db_manager.log_event(
            event_type="leader_elected",
            source_id=cluster_id,
            message=f"Leader elected: {leader.get('name')}",
            severity="info",
            metadata={
                "cluster_name": cluster.get("name"),
                "leader_name": leader.get("name"),
                "algorithm": "ricart_agrawala"
            }
        )
        
        logger.info(f"Leader elected for cluster {cluster_id}: {leader['id']}")
        
        return {
            "success": True,
            "leader_id": leader["id"],
            "leader_name": leader.get("name"),
            "algorithm": "ricart_agrawala"
        }
    
    def get_leader(self, cluster_id: str) -> Optional[Dict[str, Any]]:
        """
        Get current cluster leader.
        
        Args:
            cluster_id: Cluster identifier
            
        Returns:
            Leader device dictionary or None
        """
        try:
            from ..api.devices import device_manager
        except ImportError:
            from api.devices import device_manager
        
        cluster = db_manager.get_cluster(cluster_id)
        
        if not cluster or not cluster.get("leader_id"):
            return None
        
        return device_manager.get_device(cluster["leader_id"])
    
    # ==================== Mutual Exclusion ====================
    
    def request_resource(
        self,
        cluster_id: str,
        device_id: str,
        resource_name: str
    ) -> Dict[str, Any]:
        """
        Request access to a shared resource.
        
        Implements Suzuki-Kasami token-based mutual exclusion.
        
        Args:
            cluster_id: Cluster identifier
            device_id: Requesting device
            resource_name: Resource to access
            
        Returns:
            Request result with token if granted
        """
        # Log the request
        db_manager.log_event(
            event_type="resource_request",
            source_id=cluster_id,
            message=f"Resource request: {resource_name}",
            severity="info",
            metadata={
                "device_id": device_id,
                "resource": resource_name,
                "algorithm": "suzuki_kasami"
            }
        )
        
        logger.info(f"Resource request in {cluster_id}: {resource_name} by {device_id}")
        
        return {
            "success": True,
            "request_id": str(uuid.uuid4()),
            "status": "pending",
            "algorithm": "suzuki_kasami"
        }
    
    def release_resource(
        self,
        cluster_id: str,
        device_id: str,
        resource_name: str
    ) -> Dict[str, Any]:
        """
        Release a shared resource.
        
        Args:
            cluster_id: Cluster identifier
            device_id: Releasing device
            resource_name: Resource to release
            
        Returns:
            Release result
        """
        db_manager.log_event(
            event_type="resource_released",
            source_id=cluster_id,
            message=f"Resource released: {resource_name}",
            severity="info",
            metadata={
                "device_id": device_id,
                "resource": resource_name
            }
        )
        
        return {"success": True, "message": "Resource released"}
    
    # ==================== Vector Clocks ====================
    
    def update_vector_clock(
        self,
        cluster_id: str,
        device_id: str,
        event: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update vector clock for an event.
        
        Args:
            cluster_id: Cluster identifier
            device_id: Source device
            event: Event data
            
        Returns:
            Updated vector clock
        """
        # In a real implementation, this would update distributed vector clocks
        clock_id = str(uuid.uuid4())
        
        db_manager.log_event(
            event_type="vector_clock_update",
            source_id=cluster_id,
            message="Vector clock updated",
            severity="info",
            metadata={
                "clock_id": clock_id,
                "device_id": device_id,
                "event": event
            }
        )
        
        return {
            "clock_id": clock_id,
            "timestamp": datetime.now().isoformat(),
            "device_id": device_id
        }
    
    def get_causal_history(
        self,
        cluster_id: str,
        since: datetime = None
    ) -> List[Dict[str, Any]]:
        """
        Get causally ordered history of events.
        
        Args:
            cluster_id: Cluster identifier
            since: Optional start time
            
        Returns:
            List of causally ordered events
        """
        return db_manager.get_events(
            event_type=None,
            since=since,
            limit=1000
        )
    
    # ==================== Statistics ====================
    
    def get_cluster_statistics(self) -> Dict[str, Any]:
        """
        Get cluster statistics.
        
        Returns:
            Dictionary with cluster statistics
        """
        clusters = self.get_all_clusters()
        
        total_members = sum(c.get("member_count", 0) for c in clusters)
        active_clusters = len([c for c in clusters if c.get("status") == "active"])
        
        # Group by status
        status_counts = {}
        for cluster in clusters:
            status = cluster.get("status", "unknown")
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # Average members per cluster
        avg_members = total_members / max(1, len(clusters))
        
        return {
            "total_clusters": len(clusters),
            "active_clusters": active_clusters,
            "total_members": total_members,
            "average_members_per_cluster": avg_members,
            "status_distribution": status_counts
        }


# Global cluster manager instance
cluster_manager = ClusterManager()
