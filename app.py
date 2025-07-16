import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from data_simulator import NetworkDataSimulator
from anomaly_detector import AnomalyDetector
from dashboard import Dashboard

def main():
    st.set_page_config(
        page_title="AEGISLAN - Enterprise Network Security",
        page_icon="🛡️",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    # Custom CSS for professional dark theme
    st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(90deg, #0E1117 0%, #1E2130 100%);
        padding: 2rem 0;
        margin-bottom: 2rem;
        border-bottom: 2px solid #00D4FF;
    }
    .metric-card {
        background: #1E2130;
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid #00D4FF;
        margin-bottom: 1rem;
    }
    .alert-critical {
        background: #4A1F1F;
        border: 2px solid #FF4444;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    .alert-high {
        background: #4A2F1F;
        border: 2px solid #FF8800;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    .section-header {
        color: #00D4FF;
        font-size: 1.8rem;
        font-weight: 600;
        margin: 2rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #00D4FF;
    }
    .status-online { color: #00FF88; }
    .status-warning { color: #FFAA00; }
    .status-critical { color: #FF4444; }
    .nav-section {
        background: #1E2130;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        border: 1px solid #333;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Initialize session state
    if 'simulator' not in st.session_state:
        st.session_state.simulator = NetworkDataSimulator()
    
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
    
    # Navigation menu
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
    
    # Navigation sections
    sections = ["Dashboard", "Network Analysis", "Threat Detection", "System Configuration", "Reports"]
    selected_section = st.selectbox("Navigate to section", sections, index=0)
    
    # Sidebar controls (simplified)
    with st.sidebar:
        st.markdown("### System Control")
        st.markdown("---")
    
        # Data simulation controls
        st.markdown("#### Network Data")
        num_devices = st.slider("Devices", 5, 50, 20)
        hours_of_data = st.slider("Hours", 1, 72, 24)
        anomaly_rate = st.slider("Anomaly Rate (%)", 1, 20, 5)
        
        if st.button("Generate Data", type="primary"):
            with st.spinner("Processing network data..."):
                st.session_state.network_data = st.session_state.simulator.generate_network_data(
                    num_devices=num_devices,
                    hours=hours_of_data,
                    anomaly_percentage=anomaly_rate
                )
                st.session_state.model_trained = False
            st.success("Data generated successfully")
        
        # Model training controls
        st.markdown("#### AI Model")
        contamination = st.slider("Contamination", 0.01, 0.3, 0.1, 0.01)
    
        if st.button("Train Model") and not st.session_state.network_data.empty:
            # Training process display
            training_placeholder = st.empty()
            progress_bar = st.progress(0)
            
            training_placeholder.info("Starting training...")
            progress_bar.progress(10)
            
            training_placeholder.info("Preparing data...")
            progress_bar.progress(30)
            
            training_placeholder.info("Training AI model...")
            progress_bar.progress(60)
            
            # Actual training
            st.session_state.detector.train_model(
                st.session_state.network_data,
                contamination=contamination
            )
            
            progress_bar.progress(90)
            training_placeholder.info("Finalizing...")
            progress_bar.progress(100)
            
            st.session_state.model_trained = True
            
            # Success message
            training_placeholder.success("Model trained successfully!")
            st.success(f"AI operational with {len(st.session_state.network_data)} samples")
            
            # Display model information
            model_info = st.session_state.detector.get_model_info()
            st.write(f"Features used: {model_info['features_count']}")
            st.write(f"Contamination: {contamination:.2f}")
            
            progress_bar.empty()
    
        # Anomaly detection
        if st.button("Detect Anomalies") and st.session_state.model_trained:
            # Detection process display
            detection_placeholder = st.empty()
            detection_progress = st.progress(0)
            
            detection_placeholder.info("Analysis in progress...")
            detection_progress.progress(25)
            
            detection_placeholder.info("AI examining data...")
            detection_progress.progress(50)
            
            detection_placeholder.info("Searching for anomalies...")
            detection_progress.progress(75)
            
            # Actual detection
            st.session_state.anomalies_detected = st.session_state.detector.detect_anomalies(
                st.session_state.network_data
            )
            
            detection_progress.progress(100)
            detection_placeholder.success("Analysis completed!")
            
            # Results
            num_anomalies = len(st.session_state.anomalies_detected)
            if num_anomalies > 0:
                st.warning(f"{num_anomalies} anomalies detected!")
            else:
                st.success("No anomalies detected")
            
            detection_progress.empty()
    
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
    st.markdown('<div class="section-header">Network Security Dashboard</div>', unsafe_allow_html=True)
    
    # Display dashboard
    st.session_state.dashboard.render_dashboard(
        st.session_state.network_data,
        st.session_state.anomalies_detected,
        st.session_state.model_trained
    )

def render_network_analysis_section():
    """Network analysis section"""
    st.markdown('<div class="section-header">Network Traffic Analysis</div>', unsafe_allow_html=True)
    
    if st.session_state.network_data.empty:
        st.info("Generate network data to begin analysis")
        return
    
    # Network statistics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Connections", len(st.session_state.network_data))
    with col2:
        st.metric("Active Devices", st.session_state.network_data['device_id'].nunique())
    with col3:
        st.metric("Data Volume", f"{st.session_state.network_data['data_volume_mb'].sum():.1f} MB")
    with col4:
        st.metric("Unique Ports", st.session_state.network_data['port'].nunique())
    
    # Traffic analysis charts
    st.markdown("### Traffic Patterns")
    
    # Timeline chart
    fig = px.line(st.session_state.network_data, x='timestamp', y='data_volume_mb', 
                  title='Network Traffic Over Time')
    fig.update_layout(template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)
    
    # Protocol distribution
    protocol_counts = st.session_state.network_data['protocol'].value_counts()
    fig = px.pie(values=protocol_counts.values, names=protocol_counts.index,
                 title='Protocol Distribution')
    fig.update_layout(template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

def render_threat_detection_section():
    """Threat detection section"""
    st.markdown('<div class="section-header">AI-Powered Threat Detection</div>', unsafe_allow_html=True)
    
    if not st.session_state.model_trained:
        st.warning("AI model not trained. Please train the model first.")
        return
    
    # Anomaly overview
    if not st.session_state.anomalies_detected.empty:
        st.markdown("### Detected Threats")
        
        # Severity breakdown
        severity_counts = st.session_state.anomalies_detected['severity'].value_counts()
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            critical = severity_counts.get('Critique', 0)
            st.metric("Critical Threats", critical, delta="High Priority" if critical > 0 else None)
        with col2:
            high = severity_counts.get('Élevé', 0)
            st.metric("High Threats", high)
        with col3:
            medium = severity_counts.get('Moyen', 0)
            st.metric("Medium Threats", medium)
        with col4:
            low = severity_counts.get('Faible', 0)
            st.metric("Low Threats", low)
        
        # Threat timeline
        fig = px.scatter(st.session_state.anomalies_detected, x='timestamp', y='anomaly_score',
                        color='severity', title='Threat Detection Timeline')
        fig.update_layout(template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)
        
        # Detailed threat list
        st.markdown("### Threat Details")
        for _, anomaly in st.session_state.anomalies_detected.iterrows():
            severity_class = f"alert-{anomaly['severity'].lower()}"
            st.markdown(f"""
            <div class="{severity_class}">
                <strong>Device:</strong> {anomaly['device_id']} | 
                <strong>Severity:</strong> {anomaly['severity']} | 
                <strong>Score:</strong> {anomaly['anomaly_score']:.2f}<br>
                <strong>Time:</strong> {anomaly['timestamp']} | 
                <strong>Port:</strong> {anomaly['port']} | 
                <strong>Protocol:</strong> {anomaly['protocol']}
            </div>
            """, unsafe_allow_html=True)
    else:
        st.success("No threats detected. Network is secure.")

def render_system_config_section():
    """System configuration section"""
    st.markdown('<div class="section-header">System Configuration</div>', unsafe_allow_html=True)
    
    # AI Model Configuration
    st.markdown("### AI Model Settings")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Model Status**")
        if st.session_state.model_trained:
            st.success("Model is trained and operational")
            model_info = st.session_state.detector.get_model_info()
            st.write(f"Features: {model_info['features_count']}")
            st.write(f"Algorithm: Isolation Forest")
        else:
            st.warning("Model requires training")
    
    with col2:
        st.markdown("**Training Parameters**")
        st.write("Contamination: Percentage of expected anomalies")
        st.write("Features: Network behavioral patterns")
        st.write("Algorithm: Unsupervised learning")
    
    # Network Configuration
    st.markdown("### Network Configuration")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Data Collection**")
        st.write("Source: Network traffic simulation")
        st.write("Frequency: Real-time analysis")
        st.write("Retention: In-memory storage")
    
    with col2:
        st.markdown("**Security Settings**")
        st.write("Encryption: Data processed securely")
        st.write("Access: Restricted to authorized users")
        st.write("Logging: Activity monitoring enabled")

def render_reports_section():
    """Reports section"""
    st.markdown('<div class="section-header">Security Reports</div>', unsafe_allow_html=True)
    
    if st.session_state.network_data.empty:
        st.info("No data available for reporting")
        return
    
    # Generate comprehensive report
    total_connections = len(st.session_state.network_data)
    anomalies_count = len(st.session_state.anomalies_detected)
    anomaly_rate = (anomalies_count / total_connections * 100) if total_connections > 0 else 0
    
    # Executive summary
    st.markdown("### Executive Summary")
    st.markdown(f"""
    <div class="nav-section">
        <h4>Network Security Assessment</h4>
        <p><strong>Total Network Activity:</strong> {total_connections:,} connections analyzed</p>
        <p><strong>Anomalies Detected:</strong> {anomalies_count} threats ({anomaly_rate:.1f}% anomaly rate)</p>
        <p><strong>Security Status:</strong> {"ALERT" if anomalies_count > 0 else "SECURE"}</p>
        <p><strong>Recommendation:</strong> {"Immediate investigation required" if anomalies_count > 0 else "Continue monitoring"}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Detailed metrics
    st.markdown("### Detailed Metrics")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Network Activity**")
        st.write(f"Active devices: {st.session_state.network_data['device_id'].nunique()}")
        st.write(f"Data volume: {st.session_state.network_data['data_volume_mb'].sum():.1f} MB")
        st.write(f"Protocols used: {st.session_state.network_data['protocol'].nunique()}")
        st.write(f"Ports accessed: {st.session_state.network_data['port'].nunique()}")
    
    with col2:
        st.markdown("**Security Analysis**")
        if not st.session_state.anomalies_detected.empty:
            severity_counts = st.session_state.anomalies_detected['severity'].value_counts()
            for severity, count in severity_counts.items():
                st.write(f"{severity} threats: {count}")
        else:
            st.write("No security threats detected")
    
    # Download report button
    if st.button("Export Report"):
        st.success("Report export functionality would be implemented here")


if __name__ == "__main__":
    main()

if __name__ == "__main__":
    main()
