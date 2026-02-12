"""
DASAS UI Components Module
============================
Reusable UI components for the DASAS Admin Dashboard.

Author: DASAS Team
Version: 1.0.0
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from typing import Any, Dict, List, Optional

# Handle relative imports for both direct and package usage
try:
    from ..api.devices import device_manager
    from ..api.clusters import cluster_manager
    from ..api.analytics import analytics_manager
except ImportError:
    from api.devices import device_manager
    from api.clusters import cluster_manager
    from api.analytics import analytics_manager


class DashboardComponents:
    """
    Collection of reusable dashboard components.
    
    Provides methods for rendering common UI elements
    used across the DASAS admin dashboard.
    """
    
    def __init__(self):
        """Initialize components"""
        pass
    
    def render_header(self, title: str, subtitle: str = None):
        """
        Render page header.
        
        Args:
            title: Page title
            subtitle: Optional subtitle
        """
        st.title(title)
        if subtitle:
            st.markdown(f"*{subtitle}*")
        st.markdown("---")
    
    def render_metrics_row(self):
        """Render key metrics row"""
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            self._render_metric_card(
                "📱 Total Devices",
                device_manager.get_device_count(),
                icon="devices"
            )
        
        with col2:
            active = device_manager.get_active_count()
            total = device_manager.get_device_count()
            self._render_metric_card(
                "🟢 Active Devices",
                f"{active}/{total}",
                delta=active - (total - active) if total > 0 else 0,
                icon="active"
            )
        
        with col3:
            self._render_metric_card(
                "🔗 Active Clusters",
                cluster_manager.get_cluster_count(),
                icon="clusters"
            )
        
        with col4:
            self._render_metric_card(
                "⚡ Processing Rate",
                "150/sec",
                delta=12,
                icon="processing"
            )
    
    def _render_metric_card(
        self,
        label: str,
        value: Any,
        delta: int = None,
        icon: str = None
    ):
        """
        Render a single metric card.
        
        Args:
            label: Metric label
            value: Metric value
            optional_delta: Delta value
            icon: Icon identifier
        """
        st.metric(label=label, value=value, delta=delta)
    
    def render_device_distribution(self):
        """Render device distribution visualization"""
        st.subheader("📍 Device Distribution")
        
        stats = device_manager.get_device_statistics()
        
        # Create distribution data
        data = {
            "Status": list(stats.get("status_distribution", {}).keys()),
            "Count": list(stats.get("status_distribution", {}).values())
        }
        
        if data["Status"]:
            df = pd.DataFrame(data)
            st.bar_chart(df.set_index("Status"))
        else:
            st.info("No device status data available")
    
    def render_active_devices_table(self):
        """Render active devices table"""
        st.subheader("📱 Active Devices")
        
        devices = device_manager.get_all_devices(limit=50)
        
        if devices:
            # Format for display
            display_data = []
            for device in devices:
                display_data.append({
                    "ID": device.get("id", "")[:8] + "...",
                    "Name": device.get("name", "Unknown"),
                    "Status": self._get_status_badge(device.get("status", "offline")),
                    "Cluster": device.get("cluster_id", "N/A")[:8] + "..." if device.get("cluster_id") else "N/A",
                    "Android": device.get("android_version", "N/A"),
                    "Last Heartbeat": device.get("last_heartbeat", "Never")
                })
            
            df = pd.DataFrame(display_data)
            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No devices registered")
    
    def _get_status_badge(self, status: str) -> str:
        """Get HTML status badge"""
        colors = {
            "online": "🟢",
            "offline": "🔴",
            "busy": "🟡",
            "error": "🔴"
        }
        
        color = colors.get(status, "⚪")
        return f"{color} {status.title()}"
    
    def render_cluster_status(self):
        """Render cluster status section"""
        st.subheader("🔗 Cluster Status")
        
        clusters = cluster_manager.get_all_clusters()
        
        if clusters:
            for cluster in clusters[:5]:
                with st.expander(f"{cluster.get('name', 'Unknown')} ({cluster.get('status', 'unknown')})"):
                    st.write(f"**ID:** {cluster.get('id', 'N/A')[:8]}...")
                    st.write(f"**Members:** {cluster.get('member_count', 0)}")
                    st.write(f"**Leader:** {cluster.get('leader_id', 'N/A')[:8] if cluster.get('leader_id') else 'Not elected'}...")
        else:
            st.info("No clusters configured")
    
    def render_health_chart(self):
        """Render system health chart"""
        st.subheader("💚 System Health")
        
        # Generate sample health data
        import random
        health_data = []
        for i in range(24):
            health_data.append({
                "Hour": f"{i}:00",
                "Health Score": random.randint(85, 100)
            })
        
        df = pd.DataFrame(health_data)
        st.line_chart(df.set_index("Hour"))
    
    def render_analytics_charts(self):
        """Render analytics charts"""
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📈 Processing Throughput")
            
            # Sample throughput data
            throughput_data = {
                "Hour": ["00:00", "04:00", "08:00", "12:00", "16:00", "20:00"],
                "Events/sec": [120, 85, 200, 350, 280, 180]
            }
            
            df = pd.DataFrame(throughput_data)
            st.line_chart(df.set_index("Hour"))
        
        with col2:
            st.subheader("⏱️ Latency Distribution")
            
            # Sample latency data
            latency_data = [random.randint(20, 60) for _ in range(100)]
            st.bar_chart(pd.Series(latency_data).value_counts().sort_index())
        
        # Additional metrics
        st.subheader("📊 Key Performance Indicators")
        
        metrics = analytics_manager.get_analytics_summary()
        
        m1, m2, m3, m4 = st.columns(4)
        
        with m1:
            st.metric(
                "Avg Latency",
                f"{metrics.get('average_latency_ms', 0):.1f} ms",
                delta=-2.5
            )
        
        with m2:
            st.metric(
                "Throughput",
                f"{metrics.get('throughput_fps', 0):.1f} fps"
            )
        
        with m3:
            st.metric(
                "OCR Accuracy",
                f"{metrics.get('ocr_accuracy', 0):.1%}",
                delta=0.02
            )
        
        with m4:
            st.metric(
                "ML Inference",
                f"{metrics.get('ml_inference_time_ms', 0):.1f} ms"
            )
    
    def render_device_details(self, device_id: str):
        """
        Render detailed device information.
        
        Args:
            device_id: Device identifier
        """
        device = device_manager.get_device(device_id)
        
        if not device:
            st.error("Device not found")
            return
        
        # Device info
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Device Information")
            st.write(f"**ID:** {device.get('id', 'N/A')}")
            st.write(f"**Name:** {device.get('name', 'N/A')}")
            st.write(f"**Type:** {device.get('device_type', 'N/A')}")
            st.write(f"**Status:** {self._get_status_badge(device.get('status', 'unknown'))}")
            st.write(f"**Android Version:** {device.get('android_version', 'N/A')}")
        
        with col2:
            st.subheader("Hardware Information")
            st.write(f"**CPU Cores:** {device.get('cpu_cores', 'N/A')}")
            st.write(f"**Total Memory:** {device.get('total_memory', 'N/A')}")
            st.write(f"**IP Address:** {device.get('ip_address', 'N/A')}")
            st.write(f"**MAC Address:** {device.get('mac_address', 'N/A')}")
        
        # Metadata
        metadata = device.get("metadata", {})
        if metadata:
            st.subheader("Capabilities")
            capabilities = metadata.get("capabilities", [])
            if capabilities:
                st.write(", ".join(capabilities))
        
        # Actions
        st.subheader("Actions")
        
        action_col1, action_col2, action_col3 = st.columns(3)
        
        with action_col1:
            if st.button("📊 View Metrics", use_container_width=True):
                st.session_state.page = "device_metrics"
        
        with action_col2:
            if st.button("🔄 Restart", use_container_width=True):
                device_manager.restart_device(device_id)
                st.success("Restart command sent")
        
        with action_col3:
            if st.button("❌ Unregister", use_container_width=True):
                device_manager.unregister_device(device_id)
                st.success("Device unregistered")
    
    def render_cluster_details(self, cluster_id: str):
        """
        Render detailed cluster information.
        
        Args:
            cluster_id: Cluster identifier
        """
        cluster = cluster_manager.get_cluster(cluster_id)
        
        if not cluster:
            st.error("Cluster not found")
            return
        
        # Cluster info
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Cluster Information")
            st.write(f"**ID:** {cluster.get('id', 'N/A')}")
            st.write(f"**Name:** {cluster.get('name', 'N/A')}")
            st.write(f"**Status:** {cluster.get('status', 'N/A')}")
        
        with col2:
            st.subheader("Leadership")
            leader = cluster_manager.get_leader(cluster_id)
            if leader:
                st.write(f"**Leader:** {leader.get('name', 'N/A')}")
                st.write(f"**Leader ID:** {leader.get('id', 'N/A')[:8]}...")
            else:
                st.write("**Leader:** Not elected")
        
        # Members
        st.subheader(f"Members ({cluster.get('member_count', 0)})")
        members = cluster_manager.get_members(cluster_id)
        
        if members:
            member_data = []
            for member in members:
                member_data.append({
                    "Name": member.get("name", "Unknown"),
                    "Status": member.get("status", "unknown"),
                    "ID": member.get("id", "")[:8] + "..."
                })
            
            st.dataframe(
                pd.DataFrame(member_data),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No members in cluster")
        
        # Configuration
        config = cluster.get("configuration", {})
        if config:
            st.subheader("Configuration")
            if isinstance(config, str):
                config = eval(config)
            st.json(config)
    
    def render_event_log(self, limit: int = 50):
        """
        Render event log.
        
        Args:
            limit: Maximum events to display
        """
        try:
            from ..db.database import db_manager
        except ImportError:
            from db.database import db_manager
        
        events = db_manager.get_events(limit=limit)
        
        if events:
            # Format for display
            display_data = []
            for event in events:
                severity = event.get("severity", "info")
                severity_icons = {
                    "info": "ℹ️",
                    "warning": "⚠️",
                    "error": "❌",
                    "debug": "🔍"
                }
                icon = severity_icons.get(severity, "ℹ️")
                
                display_data.append({
                    "Time": event.get("timestamp", ""),
                    "Type": event.get("event_type", ""),
                    "Severity": f"{icon} {severity.title()}",
                    "Source": event.get("source_id", "N/A")[:8] + "..." if event.get("source_id") else "N/A",
                    "Message": event.get("message", "")
                })
            
            df = pd.DataFrame(display_data)
            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No events recorded")
    
    def render_alert_panel(self):
        """Render alert panel"""
        try:
            from ..db.database import db_manager
        except ImportError:
            from db.database import db_manager
        
        alerts = db_manager.get_active_alerts()
        
        if alerts:
            for alert in alerts:
                severity = alert.get("severity", "warning")
                if severity == "critical":
                    st.error(f"🚨 {alert.get('message', '')}")
                elif severity == "warning":
                    st.warning(f"⚠️ {alert.get('message', '')}")
                else:
                    st.info(f"ℹ️ {alert.get('message', '')}")
        else:
            st.success("✅ No active alerts")
    
    def render_command_panel(self, device_id: str):
        """
        Render command panel for a device.
        
        Args:
            device_id: Device identifier
        """
        st.subheader("📨 Send Command")
        
        command = st.selectbox(
            "Command",
            ["restart", "take_screenshot", "update_config", "get_logs"]
        )
        
        if command == "update_config":
            config = st.text_area(
                "Configuration (JSON)",
                value='{"key": "value"}'
            )
            try:
                config = eval(config)
            except:
                st.error("Invalid JSON configuration")
                return
        
        if st.button("Send Command", use_container_width=True):
            result = device_manager.send_command(
                device_id,
                command,
                config if command == "update_config" else None
            )
            if result.get("success"):
                st.success(f"Command sent: {result.get('command_id')}")
            else:
                st.error("Failed to send command")
    
    def render_timeline(self, data: List[Dict[str, Any]]):
        """
        Render timeline visualization.
        
        Args:
            data: Timeline data points
        """
        import pandas as pd
        
        if data:
            df = pd.DataFrame(data)
            st.line_chart(
                df.set_index(df.columns[0])
            )
        else:
            st.info("No timeline data available")


# Global components instance
dashboard_components = DashboardComponents()
