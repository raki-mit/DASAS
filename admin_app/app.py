# Distributed Android Screen Analytics System (DASAS)
# Production-Grade Monitoring Dashboard

"""
DASAS Admin Web Application
============================
A Streamlit-based admin dashboard for monitoring and managing
the Distributed Android Screen Analytics System infrastructure.

Author: DASAS Team
Version: 1.0.0
"""

import streamlit as st
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

# Import core modules
from core.config import settings
from core.logging_config import logger
from core.metrics import MetricsCollector

# Handle relative imports for both direct and package usage
try:
    from db.database import DatabaseManager
    from api.devices import DeviceManager
    from api.clusters import ClusterManager
    from api.analytics import AnalyticsManager
    from ui.components import DashboardComponents
    from ui.pages import DevicePage, ClusterPage, AnalyticsPage, SettingsPage
except ImportError:
    from .db.database import DatabaseManager
    from .api.devices import DeviceManager
    from .api.clusters import ClusterManager
    from .api.analytics import AnalyticsManager
    from .ui.components import DashboardComponents
    from .ui.pages import DevicePage, ClusterPage, AnalyticsPage, SettingsPage

# Page configurations
st.set_page_config(
    page_title="DASAS Admin Dashboard",
    page_icon="📱",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "About": "### DASAS v1.0.0\nDistributed Android Screen Analytics System",
        "Report a bug": None,
        "Get help": None,
    },
)


class DASASAdminApp:
    """
    Main Streamlit Application Class
    
    Provides comprehensive monitoring and management capabilities
    for the distributed Android device network.
    """
    
    def __init__(self):
        self.logger = logger
        self.metrics = MetricsCollector()
        self.db_manager = DatabaseManager()
        self.device_manager = DeviceManager()
        self.cluster_manager = ClusterManager()
        self.analytics_manager = AnalyticsManager()
        self.ui_components = DashboardComponents()
        
        # Initialize session state
        self._init_session_state()
    
    def _init_session_state(self):
        """Initialize session state variables"""
        if "page" not in st.session_state:
            st.session_state.page = "dashboard"
        if "selected_device" not in st.session_state:
            st.session_state.selected_device = None
        if "selected_cluster" not in st.session_state:
            st.session_state.selected_cluster = None
        if "refresh_interval" not in st.session_state:
            st.session_state.refresh_interval = 30
        if "dark_mode" not in st.session_state:
            st.session_state.dark_mode = True
    
    def apply_theme(self):
        """Apply custom theme based on session state"""
        if st.session_state.dark_mode:
            st.markdown("""
                <style>
                .stApp {
                    background-color: #0e1117;
                    color: #fafafa;
                }
                .stMetric {
                    background-color: #262730;
                    padding: 15px;
                    border-radius: 10px;
                }
                .stDataFrame {
                    background-color: #262730;
                }
                </style>
            """, unsafe_allow_html=True)
    
    def render_sidebar(self):
        """Render sidebar navigation"""
        with st.sidebar:
            st.title("📱 DASAS Admin")
            st.markdown("---")
            
            # Navigation menu
            menu_options = [
                "Dashboard",
                "Devices",
                "Clusters",
                "Analytics",
                "Fault Tolerance",
                "Settings"
            ]
            
            selected_page = st.radio(
                "Navigation",
                menu_options,
                index=menu_options.index(
                    st.session_state.page.replace("_", " ").title()
                ) if st.session_state.page != "dashboard" else 0
            )
            
            st.session_state.page = selected_page.lower().replace(" ", "_")
            
            st.markdown("---")
            
            # Refresh settings
            st.subheader("⚙️ Settings")
            st.session_state.refresh_interval = st.slider(
                "Auto-refresh (seconds)",
                min_value=5,
                max_value=300,
                value=st.session_state.refresh_interval,
                step=5
            )
            
            st.session_state.dark_mode = st.toggle(
                "Dark Mode",
                value=st.session_state.dark_mode
            )
            
            st.markdown("---")
            
            # System status
            st.subheader("📊 System Status")
            self._render_system_status()
            
            # Version info
            st.markdown("---")
            st.caption(f"DASAS v1.0.0 | Python {sys.version.split()[0]}")
    
    def _render_system_status(self):
        """Render system status indicators"""
        try:
            # Get system metrics
            metrics = self.metrics.get_system_metrics()
            
            # Status indicators
            status_color = "🟢" if metrics["status"] == "healthy" else "🟡" if metrics["status"] == "degraded" else "🔴"
            st.markdown(f"**Status:** {status_color} {metrics['status'].title()}")
            
            # Connection count
            active_devices = self.device_manager.get_active_count()
            st.metric(
                "Active Devices",
                f"{active_devices}/{metrics.get('total_devices', 0)}",
                delta=f"{active_devices - metrics.get('prev_active', 0)}"
            )
            
            # Cluster status
            cluster_count = self.cluster_manager.get_cluster_count()
            st.metric("Active Clusters", cluster_count)
            
        except Exception as e:
            self.logger.error(f"Error rendering system status: {e}")
            st.error("Unable to fetch system status")
    
    def render_dashboard(self):
        """Render main dashboard page"""
        self.ui_components.render_header("📊 Dashboard", "Overview of the DASAS Infrastructure")
        
        # Key metrics row
        self.ui_components.render_metrics_row()
        
        # Main content columns
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Device distribution map
            self.ui_components.render_device_distribution()
            
            # Active devices table
            self.ui_components.render_active_devices_table()
        
        with col2:
            # Cluster status
            self.ui_components.render_cluster_status()
            
            # System health chart
            self.ui_components.render_health_chart()
        
        # Analytics section
        with st.expander("📈 Quick Analytics", expanded=True):
            self.analytics_manager.render_quick_analytics()
    
    def render_devices_page(self):
        """Render device management page"""
        device_page = DevicePage(self.device_manager, self.ui_components)
        device_page.render()
    
    def render_clusters_page(self):
        """Render cluster management page"""
        cluster_page = ClusterPage(self.cluster_manager, self.ui_components)
        cluster_page.render()
    
    def render_analytics_page(self):
        """Render analytics page"""
        analytics_page = AnalyticsPage(self.analytics_manager, self.ui_components)
        analytics_page.render()
    
    def render_fault_tolerance_page(self):
        """Render fault tolerance page"""
        self.ui_components.render_header("🛡️ Fault Tolerance", "Monitor Byzantine Agreement and System Resilience")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🔐 Byzantine Agreement Status")
            self._render_byzantine_status()
        
        with col2:
            st.subheader("⚠️ Node Health")
            self._render_node_health()
        
        st.subheader("📋 Checkpoint History")
        self._render_checkpoint_history()
    
    def _render_byzantine_status(self):
        """Render Byzantine agreement status"""
        try:
            status = self.analytics_manager.get_byzantine_status()
            
            if status["active"]:
                st.success("✅ Byzantine Agreement Active")
            else:
                st.warning("⚠️ Byzantine Agreement Degraded")
            
            st.progress(status["agreement_rate"])
            st.caption(f"Agreement Rate: {status['agreement_rate']:.1%}")
            
            # Fault tolerance metrics
            st.metric("Faulty Nodes Detected", status["faulty_nodes"])
            st.metric("Successful Reconstructions", status["reconstructions"])
            
        except Exception as e:
            st.error(f"Unable to fetch Byzantine status: {e}")
    
    def _render_node_health(self):
        """Render node health status"""
        try:
            nodes = self.device_manager.get_all_nodes()
            
            for node in nodes:
                status = "healthy" if node["health_score"] > 80 else "degraded" if node["health_score"] > 50 else "critical"
                color = "green" if status == "healthy" else "orange" if status == "degraded" else "red"
                
                st.markdown(f"""
                <div style="display: flex; justify-content: space-between; padding: 8px;">
                    <span>{node['name']}</span>
                    <span style="color: {color}">● {status.title()}</span>
                </div>
                """, unsafe_allow_html=True)
                
                st.progress(node["health_score"] / 100)
                
        except Exception as e:
            st.error(f"Unable to fetch node health: {e}")
    
    def _render_checkpoint_history(self):
        """Render checkpoint history table"""
        try:
            checkpoints = self.analytics_manager.get_checkpoint_history()
            
            if checkpoints:
                # Create dataframe
                import pandas as pd
                df = pd.DataFrame(checkpoints)
                
                # Display with formatting
                st.dataframe(
                    df,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "timestamp": st.column_config.DatetimeColumn("Time", format="D MMM YYYY, h:mm a"),
                        "status": st.column_config.TextColumn("Status", width="medium"),
                        "nodes_checked": st.column_config.ProgressColumn("Nodes Checked", min_value=0, max_value=100),
                    }
                )
            else:
                st.info("No checkpoint data available")
                
        except Exception as e:
            st.error(f"Unable to fetch checkpoint history: {e}")
    
    def render_settings_page(self):
        """Render settings page"""
        settings_page = SettingsPage(self)
        settings_page.render()
    
    def run(self):
        """Main application loop"""
        try:
            # Apply theme
            self.apply_theme()
            
            # Render sidebar
            self.render_sidebar()
            
            # Route to appropriate page
            page_handlers = {
                "dashboard": self.render_dashboard,
                "devices": self.render_devices_page,
                "clusters": self.render_clusters_page,
                "analytics": self.render_analytics_page,
                "fault_tolerance": self.render_fault_tolerance_page,
                "settings": self.render_settings_page,
            }
            
            handler = page_handlers.get(st.session_state.page, self.render_dashboard)
            handler()
            
            # Auto-refresh
            if st.session_state.refresh_interval > 0:
                st.rerun()
                
        except Exception as e:
            self.logger.critical(f"Application error: {e}")
            st.error(f"Critical error: {e}")
            st.stop()


def main():
    """Entry point for the application"""
    logger.info("Starting DASAS Admin Dashboard...")
    
    app = DASASAdminApp()
    app.run()


if __name__ == "__main__":
    main()
