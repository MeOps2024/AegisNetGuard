import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from data_simulator import NetworkDataSimulator
from anomaly_detector import AnomalyDetector
from real_network_collector import RealNetworkCollector
from dashboard_clean import Dashboard

def main():
    st.set_page_config(
        page_title="AEGISLAN - Enterprise Network Security",
        page_icon=":zap:",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS for professional dark theme
    st.markdown("""
    <style>
    .main {
        background-color: #0E1117;
        color: #FAFAFA;
    }
    .stApp {
        background-color: #0E1117;
    }
    .main-header {
        background: linear-gradient(90deg, #262730 0%, #1E1E2E 50%, #262730 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        border: 1px solid #00D4FF;
    }
    .stSelectbox > div > div {
        background-color: #262730;
        border: 1px solid #00D4FF;
    }
    .metric-container {
        background-color: #262730;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #444;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #262730;
        border: 1px solid #444;
        color: #FAFAFA;
    }
    .stTabs [aria-selected="true"] {
        background-color: #00D4FF !important;
        color: #000000 !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Initialize session state
    if 'simulator' not in st.session_state:
        st.session_state.simulator = NetworkDataSimulator()
    
    if 'collector' not in st.session_state:
        st.session_state.collector = RealNetworkCollector()
    
    if 'detector' not in st.session_state:
        st.session_state.detector = AnomalyDetector()
    
    if 'dashboard' not in st.session_state:
        st.session_state.dashboard = Dashboard()
    
    if 'network_data' not in st.session_state:
        st.session_state.network_data = pd.DataFrame()
    
    if 'anomalies_detected' not in st.session_state:
        st.session_state.anomalies_detected = pd.DataFrame()
    
    if 'model_trained' not in st.session_state:
        st.session_state.model_trained = False
    
    # Header
    st.markdown('<div class="main-header">', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <h1 style='text-align: center; color: #00D4FF; font-size: 3rem; margin: 0;'>
        AEGISLAN
        </h1>
        <p style='text-align: center; color: #FFFFFF; font-size: 1.2rem; margin: 0;'>
        Enterprise Network Security Intelligence Platform
        </p>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Navigation - using radio buttons instead of selectbox
    sections = ["Dashboard", "Network Analysis", "Threat Detection", "System Configuration", "Reports"]
    selected_section = st.radio("Navigate to section", sections, horizontal=True, key="main_navigation")
    
    # Sidebar controls
    with st.sidebar:
        st.markdown("### System Control")
        st.markdown("---")
    
        # Data source selection
        st.markdown("#### Data Source")
        data_source = st.radio("Choose data source", ("Simulated Data", "Real Network Scan"), key="data_source_radio")

        if data_source == "Simulated Data":
            # Data simulation controls
            st.markdown("##### Simulation Settings")
            num_devices = st.slider("Devices", 5, 50, 20, key="devices_slider")
            hours_of_data = st.slider("Hours", 1, 72, 24, key="hours_slider")
            anomaly_rate = st.slider("Anomaly Rate (%)", 1, 20, 5, key="anomaly_slider")
            
            if st.button("Generate Data", type="primary", key="generate_button"):
                with st.spinner("Processing network data..."):
                    st.session_state.network_data = st.session_state.simulator.generate_network_data(
                        num_devices=num_devices,
                        hours=hours_of_data,
                        anomaly_percentage=anomaly_rate
                    )
                    st.session_state.model_trained = False
                st.success("Simulated data generated successfully")
        else: # Real Network Scan
            st.markdown("##### Real Scan Settings")
            scan_ports = st.text_input("Ports to scan", "1-1000", key="scan_ports_input")
            if st.button("Scan Network (Nmap)", type="primary", key="scan_button"):
                with st.spinner("Scanning network with Nmap... This may take a few minutes."):
                    st.session_state.network_data = st.session_state.collector.scan_network_nmap(ports=scan_ports)
                    st.session_state.model_trained = False
                st.success(f"Network scan complete. Found {len(st.session_state.network_data)} devices.")
        
        # Model training controls
        st.markdown("#### AI Model")
        contamination = st.slider("Contamination", 0.01, 0.3, 0.1, 0.01, key="contamination_slider")
    
        if st.button("Train Model", key="train_button") and not st.session_state.network_data.empty:
            # Training process display
            training_placeholder = st.empty()
            progress_bar = st.progress(0)
            
            training_placeholder.info("Starting training...")
            progress_bar.progress(10)
            
            training_placeholder.info("Preparing features...")
            progress_bar.progress(30)
            
            training_placeholder.info("Training Isolation Forest...")
            progress_bar.progress(60)
            
            # Actual training
            st.session_state.detector.train_model(st.session_state.network_data, contamination=contamination)
            progress_bar.progress(80)
            
            training_placeholder.info("Finalizing model...")
            progress_bar.progress(100)
            
            st.session_state.model_trained = True
            training_placeholder.success("Model trained successfully!")
            progress_bar.empty()
        
        # Anomaly detection
        st.markdown("#### Anomaly Detection")
        if st.button("Detect Anomalies", key="detect_button", disabled=(not st.session_state.model_trained or st.session_state.network_data.empty)):
            detection_progress = st.empty()
            detection_progress.info("Analyzing network patterns...")
            
            st.session_state.anomalies_detected = st.session_state.detector.detect_anomalies(st.session_state.network_data)
            
            if not st.session_state.anomalies_detected.empty:
                anomaly_count = len(st.session_state.anomalies_detected)
                detection_progress.warning(f"⚠️ {anomaly_count} anomalies detected!")
            else:
                detection_progress.success("No anomalies detected")
    
    # Main content based on selected section
    if selected_section == "Dashboard":
        render_dashboard_section()
    elif selected_section == "Network Analysis":
        render_network_analysis_section()
    elif selected_section == "Threat Detection":
        render_threat_detection_section()
    elif selected_section == "System Configuration":
        render_system_config_section()
    elif selected_section == "Reports":
        render_reports_section()

def render_dashboard_section():
    """Main dashboard section"""
    st.session_state.dashboard.render_dashboard(
        st.session_state.network_data,
        st.session_state.anomalies_detected,
        st.session_state.model_trained
    )

def render_network_analysis_section():
    """Network analysis section"""
    st.header("Network Analysis")
    
    if st.session_state.network_data.empty:
        st.info("Generate network data to begin analysis.")
        return
    
    # Network overview
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_connections = len(st.session_state.network_data)
        st.metric("Total Connections", f"{total_connections:,}")
    
    with col2:
        unique_devices = st.session_state.network_data['device_id'].nunique()
        st.metric("Active Devices", unique_devices)
    
    with col3:
        protocols = st.session_state.network_data['protocol'].nunique()
        st.metric("Protocols", protocols)
    
    with col4:
        total_volume = st.session_state.network_data['data_volume_mb'].sum()
        st.metric("Total Volume", f"{total_volume:.1f} MB")
    
    # Detailed analysis tabs
    tab1, tab2, tab3 = st.tabs(["Traffic Patterns", "Device Behavior", "Protocol Analysis"])
    
    with tab1:
        st.subheader("Traffic Timeline")
        
        # Hourly traffic analysis
        hourly_data = st.session_state.network_data.groupby(
            st.session_state.network_data['timestamp'].dt.floor('H')
        ).agg({
            'data_volume_mb': 'sum',
            'device_id': 'count'
        }).reset_index()
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=hourly_data['timestamp'],
            y=hourly_data['data_volume_mb'],
            mode='lines+markers',
            name='Data Volume (MB)',
            line=dict(color='#00D4FF')
        ))
        
        fig.update_layout(
            title="Network Traffic Over Time",
            xaxis_title="Time",
            yaxis_title="Data Volume (MB)",
            template="plotly_dark"
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.subheader("Device Activity")
        
        device_stats = st.session_state.network_data.groupby(['device_id', 'device_type']).agg({
            'data_volume_mb': 'sum',
            'port': 'nunique'
        }).reset_index()
        
        fig = px.scatter(
            device_stats,
            x='data_volume_mb',
            y='port',
            color='device_type',
            size='data_volume_mb',
            hover_data=['device_id'],
            title="Device Activity Analysis"
        )
        
        fig.update_layout(template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        st.subheader("Protocol Distribution")
        
        protocol_dist = st.session_state.network_data['protocol'].value_counts()
        
        fig = px.pie(
            values=protocol_dist.values,
            names=protocol_dist.index,
            title="Protocol Usage Distribution"
        )
        
        fig.update_layout(template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)

def render_threat_detection_section():
    """Threat detection section"""
    st.header("Threat Detection")
    
    if not st.session_state.model_trained:
        st.warning("Train the AI model first to enable threat detection.")
        return
    
    if st.session_state.anomalies_detected.empty:
        st.success("No threats detected - Network is secure")
        return
    
    # Threat summary
    col1, col2, col3, col4 = st.columns(4)
    
    severity_counts = st.session_state.anomalies_detected['severity'].value_counts()
    
    with col1:
        critical = severity_counts.get('Critique', 0)
        st.metric("Critical Threats", critical, delta="Immediate action required" if critical > 0 else None)
    
    with col2:
        high = severity_counts.get('Élevé', 0)
        st.metric("High Threats", high)
    
    with col3:
        medium = severity_counts.get('Moyen', 0)
        st.metric("Medium Threats", medium)
    
    with col4:
        low = severity_counts.get('Faible', 0)
        st.metric("Low Threats", low)
    
    # Threat details
    st.subheader("Threat Details")
    
    # Filter by severity
    severity_filter = st.selectbox("Filter by severity", 
                                  ['All'] + list(severity_counts.index),
                                  key="severity_filter")
    
    if severity_filter != 'All':
        filtered_threats = st.session_state.anomalies_detected[
            st.session_state.anomalies_detected['severity'] == severity_filter
        ]
    else:
        filtered_threats = st.session_state.anomalies_detected
    
    # Display threats table
    if not filtered_threats.empty:
        st.dataframe(
            filtered_threats[['timestamp', 'device_id', 'ip_address', 'port', 'severity', 'anomaly_score']],
            use_container_width=True
        )
    else:
        st.info("No threats match the selected filter.")

def render_system_config_section():
    """System configuration section"""
    st.header("System Configuration")
    
    tab1, tab2, tab3 = st.tabs(["Model Settings", "Detection Parameters", "System Status"])
    
    with tab1:
        st.subheader("AI Model Configuration")
        
        if st.session_state.model_trained:
            model_info = st.session_state.detector.get_model_info()
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Model Status:** Trained and Ready")
                st.write(f"**Training Samples:** {model_info.get('n_samples', 'N/A')}")
                st.write(f"**Features:** {model_info.get('n_features', 'N/A')}")
            
            with col2:
                st.write(f"**Contamination:** {model_info.get('contamination', 'N/A')}")
                st.write(f"**Training Time:** {model_info.get('training_time', 'N/A')}")
        else:
            st.warning("AI model not trained yet")
    
    with tab2:
        st.subheader("Detection Parameters")
        
        st.write("**Current Settings:**")
        st.write("- Contamination rate: Adjustable via sidebar")
        st.write("- Detection threshold: Auto-calibrated")
        st.write("- Severity classification: Based on anomaly score")
        
        st.info("Advanced parameters can be adjusted in the sidebar before training.")
    
    with tab3:
        st.subheader("System Health")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Data Status:**")
            if not st.session_state.network_data.empty:
                st.success("✅ Network data loaded")
                st.write(f"Records: {len(st.session_state.network_data):,}")
            else:
                st.error("❌ No network data")
        
        with col2:
            st.write("**AI Model Status:**")
            if st.session_state.model_trained:
                st.success("✅ Model trained and ready")
            else:
                st.warning("⚠️ Model requires training")

def render_reports_section():
    """Reports section"""
    st.header("Security Reports")
    
    if st.session_state.network_data.empty:
        st.info("Generate network data to create reports.")
        return
    
    # Executive summary
    st.subheader("Executive Summary")
    
    total_connections = len(st.session_state.network_data)
    anomalies_count = len(st.session_state.anomalies_detected)
    anomaly_rate = (anomalies_count / total_connections * 100) if total_connections > 0 else 0
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Network Health Score", 
                 f"{max(0, 100 - anomaly_rate * 2):.0f}%",
                 delta="Network security rating")
    
    with col2:
        st.metric("Risk Level", 
                 "LOW" if anomaly_rate < 2 else "MEDIUM" if anomaly_rate < 5 else "HIGH",
                 delta=f"{anomaly_rate:.1f}% anomaly rate")
    
    with col3:
        st.metric("Compliance Status", 
                 "COMPLIANT" if anomaly_rate < 3 else "REVIEW REQUIRED")
    
    # Detailed reports
    tab1, tab2, tab3 = st.tabs(["Network Overview", "Security Analysis", "Recommendations"])
    
    with tab1:
        st.subheader("Network Activity Report")
        
        # Time range analysis
        time_range = st.session_state.network_data['timestamp'].max() - st.session_state.network_data['timestamp'].min()
        
        st.write(f"**Monitoring Period:** {time_range}")
        st.write(f"**Total Devices:** {st.session_state.network_data['device_id'].nunique()}")
        st.write(f"**Total Connections:** {total_connections:,}")
        st.write(f"**Data Volume:** {st.session_state.network_data['data_volume_mb'].sum():.2f} MB")
        
        # Device breakdown
        device_summary = st.session_state.network_data.groupby('device_type').agg({
            'device_id': 'nunique',
            'data_volume_mb': 'sum'
        }).reset_index()
        
        st.subheader("Device Type Summary")
        st.dataframe(device_summary, use_container_width=True)
    
    with tab2:
        st.subheader("Security Analysis Report")
        
        if st.session_state.anomalies_detected.empty:
            st.success("✅ No security threats detected during monitoring period")
            st.write("**Findings:**")
            st.write("- All network traffic patterns appear normal")
            st.write("- No suspicious device behavior identified")
            st.write("- Port usage within expected parameters")
        else:
            st.warning(f"⚠️ {anomalies_count} security anomalies detected")
            
            # Severity breakdown
            severity_summary = st.session_state.anomalies_detected['severity'].value_counts()
            
            st.write("**Threat Breakdown:**")
            for severity, count in severity_summary.items():
                st.write(f"- {severity}: {count} incidents")
            
            # Affected devices
            affected_devices = st.session_state.anomalies_detected['device_id'].nunique()
            st.write(f"**Affected Devices:** {affected_devices}")
    
    with tab3:
        st.subheader("Recommendations")
        
        if anomaly_rate < 1:
            st.success("**System Status: Excellent**")
            st.write("**Recommendations:**")
            st.write("- Continue current monitoring schedule")
            st.write("- Regular model retraining (weekly)")
            st.write("- Maintain security policies")
        elif anomaly_rate < 3:
            st.warning("**System Status: Good**")
            st.write("**Recommendations:**")
            st.write("- Monitor anomalous devices closely")
            st.write("- Review security policies")
            st.write("- Increase monitoring frequency")
        else:
            st.error("**System Status: Requires Attention**")
            st.write("**Immediate Actions Required:**")
            st.write("- Investigate all critical and high severity alerts")
            st.write("- Review network access policies")
            st.write("- Consider network segmentation")
            st.write("- Implement additional security controls")
        
        # Export option
        st.subheader("Export Report")
        if st.button("Generate PDF Report", key="export_button"):
            st.info("PDF export functionality would be implemented here")

if __name__ == "__main__":
    main()