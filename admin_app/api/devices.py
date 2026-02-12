"""
DASAS Device Manager Module
=============================
Provides device management functionality for the DASAS Admin Dashboard.

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

try:
    from ..core.metrics import DeviceMetrics
except ImportError:
    from core.metrics import DeviceMetrics


class DeviceManager:
    """
    Manager class for Android device operations.
    
    Handles device registration, status updates, monitoring,
    and communication with registered devices.
    """
    
    def __init__(self):
        """Initialize device manager"""
        self._device_cache: Dict[str, Dict[str, Any]] = {}
    
    # ==================== Device Registration ====================
    
    def register_device(
        self,
        name: str,
        device_info: Dict[str, Any],
        cluster_id: str = None
    ) -> Dict[str, Any]:
        """
        Register a new Android device.
        
        Args:
            name: Device name
            device_info: Device information dictionary
            cluster_id: Optional cluster to join
            
        Returns:
            Registration result with device ID
        """
        device_id = device_info.get("device_id", str(uuid.uuid4()))
        
        # Check if device already exists
        existing = db_manager.get_device(device_id)
        if existing:
            # Update existing device
            self.update_device(device_id, device_info)
            return {"success": True, "device_id": device_id, "message": "Device updated"}
        
        # Prepare device data
        device_data = {
            "device_id": device_id,
            "name": name,
            "device_type": device_info.get("device_type", "android"),
            "ip_address": device_info.get("ip_address"),
            "mac_address": device_info.get("mac_address"),
            "cpu_cores": device_info.get("cpu_cores"),
            "total_memory": device_info.get("total_memory"),
            "android_version": device_info.get("android_version"),
            "status": "online",
            "cluster_id": cluster_id,
            "metadata": {
                "manufacturer": device_info.get("manufacturer"),
                "model": device_info.get("model"),
                "sdk_version": device_info.get("sdk_version"),
                "capabilities": device_info.get("capabilities", [])
            }
        }
        
        # Save to database
        db_manager.add_device(device_id, name, **device_data)
        
        # Log event
        db_manager.log_event(
            event_type="device_registered",
            source_id=device_id,
            message=f"Device {name} registered successfully",
            severity="info",
            metadata=device_data
        )
        
        logger.info(f"Device registered: {device_id} - {name}")
        
        return {
            "success": True,
            "device_id": device_id,
            "message": "Device registered successfully"
        }
    
    def update_device(self, device_id: str, device_info: Dict[str, Any]) -> bool:
        """
        Update device information.
        
        Args:
            device_id: Device identifier
            device_info: Updated device information
            
        Returns:
            True if successful
        """
        return db_manager.update_device_status(
            device_id,
            status=device_info.get("status", "online"),
            **device_info
        )
    
    def unregister_device(self, device_id: str) -> bool:
        """
        Unregister a device.
        
        Args:
            device_id: Device identifier
            
        Returns:
            True if successful
        """
        # Set device to offline
        db_manager.update_device_status(device_id, "offline")
        
        # Log event
        db_manager.log_event(
            event_type="device_unregistered",
            source_id=device_id,
            message=f"Device {device_id} unregistered",
            severity="info"
        )
        
        logger.info(f"Device unregistered: {device_id}")
        return True
    
    # ==================== Device Queries ====================
    
    def get_device(self, device_id: str) -> Optional[Dict[str, Any]]:
        """
        Get device information.
        
        Args:
            device_id: Device identifier
            
        Returns:
            Device information dictionary or None
        """
        return db_manager.get_device(device_id)
    
    def get_all_devices(
        self,
        status: str = None,
        cluster_id: str = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get all registered devices.
        
        Args:
            status: Filter by status
            cluster_id: Filter by cluster
            limit: Maximum results
            
        Returns:
            List of device dictionaries
        """
        return db_manager.get_all_devices(status, cluster_id, limit)
    
    def get_online_devices(self) -> List[Dict[str, Any]]:
        """Get all online devices"""
        return self.get_all_devices(status="online")
    
    def get_offline_devices(self) -> List[Dict[str, Any]]:
        """Get all offline devices"""
        return self.get_all_devices(status="offline")
    
    def get_device_count(self, status: str = None) -> int:
        """Get device count"""
        return db_manager.get_device_count(status)
    
    def get_active_count(self) -> int:
        """Get count of devices with recent heartbeat"""
        timeout = timedelta(seconds=60)
        devices = self.get_all_devices()
        
        active_count = 0
        for device in devices:
            if device.get("last_heartbeat"):
                last_heartbeat = datetime.fromisoformat(
                    device["last_heartbeat"].replace("Z", "+00:00")
                )
                if datetime.now() - last_heartbeat < timeout:
                    active_count += 1
        
        return active_count
    
    def search_devices(self, query: str) -> List[Dict[str, Any]]:
        """
        Search devices by name or ID.
        
        Args:
            query: Search query
            
        Returns:
            List of matching devices
        """
        devices = self.get_all_devices(limit=1000)
        query_lower = query.lower()
        
        return [
            d for d in devices
            if query_lower in d.get("name", "").lower()
            or query_lower in d.get("id", "").lower()
        ]
    
    # ==================== Heartbeat Management ====================
    
    def process_heartbeat(
        self,
        device_id: str,
        heartbeat_data: Dict[str, Any]
    ) -> bool:
        """
        Process device heartbeat.
        
        Args:
            device_id: Device identifier
            heartbeat_data: Heartbeat data
            
        Returns:
            True if heartbeat processed
        """
        # Update device status
        db_manager.update_device_status(
            device_id,
            status="online",
            last_heartbeat=datetime.now().isoformat()
        )
        
        # Record metrics
        metrics = heartbeat_data.get("metrics", {})
        
        if "cpu_usage" in metrics:
            db_manager.record_device_metric(
                device_id, "cpu_usage", metrics["cpu_usage"]
            )
        
        if "memory_usage" in metrics:
            db_manager.record_device_metric(
                device_id, "memory_usage", metrics["memory_usage"]
            )
        
        if "battery_level" in metrics:
            db_manager.record_device_metric(
                device_id, "battery_level", metrics["battery_level"]
            )
        
        # Update cluster member count if device is in a cluster
        cluster_id = heartbeat_data.get("cluster_id")
        if cluster_id:
            cluster_devices = self.get_all_devices(cluster_id=cluster_id)
            db_manager.update_cluster_member_count(cluster_id, len(cluster_devices))
        
        return True
    
    def get_stale_devices(self, timeout_seconds: int = 60) -> List[Dict[str, Any]]:
        """
        Get devices that haven't sent heartbeat recently.
        
        Args:
            timeout_seconds: Heartbeat timeout
            
        Returns:
            List of stale device dictionaries
        """
        cutoff = datetime.now() - timedelta(seconds=timeout_seconds)
        devices = self.get_all_devices(status="online")
        
        stale_devices = []
        for device in devices:
            if device.get("last_heartbeat"):
                last_heartbeat = datetime.fromisoformat(
                    device["last_heartbeat"].replace("Z", "+00:00")
                )
                if last_heartbeat < cutoff:
                    stale_devices.append(device)
        
        return stale_devices
    
    # ==================== Device Control ====================
    
    def send_command(
        self,
        device_id: str,
        command: str,
        parameters: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Send a command to a device.
        
        Args:
            device_id: Target device
            command: Command to send
            parameters: Command parameters
            
        Returns:
            Command result
        """
        # In a real implementation, this would send via MQTT or gRPC
        command_id = str(uuid.uuid4())
        
        # Log the command
        db_manager.log_event(
            event_type="command_sent",
            source_id=device_id,
            message=f"Command '{command}' sent to device",
            severity="info",
            metadata={
                "command_id": command_id,
                "command": command,
                "parameters": parameters or {}
            }
        )
        
        logger.info(f"Command sent to {device_id}: {command}")
        
        return {
            "success": True,
            "command_id": command_id,
            "status": "queued"
        }
    
    def restart_device(self, device_id: str) -> Dict[str, Any]:
        """Send restart command to device"""
        return self.send_command(device_id, "restart")
    
    def update_device_config(
        self,
        device_id: str,
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update device configuration.
        
        Args:
            device_id: Device identifier
            config: New configuration
            
        Returns:
            Update result
        """
        return self.send_command(device_id, "update_config", config)
    
    def take_screenshot(self, device_id: str) -> Dict[str, Any]:
        """Request screenshot from device"""
        return self.send_command(device_id, "take_screenshot")
    
    # ==================== Device Groups ====================
    
    def get_devices_by_group(self, group_id: str) -> List[Dict[str, Any]]:
        """Get devices in a specific group"""
        devices = self.get_all_devices(limit=1000)
        
        return [
            d for d in devices
            if d.get("metadata", {}).get("group_id") == group_id
        ]
    
    def get_devices_by_model(self, model: str) -> List[Dict[str, Any]]:
        """Get devices by model"""
        devices = self.get_all_devices(limit=1000)
        
        return [
            d for d in devices
            if d.get("metadata", {}).get("model") == model
        ]
    
    # ==================== Statistics ====================
    
    def get_device_statistics(self) -> Dict[str, Any]:
        """
        Get device statistics.
        
        Returns:
            Dictionary with device statistics
        """
        devices = self.get_all_devices(limit=1000)
        
        online = len([d for d in devices if d.get("status") == "online"])
        offline = len([d for d in devices if d.get("status") == "offline"])
        in_clusters = len([d for d in devices if d.get("cluster_id")])
        
        # Group by status
        status_counts = {}
        for device in devices:
            status = device.get("status", "unknown")
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # Group by Android version
        version_counts = {}
        for device in devices:
            version = device.get("android_version", "unknown")
            version_counts[version] = version_counts.get(version, 0) + 1
        
        return {
            "total": len(devices),
            "online": online,
            "offline": offline,
            "in_clusters": in_clusters,
            "status_distribution": status_counts,
            "android_version_distribution": version_counts,
            "active_percentage": (online / max(1, len(devices))) * 100
        }
    
    def get_all_nodes(self) -> List[Dict[str, Any]]:
        """
        Get all device nodes for fault tolerance monitoring.
        
        Returns:
            List of device nodes with health scores
        """
        devices = self.get_all_devices(limit=1000)
        
        nodes = []
        for device in devices:
            # Calculate health score
            health_score = self._calculate_health_score(device)
            
            nodes.append({
                "id": device["id"],
                "name": device["name"],
                "status": device.get("status", "unknown"),
                "health_score": health_score,
                "cluster_id": device.get("cluster_id"),
                "last_heartbeat": device.get("last_heartbeat")
            })
        
        return nodes
    
    def _calculate_health_score(self, device: Dict[str, Any]) -> float:
        """
        Calculate health score for a device.
        
        Args:
            device: Device information
            
        Returns:
            Health score (0-100)
        """
        score = 100.0
        
        # Check status
        if device.get("status") != "online":
            score -= 50
        
        # Check heartbeat recency
        if device.get("last_heartbeat"):
            last_heartbeat = datetime.fromisoformat(
                device["last_heartbeat"].replace("Z", "+00:00")
            )
            elapsed = (datetime.now() - last_heartbeat).total_seconds()
            
            if elapsed > 60:
                score -= 30
            elif elapsed > 30:
                score -= 15
        
        # Check cluster membership
        if not device.get("cluster_id"):
            score -= 10
        
        return max(0, min(100, score))


# Global device manager instance
device_manager = DeviceManager()
