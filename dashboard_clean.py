import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta

class Dashboard:
    """Interface de tableau de bord pour AEGISLAN - Version professionnelle"""
    
    def __init__(self):
        self.severity_colors = {
            'Critique': '#FF4444',
            'Élevé': '#FF8800',
            'Moyen': '#FFBB00',
            'Faible': '#44AA44'
        }
    
    def render_dashboard(self, network_data, anomalies_data, model_trained):
        """
        Affiche le tableau de bord principal
        
        Args:
            network_data: DataFrame avec toutes les données réseau
            anomalies_data: DataFrame avec les anomalies détectées
            model_trained: Boolean indiquant si le modèle est entraîné
        """
        # Section d'état du système
        self._render_system_status(network_data, anomalies_data, model_trained)
        
        if network_data.empty:
            st.info("Generate network data to begin analysis.")
            return
        
        # Métriques principales
        self._render_key_metrics(network_data, anomalies_data)
        
        # Alertes en temps réel
        if not anomalies_data.empty:
            self._render_alerts(anomalies_data)
        
        # Graphiques d'analyse
        col1, col2 = st.columns(2)
        
        with col1:
            self._render_traffic_timeline(network_data, anomalies_data)
            self._render_device_activity(network_data)
        
        with col2:
            self._render_port_analysis(network_data, anomalies_data)
            self._render_protocol_distribution(network_data)
        
        # Section d'analyse détaillée
        self._render_detailed_analysis(network_data, anomalies_data)
    
    def _render_system_status(self, network_data, anomalies_data, model_trained):
        """Affiche l'état du système"""
        st.subheader("System Status")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if not network_data.empty:
                st.metric("Network Status", "Active", delta="Monitoring")
            else:
                st.metric("Network Status", "Inactive", delta="No data")
        
        with col2:
            if model_trained:
                st.metric("AI Model", "Operational", delta="Ready")
            else:
                st.metric("AI Model", "Not trained", delta="Configuration required")
        
        with col3:
            if not anomalies_data.empty:
                critical_count = len(anomalies_data[anomalies_data['severity'] == 'Critique'])
                st.metric("Critical Alerts", critical_count, 
                         delta="Attention required" if critical_count > 0 else "System healthy")
            else:
                st.metric("Critical Alerts", "0", delta="System healthy")
        
        with col4:
            if not network_data.empty:
                devices_count = network_data['device_id'].nunique()
                st.metric("Monitored Devices", devices_count, delta="Online")
            else:
                st.metric("Monitored Devices", "0", delta="Offline")
    
    def _render_key_metrics(self, network_data, anomalies_data):
        """Affiche les métriques clés"""
        st.subheader("Network Metrics")
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        total_traffic = len(network_data)
        anomalies_count = len(anomalies_data)
        anomaly_rate = (anomalies_count / total_traffic * 100) if total_traffic > 0 else 0
        
        with col1:
            st.metric("Total Connections", f"{total_traffic:,}", 
                     delta="Last hour")
        
        with col2:
            st.metric("Detected Anomalies", anomalies_count, 
                     delta=f"{anomaly_rate:.1f}%" if anomaly_rate > 0 else "Normal")
        
        with col3:
            unique_devices = network_data['device_id'].nunique()
            st.metric("Active Devices", unique_devices)
        
        with col4:
            total_volume = network_data['data_volume_mb'].sum()
            st.metric("Total Volume", f"{total_volume:,.0f} MB")
        
        with col5:
            unique_ports = network_data['port'].nunique()
            st.metric("Ports Used", unique_ports)
    
    def _render_alerts(self, anomalies_data):
        """Affiche les alertes en temps réel"""
        st.subheader("Real-Time Security Alerts")
        
        if anomalies_data.empty:
            st.success("No anomalies detected - Network is secure")
            return
        
        # Alertes par niveau de criticité
        for severity in ['Critique', 'Élevé', 'Moyen', 'Faible']:
            severity_alerts = anomalies_data[anomalies_data['severity'] == severity]
            
            if not severity_alerts.empty:
                with st.expander(f"{severity} Alerts ({len(severity_alerts)})", 
                               expanded=(severity in ['Critique', 'Élevé'])):
                    
                    for idx, alert in severity_alerts.head(5).iterrows():
                        col1, col2, col3 = st.columns([2, 2, 1])
                        
                        with col1:
                            st.write(f"**Device:** {alert['device_id']}")
                            st.write(f"**IP:** {alert['ip_address']}")
                        
                        with col2:
                            st.write(f"**Port:** {alert['port']}")
                            st.write(f"**Volume:** {alert['data_volume_mb']} MB")
                        
                        with col3:
                            if 'anomaly_confidence' in alert:
                                confidence_pct = alert['anomaly_confidence'] * 100
                                st.metric("Confidence", f"{confidence_pct:.1f}%")
                            else:
                                st.metric("Score", f"{alert.get('anomaly_score', 0):.2f}")
                        
                        # Détails de l'anomalie si disponible
                        if 'anomaly_type' in alert and pd.notna(alert['anomaly_type']):
                            st.caption(f"Type: {alert['anomaly_type']}")
                        
                        st.divider()
    
    def _render_traffic_timeline(self, network_data, anomalies_data):
        """Graphique temporel du trafic"""
        st.subheader("Network Traffic Timeline")
        
        # Agrégation par heure
        hourly_data = network_data.groupby(network_data['timestamp'].dt.floor('H')).agg({
            'data_volume_mb': 'sum',
            'device_id': 'count'
        }).reset_index()
        hourly_data.columns = ['hour', 'total_volume', 'connection_count']
        
        # Anomalies par heure
        if not anomalies_data.empty:
            hourly_anomalies = anomalies_data.groupby(
                anomalies_data['timestamp'].dt.floor('H')
            ).size().reset_index()
            hourly_anomalies.columns = ['hour', 'anomaly_count']
            hourly_data = hourly_data.merge(hourly_anomalies, on='hour', how='left')
            hourly_data['anomaly_count'] = hourly_data['anomaly_count'].fillna(0)
        else:
            hourly_data['anomaly_count'] = 0
        
        # Graphique combiné
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=('Data Volume (MB)', 'Connections Count'),
            vertical_spacing=0.1
        )
        
        # Volume de données
        fig.add_trace(
            go.Scatter(
                x=hourly_data['hour'],
                y=hourly_data['total_volume'],
                mode='lines+markers',
                name='Volume (MB)',
                line=dict(color='#00D4FF', width=2)
            ),
            row=1, col=1
        )
        
        # Nombre de connexions
        fig.add_trace(
            go.Bar(
                x=hourly_data['hour'],
                y=hourly_data['connection_count'],
                name='Connections',
                marker_color='#44AA44'
            ),
            row=2, col=1
        )
        
        # Anomalies si disponibles
        if 'anomaly_count' in hourly_data.columns:
            fig.add_trace(
                go.Scatter(
                    x=hourly_data['hour'],
                    y=hourly_data['anomaly_count'],
                    mode='markers',
                    name='Anomalies',
                    marker=dict(color='#FF4444', size=8, symbol='x')
                ),
                row=1, col=1
            )
        
        fig.update_layout(
            height=400,
            showlegend=True,
            title_text="Network Traffic Timeline Analysis",
            template="plotly_dark"
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _render_device_activity(self, network_data):
        """Graphique d'activité par appareil"""
        st.subheader("Device Activity Analysis")
        
        device_activity = network_data.groupby(['device_id', 'device_type']).agg({
            'data_volume_mb': 'sum',
            'port': 'nunique'
        }).reset_index()
        device_activity.columns = ['device_id', 'device_type', 'total_volume', 'unique_ports']
        
        # Top 10 des appareils les plus actifs
        top_devices = device_activity.nlargest(10, 'total_volume')
        
        fig = px.bar(
            top_devices,
            x='device_id',
            y='total_volume',
            color='device_type',
            title='Top 10 Most Active Devices',
            labels={'total_volume': 'Total Volume (MB)', 'device_id': 'Device'},
            hover_data=['unique_ports']
        )
        
        fig.update_layout(height=350, template="plotly_dark", xaxis_tickangle=45)
        st.plotly_chart(fig, use_container_width=True)
    
    def _render_port_analysis(self, network_data, anomalies_data):
        """Analyse des ports utilisés"""
        st.subheader("Port Usage Analysis")
        
        port_usage = network_data['port'].value_counts().head(15)
        
        # Identifier les ports avec anomalies
        anomaly_ports = set()
        if not anomalies_data.empty:
            anomaly_ports = set(anomalies_data['port'].unique())
        
        colors = ['#FF4444' if port in anomaly_ports else '#00D4FF' 
                 for port in port_usage.index]
        
        fig = go.Figure(data=[
            go.Bar(
                x=port_usage.index.astype(str),
                y=port_usage.values,
                marker_color=colors,
                text=port_usage.values,
                textposition='auto'
            )
        ])
        
        fig.update_layout(
            title='Top 15 Most Used Ports',
            xaxis_title='Port',
            yaxis_title='Connection Count',
            height=300,
            template="plotly_dark"
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Légende
        if anomaly_ports:
            st.caption("Red: Ports with detected anomalies | Blue: Normal ports")
    
    def _render_protocol_distribution(self, network_data):
        """Distribution des protocoles"""
        st.subheader("Protocol Distribution")
        
        protocol_dist = network_data['protocol'].value_counts()
        
        fig = px.pie(
            values=protocol_dist.values,
            names=protocol_dist.index,
            title='Traffic Distribution by Protocol'
        )
        
        fig.update_layout(height=350, template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)
    
    def _render_detailed_analysis(self, network_data, anomalies_data):
        """Section d'analyse détaillée"""
        st.subheader("Detailed Analysis")
        
        tab1, tab2, tab3 = st.tabs(["Network Summary", "Anomaly Details", "System Health"])
        
        with tab1:
            st.markdown("### Network Overview")
            
            # Statistiques générales
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Traffic Statistics**")
                st.write(f"Total connections: {len(network_data):,}")
                st.write(f"Data volume: {network_data['data_volume_mb'].sum():.2f} MB")
                st.write(f"Average per device: {network_data['data_volume_mb'].mean():.2f} MB")
                st.write(f"Peak volume: {network_data['data_volume_mb'].max():.2f} MB")
            
            with col2:
                st.markdown("**Device Statistics**")
                st.write(f"Total devices: {network_data['device_id'].nunique()}")
                st.write(f"Device types: {network_data['device_type'].nunique()}")
                st.write(f"Protocols used: {network_data['protocol'].nunique()}")
                st.write(f"Unique ports: {network_data['port'].nunique()}")
        
        with tab2:
            if not anomalies_data.empty:
                st.markdown("### Anomaly Analysis")
                
                # Résumé des anomalies
                severity_counts = anomalies_data['severity'].value_counts()
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**Severity Breakdown**")
                    for severity, count in severity_counts.items():
                        st.write(f"{severity}: {count} alerts")
                
                with col2:
                    st.markdown("**Affected Devices**")
                    affected_devices = anomalies_data['device_id'].nunique()
                    st.write(f"Devices with anomalies: {affected_devices}")
                    
                    if affected_devices > 0:
                        top_affected = anomalies_data['device_id'].value_counts().head(5)
                        st.write("Most affected devices:")
                        for device, count in top_affected.items():
                            st.write(f"- {device}: {count} anomalies")
                
                # Table des anomalies récentes
                st.markdown("**Recent Anomalies**")
                recent_anomalies = anomalies_data.head(10)[['timestamp', 'device_id', 'severity', 'anomaly_score', 'port']]
                st.dataframe(recent_anomalies, use_container_width=True)
            else:
                st.success("No anomalies detected in current dataset")
        
        with tab3:
            st.markdown("### System Health")
            
            # Indicateurs de santé
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Performance Metrics**")
                anomaly_rate = (len(anomalies_data) / len(network_data) * 100) if len(network_data) > 0 else 0
                st.write(f"Anomaly rate: {anomaly_rate:.2f}%")
                
                if anomaly_rate < 1:
                    st.success("Low anomaly rate - System healthy")
                elif anomaly_rate < 5:
                    st.warning("Moderate anomaly rate - Monitor closely")
                else:
                    st.error("High anomaly rate - Investigation required")
            
            with col2:
                st.markdown("**Recommendations**")
                
                if anomalies_data.empty:
                    st.write("- Continue normal monitoring")
                    st.write("- Regular model retraining recommended")
                else:
                    st.write("- Review anomalous devices")
                    st.write("- Update security policies if needed")
                    st.write("- Consider network segmentation")
                    
                    if len(anomalies_data) > 10:
                        st.write("- Immediate security review required")