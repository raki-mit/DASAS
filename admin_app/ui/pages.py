"""
DASAS UI Pages Module
=======================
Page implementations for the DASAS Admin Dashboard.

Author: DASAS Team
Version: 1.0.0
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from typing import Any, Dict, List, Optional

# Handle relative imports for both direct and package usage
try:
    from .components import DashboardComponents
    from ..api.devices import device_manager
    from ..api.clusters import cluster_manager
    from ..api.analytics import analytics_manager
except ImportError:
    from ui.components import DashboardComponents
    from api.devices import device_manager
    from api.clusters import cluster_manager
    from api.analytics import analytics_manager


class DevicePage:
    """Page for device management"""
    
    def __init__(self, device_mgr, components: DashboardComponents):
        self.device_manager = device_mgr
        self.components = components
    
    def render(self):
        """Render the devices page"""
        self.components.render_header(
            "📱 Device Management",
            "Monitor and manage Android devices in the DASAS network"
        )
        
        # Tabs for different views
        tab1, tab2, tab3, tab4 = st.tabs([
            "📊 Overview",
            "🔍 Search",
            "➕ Register",
            "📋 All Devices"
        ])
        
        with tab1:
            self._render_overview()
        
        with tab2:
            self._render_search()
        
        with tab3:
            self._render_register()
        
        with tab4:
            self._render_all_devices()
    
    def _render_overview(self):
        """Render device overview"""
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Device statistics
            stats = device_manager.get_device_statistics()
            
            st.subheader("📊 Device Statistics")
            
            m1, m2, m3 = st.columns(3)
            
            with m1:
                st.metric("Total Devices", stats.get("total", 0))
            
            with m2:
                st.metric("Online", stats.get("online", 0))
            
            with m3:
                st.metric("Offline", stats.get("offline", 0))
            
            # Status distribution
            if stats.get("status_distribution"):
                st.subheader("Status Distribution")
                status_data = pd.DataFrame(
                    stats["status_distribution"],
                    index=["Count"]
                ).T
                st.bar_chart(status_data)
        
        with col2:
            # Quick actions
            st.subheader("⚡ Quick Actions")
            
            if st.button("🔄 Refresh Status", use_container_width=True):
                st.rerun()
            
            if st.button("📧 Send Broadcast", use_container_width=True):
                st.info("Broadcast message sent to all devices")
            
            # Alerts panel
            self.components.render_alert_panel()
    
    def _render_search(self):
        """Render device search"""
        st.subheader("🔍 Device Search")
        
        search_query = st.text_input("Search by name or ID")
        
        if search_query:
            results = device_manager.search_devices(search_query)
            
            if results:
                st.write(f"Found {len(results)} devices:")
                
                for device in results:
                    with st.expander(f"{device.get('name', 'Unknown')} ({device.get('status', 'unknown')})"):
                        self.components.render_device_details(device["id"])
            else:
                st.info("No devices found matching your search")
    
    def _render_register(self):
        """Render device registration"""
        st.subheader("➕ Register New Device")
        
        with st.form("register_device"):
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("Device Name")
                device_id = st.text_input("Device ID (auto-generated if empty)")
                device_type = st.selectbox("Device Type", ["android", "tablet", "other"])
            
            with col2:
                ip_address = st.text_input("IP Address")
                mac_address = st.text_input("MAC Address")
                android_version = st.text_input("Android Version")
            
            submit = st.form_submit_button("Register Device")
            
            if submit:
                if not name:
                    st.error("Device name is required")
                else:
                    result = device_manager.register_device(
                        name=name,
                        device_info={
                            "device_id": device_id or None,
                            "device_type": device_type,
                            "ip_address": ip_address,
                            "mac_address": mac_address,
                            "android_version": android_version
                        }
                    )
                    
                    if result.get("success"):
                        st.success(f"Device registered: {result.get('device_id')}")
                    else:
                        st.error("Registration failed")
    
    def _render_all_devices(self):
        """Render all devices table"""
        devices = device_manager.get_all_devices(limit=100)
        
        if devices:
            # Create searchable dataframe
            search = st.text_input("🔍 Filter devices")
            
            if search:
                devices = [
                    d for d in devices
                    if search.lower() in d.get("name", "").lower()
                    or search.lower() in d.get("id", "").lower()
                ]
            
            # Device list
            for device in devices:
                with st.expander(f"{device.get('name', 'Unknown')} - {device.get('id', '')[:8]}..."):
                    self.components.render_device_details(device["id"])
        else:
            st.info("No devices registered")


class ClusterPage:
    """Page for cluster management"""
    
    def __init__(self, cluster_mgr, components: DashboardComponents):
        self.cluster_manager = cluster_mgr
        self.components = components
    
    def render(self):
        """Render the clusters page"""
        self.components.render_header(
            "🔗 Cluster Management",
            "Manage Android device clusters and distributed coordination"
        )
        
        # Tabs
        tab1, tab2, tab3 = st.tabs([
            "📊 Overview",
            "➕ Create",
            "👥 Members"
        ])
        
        with tab1:
            self._render_overview()
        
        with tab2:
            self._render_create()
        
        with tab3:
            self._render_members()
    
    def _render_overview(self):
        """Render cluster overview"""
        stats = cluster_manager.get_cluster_statistics()
        
        m1, m2, m3, m4 = st.columns(4)
        
        with m1:
            st.metric("Total Clusters", stats.get("total_clusters", 0))
        
        with m2:
            st.metric("Active Clusters", stats.get("active_clusters", 0))
        
        with m3:
            st.metric("Total Members", stats.get("total_members", 0))
        
        with m4:
            st.metric("Avg Members/Cluster", f"{stats.get('average_members_per_cluster', 0):.1f}")
        
        # Cluster list
        st.subheader("📋 All Clusters")
        
        clusters = cluster_manager.get_all_clusters()
        
        if clusters:
            for cluster in clusters:
                with st.expander(f"{cluster.get('name', 'Unknown')} ({cluster.get('status', 'unknown')})"):
                    self.components.render_cluster_details(cluster["id"])
        else:
            st.info("No clusters configured")
    
    def _render_create(self):
        """Render cluster creation"""
        st.subheader("➕ Create New Cluster")
        
        with st.form("create_cluster"):
            name = st.text_input("Cluster Name")
            leader_id = st.text_input("Leader Device ID (optional)")
            
            # Advanced configuration
            with st.expander("⚙️ Advanced Configuration"):
                election_timeout = st.number_input(
                    "Election Timeout (ms)",
                    value=5000,
                    step=100
                )
                heartbeat_interval = st.number_input(
                    "Heartbeat Interval (ms)",
                    value=1000,
                    step=100
                )
            
            submit = st.form_submit_button("Create Cluster")
            
            if submit:
                if not name:
                    st.error("Cluster name is required")
                else:
                    result = cluster_manager.create_cluster(
                        name=name,
                        leader_id=leader_id if leader_id else None,
                        configuration={
                            "election_timeout": election_timeout,
                            "heartbeat_interval": heartbeat_interval
                        }
                    )
                    
                    if result.get("success"):
                        st.success(f"Cluster created: {result.get('cluster_id')}")
                    else:
                        st.error("Cluster creation failed")
    
    def _render_members(self):
        """Render member management"""
        st.subheader("👥 Manage Members")
        
        # Get clusters
        clusters = cluster_manager.get_all_clusters()
        
        if not clusters:
            st.info("No clusters available. Create a cluster first.")
            return
        
        # Select cluster
        cluster_options = {c["name"]: c["id"] for c in clusters}
        selected_name = st.selectbox("Select Cluster", list(cluster_options.keys()))
        cluster_id = cluster_options[selected_name]
        
        # Add member
        st.markdown("### ➕ Add Member")
        
        with st.form("add_member"):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                device_id = st.text_input("Device ID")
            
            with col2:
                submit = st.form_submit_button("Add")
            
            if submit:
                result = cluster_manager.add_member(cluster_id, device_id)
                if result.get("success"):
                    st.success("Member added successfully")
                else:
                    st.error(result.get("message", "Failed to add member"))
        
        # Member list
        st.markdown("### 📋 Current Members")
        
        members = cluster_manager.get_members(cluster_id)
        
        if members:
            member_data = []
            for member in members:
                member_data.append({
                    "Name": member.get("name", "Unknown"),
                    "Status": member.get("status", "unknown"),
                    "ID": member.get("id", "")[:8] + "...",
                    "Action": member.get("id", "")
                })
            
            df = pd.DataFrame(member_data)
            
            for i, row in df.iterrows():
                col1, col2, col3 = st.columns([3, 2, 2])
                
                with col1:
                    st.write(f"**{row['Name']}**")
                
                with col2:
                    st.write(row['Status'])
                
                with col3:
                    if st.button("Remove", key=f"remove_{row['Action']}"):
                        cluster_manager.remove_member(cluster_id, row['Action'])
                        st.rerun()
        else:
            st.info("No members in this cluster")


class AnalyticsPage:
    """Page for analytics"""
    
    def __init__(self, analytics_mgr, components: DashboardComponents):
        self.analytics_manager = analytics_mgr
        self.components = components
    
    def render(self):
        """Render the analytics page"""
        self.components.render_header(
            "📈 Analytics",
            "Performance metrics and analytics for the DASAS system"
        )
        
        # Time range selector
        time_range = st.select_slider(
            "Time Range",
            options=["1h", "6h", "12h", "24h", "7d", "30d"],
            value="24h"
        )
        
        # Metrics sections
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("⏱️ Processing Latency")
            
            metrics = analytics_manager.get_performance_metrics()
            
            if metrics:
                df = pd.DataFrame(metrics)
                st.line_chart(df.set_index("timestamp"))
        
        with col2:
            st.subheader("📊 Throughput")
            
            summary = analytics_manager.get_analytics_summary()
            
            st.metric("Processing Rate", f"{summary.get('processing_rate', 0):.0f}/sec")
            st.metric("Data Points Processed", f"{summary.get('data_points_processed', 0):,}")
            st.metric("Storage Used", f"{summary.get('storage_used_gb', 0):.1f} GB")
        
        # Detailed metrics
        st.markdown("---")
        st.subheader("📋 Detailed Metrics")
        
        # Tabular data
        metrics_data = analytics_manager.get_performance_metrics()
        
        if metrics_data:
            df = pd.DataFrame(metrics_data)
            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True
            )
        
        # Export
        st.markdown("---")
        st.subheader("📥 Export Data")
        
        export_format = st.selectbox("Format", ["json", "csv"])
        
        if st.button("Export"):
            data = analytics_manager.export_analytics(format=export_format)
            st.download_button(
                label="Download",
                data=data,
                file_name=f"dasas_analytics.{export_format}",
                mime="text/plain"
            )


class SettingsPage:
    """Page for settings"""
    
    def __init__(self, app):
        self.app = app
    
    def render(self):
        """Render the settings page"""
        self.app.ui_components.render_header(
            "⚙️ Settings",
            "Configure the DASAS Admin Dashboard"
        )
        
        # General settings
        st.subheader("🔧 General Settings")
        
        st.session_state.refresh_interval = st.slider(
            "Auto-refresh Interval (seconds)",
            min_value=0,
            max_value=300,
            value=st.session_state.refresh_interval,
            step=5
        )
        
        st.session_state.dark_mode = st.toggle(
            "Dark Mode",
            value=st.session_state.dark_mode
        )
        
        # Data management
        st.markdown("---")
        st.subheader("💾 Data Management")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🧹 Clear Old Data"):
                try:
                    from ..db.database import db_manager
                except ImportError:
                    from db.database import db_manager
                db_manager.cleanup_old_data(days=30)
                st.success("Old data cleared")
        
        with col2:
            if st.button("💾 Backup Database"):
                try:
                    from ..db.database import db_manager
                except ImportError:
                    from db.database import db_manager
                db_manager.backup_database("./data/backup.db")
                st.success("Database backup created")
        
        # System information
        st.markdown("---")
        st.subheader("ℹ️ System Information")
        
        st.write(f"**DASAS Version:** 1.0.0")
        st.write(f"**Python Version:**")
        import sys
        st.code(f"{sys.version}")
        
        # About
        st.markdown("---")
        st.subheader("📖 About")
        
        st.markdown("""
        **Distributed Android Screen Analytics System (DASAS)** is an innovative 
        framework designed to leverage the underutilized computational power of 
        modern Android devices. By creating a decentralized peer-to-peer (P2P) mesh, 
        DASAS enables real-time screen content analysis without relying on 
        centralized cloud infrastructure.
        
        Built with production-grade architecture including:
        - Ricart-Agrawala mutual exclusion
        - Byzantine fault tolerance
        - Vector clock synchronization
        - TensorFlow Lite inference
        """)
