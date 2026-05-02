"""
DASAS Android Device Client
============================
Client script to run on Android devices to connect to the DASAS dashboard.
Requires: Python 3.7+ with requests and psutil

Install dependencies:
    pip install requests psutil

Run with:
    python android_client.py --name "My Phone" --server http://your-dashboard-ip:8501

For Termux on Android:
    termux-setup-storage
    pip install requests psutil
    python android_client.py --name "My Phone" --server http://your-dashboard-ip:8501
"""

import argparse
import json
import os
import platform
import socket
import time
import uuid
import requests
from datetime import datetime
from typing import Any, Dict, Optional

# Try to import psutil, provide fallback if not available
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    print("Warning: psutil not installed. Install with: pip install psutil")


class DASASClient:
    """Client for connecting Android device to DASAS dashboard"""
    
    def __init__(self, name: str, server_url: str, device_id: str = None):
        """
        Initialize DASAS client.
        
        Args:
            name: Device name
            server_url: DASAS dashboard URL
            device_id: Unique device ID (auto-generated if not provided)
        """
        self.name = name
        self.server_url = server_url.rstrip('/')
        self.device_id = device_id or str(uuid.uuid4())
        self.registration_id = None
        self.running = False
        
        # Get device info
        self.device_info = self._get_device_info()
    
    def _get_device_info(self) -> Dict[str, Any]:
        """Get device information"""
        info = {
            "device_id": self.device_id,
            "name": self.name,
            "device_type": "android",
            "ip_address": self._get_ip_address(),
            "mac_address": self._get_mac_address(),
            "android_version": self._get_android_version(),
            "manufacturer": self._get_manufacturer(),
            "model": self._get_model(),
            "sdk_version": self._get_sdk_version(),
        }
        
        if PSUTIL_AVAILABLE:
            info["cpu_cores"] = psutil.cpu_count()
            info["total_memory"] = psutil.virtual_memory().total
        
        return info
    
    def _get_ip_address(self) -> str:
        """Get device IP address"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "127.0.0.1"
    
    def _get_mac_address(self) -> str:
        """Get device MAC address"""
        try:
            mac = uuid.getnode()
            return ':'.join(f'{(mac >> i) & 0xff:02x}' for i in range(0, 48, 8))
        except Exception:
            return "unknown"
    
    def _get_android_version(self) -> str:
        """Get Android version"""
        try:
            # Try Android-specific paths
            with open('/system/build.prop', 'r') as f:
                for line in f:
                    if line.startswith('ro.build.version.release='):
                        return line.split('=')[1].strip()
        except Exception:
            pass
        
        # Fallback to platform
        return platform.release() or "Unknown"
    
    def _get_manufacturer(self) -> str:
        """Get device manufacturer"""
        try:
            with open('/system/build.prop', 'r') as f:
                for line in f:
                    if line.startswith('ro.product.manufacturer='):
                        return line.split('=')[1].strip()
        except Exception:
            pass
        return "Unknown"
    
    def _get_model(self) -> str:
        """Get device model"""
        try:
            with open('/system/build.prop', 'r') as f:
                for line in f:
                    if line.startswith('ro.product.model='):
                        return line.split('=')[1].strip()
        except Exception:
            pass
        return platform.machine() or "Unknown"
    
    def _get_sdk_version(self) -> int:
        """Get Android SDK version"""
        try:
            with open('/system/build.prop', 'r') as f:
                for line in f:
                    if line.startswith('ro.build.version.sdk='):
                        return int(line.split('=')[1].strip())
        except Exception:
            pass
        return 0
    
    def _get_metrics(self) -> Dict[str, Any]:
        """Get current device metrics"""
        metrics = {}
        
        if PSUTIL_AVAILABLE:
            metrics["cpu_usage"] = psutil.cpu_percent(interval=None)
            metrics["memory_usage"] = psutil.virtual_memory().percent
            metrics["battery_level"] = self._get_battery_level()
            metrics["disk_usage"] = psutil.disk_usage('/').percent
        else:
            # Fallback metrics
            metrics["cpu_usage"] = 0
            metrics["memory_usage"] = 0
            metrics["battery_level"] = 100
            metrics["disk_usage"] = 0
        
        return metrics
    
    def _get_battery_level(self) -> int:
        """Get battery level"""
        try:
            # Try Android-specific paths
            if os.path.exists('/sys/class/power_supply/battery/capacity'):
                with open('/sys/class/power_supply/battery/capacity', 'r') as f:
                    return int(f.read().strip())
        except Exception:
            pass
        return 100  # Assume full battery if can't read
    
    def register(self) -> bool:
        """Register device with DASAS dashboard"""
        try:
            # First, try to register via API
            response = requests.post(
                f"{self.server_url}/api/devices/register",
                json={
                    "name": self.name,
                    "device_info": self.device_info
                },
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    print(f"✅ Device registered: {result.get('device_id')}")
                    return True
            
            # Fallback: Direct database registration (for local testing)
            print("⚠️ API not available, using direct registration...")
            return self._direct_register()
            
        except requests.exceptions.ConnectionError:
            print(f"❌ Cannot connect to {self.server_url}")
            print("Make sure the DASAS dashboard is running")
            return False
        except Exception as e:
            print(f"❌ Registration error: {e}")
            return False
    
    def _direct_register(self) -> bool:
        """Direct database registration (for SQLite)"""
        try:
            import sqlite3
            db_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                'data', 'dasas_admin.db'
            )
            
            if not os.path.exists(db_path):
                print(f"❌ Database not found: {db_path}")
                return False
            
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Check if device exists
            cursor.execute("SELECT id FROM devices WHERE id = ?", (self.device_id,))
            if cursor.fetchone():
                print(f"✅ Device already registered: {self.device_id}")
                conn.close()
                return True
            
            # Insert device
            cursor.execute("""
                INSERT INTO devices (
                    id, name, device_type, status, ip_address, mac_address,
                    cpu_cores, total_memory, android_version, last_heartbeat
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                self.device_id,
                self.name,
                'android',
                'online',
                self.device_info.get('ip_address'),
                self.device_info.get('mac_address'),
                self.device_info.get('cpu_cores'),
                self.device_info.get('total_memory'),
                self.device_info.get('android_version'),
                datetime.now().isoformat()
            ))
            
            conn.commit()
            conn.close()
            print(f"✅ Device registered directly: {self.device_id}")
            return True
            
        except Exception as e:
            print(f"❌ Direct registration error: {e}")
            return False
    
    def send_heartbeat(self) -> bool:
        """Send heartbeat to DASAS dashboard"""
        try:
            metrics = self._get_metrics()
            
            response = requests.post(
                f"{self.server_url}/api/devices/heartbeat",
                json={
                    "device_id": self.device_id,
                    "metrics": metrics
                },
                timeout=10
            )
            
            if response.status_code == 200:
                return True
            
            return False
            
        except Exception:
            # If API not available, update directly
            return self._direct_heartbeat()
    
    def _direct_heartbeat(self) -> bool:
        """Direct heartbeat update (for SQLite)"""
        try:
            import sqlite3
            db_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                'data', 'dasas_admin.db'
            )
            
            if not os.path.exists(db_path):
                return False
            
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Update device status
            cursor.execute("""
                UPDATE devices SET status = 'online', last_heartbeat = ? WHERE id = ?
            """, (datetime.now().isoformat(), self.device_id))
            
            # Record metrics
            metrics = self._get_metrics()
            for metric_name, metric_value in metrics.items():
                cursor.execute("""
                    INSERT INTO device_metrics (device_id, metric_name, metric_value)
                    VALUES (?, ?, ?)
                """, (self.device_id, metric_name, metric_value))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception:
            return False
    
    def run(self, interval: int = 30):
        """
        Run the client.
        
        Args:
            interval: Heartbeat interval in seconds
        """
        print(f"\n📱 DASAS Android Client")
        print(f"   Device: {self.name}")
        print(f"   Device ID: {self.device_id}")
        print(f"   Server: {self.server_url}")
        print(f"   Heartbeat Interval: {interval}s")
        print("-" * 40)
        
        # Register device
        if not self.register():
            print("❌ Failed to register device. Exiting.")
            return
        
        self.running = True
        
        try:
            while self.running:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Sending heartbeat...")
                
                if self.send_heartbeat():
                    print("   ✅ Heartbeat sent")
                else:
                    print("   ⚠️ Heartbeat failed")
                
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("\n🛑 Client stopped by user")
            self.stop()
    
    def stop(self):
        """Stop the client"""
        self.running = False
        print("👋 Goodbye!")


def main():
    parser = argparse.ArgumentParser(description="DASAS Android Device Client")
    parser.add_argument(
        "--name", "-n",
        default="Android Device",
        help="Device name"
    )
    parser.add_argument(
        "--server", "-s",
        default="http://localhost:8501",
        help="DASAS dashboard URL"
    )
    parser.add_argument(
        "--device-id", "-d",
        default=None,
        help="Device ID (auto-generated if not provided)"
    )
    parser.add_argument(
        "--interval", "-i",
        type=int,
        default=30,
        help="Heartbeat interval in seconds"
    )
    
    args = parser.parse_args()
    
    client = DASASClient(
        name=args.name,
        server_url=args.server,
        device_id=args.device_id
    )
    
    client.run(interval=args.interval)


if __name__ == "__main__":
    main()
