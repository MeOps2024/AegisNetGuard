import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta

class Dashboard:
    """Interface de tableau de bord pour AEGISLAN"""
    
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
        st.subheader("État du Système")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if not network_data.empty:
                st.metric("Statut Réseau", "Actif", delta="Surveillance")
            else:
                st.metric("Statut Réseau", "Inactif", delta="Aucune donnée")
        
        with col2:
            if model_trained:
                st.metric("Modèle IA", "Opérationnel", delta="Prêt")
            else:
                st.metric("Modèle IA", "Non entraîné", delta="Configuration requise")
        
        with col3:
            if not anomalies_data.empty:
                critical_count = len(anomalies_data[anomalies_data['severity'] == 'Critique'])
                st.metric("Alertes Critiques", critical_count, 
                         delta="Attention requise" if critical_count > 0 else "Système sain")
            else:
                st.metric("Alertes Critiques", "0", delta="Système sain")
        
        with col4:
            if not network_data.empty:
                devices_count = network_data['device_id'].nunique()
                st.metric("Appareils Surveillés", devices_count, delta="En ligne")
            else:
                st.metric("Appareils Surveillés", "0", delta="Hors ligne")
    
    def _render_key_metrics(self, network_data, anomalies_data):
        """Affiche les métriques clés"""
        st.subheader("Métriques Réseau")
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        total_traffic = len(network_data)
        anomalies_count = len(anomalies_data)
        anomaly_rate = (anomalies_count / total_traffic * 100) if total_traffic > 0 else 0
        
        with col1:
            st.metric("Total Connexions", f"{total_traffic:,}", 
                     delta=f"Dernière heure")
        
        with col2:
            st.metric("Anomalies Détectées", anomalies_count, 
                     delta=f"{anomaly_rate:.1f}%" if anomaly_rate > 0 else "Normal")
        
        with col3:
            unique_devices = network_data['device_id'].nunique()
            st.metric("Appareils Actifs", unique_devices)
        
        with col4:
            total_volume = network_data['data_volume_mb'].sum()
            st.metric("Volume Total", f"{total_volume:,.0f} MB")
        
        with col5:
            unique_ports = network_data['port'].nunique()
            st.metric("Ports Utilisés", unique_ports)
    
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
                with st.expander(f"⚠️ Alertes {severity} ({len(severity_alerts)})", 
                               expanded=(severity in ['Critique', 'Élevé'])):
                    
                    for _, alert in severity_alerts.head(5).iterrows():
                        col1, col2, col3 = st.columns([2, 2, 1])
                        
                        with col1:
                            st.write(f"**Appareil:** {alert['device_id']}")
                            st.write(f"**IP:** {alert['ip_address']}")
                        
                        with col2:
                            st.write(f"**Port:** {alert['port']}")
                            st.write(f"**Volume:** {alert['data_volume_mb']} MB")
                        
                        with col3:
                            confidence_pct = alert['anomaly_confidence'] * 100
                            st.metric("Confiance", f"{confidence_pct:.1f}%")
                        
                        # Détails de l'anomalie si disponible
                        if 'anomaly_type' in alert and pd.notna(alert['anomaly_type']):
                            st.caption(f"Type: {alert['anomaly_type']}")
                        
                        st.divider()
    
    def _render_traffic_timeline(self, network_data, anomalies_data):
        """Graphique temporel du trafic"""
        st.subheader("📈 Évolution du Trafic")
        
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
            subplot_titles=['Volume de Données (MB)', 'Connexions et Anomalies'],
            vertical_spacing=0.1
        )
        
        # Volume de données
        fig.add_trace(
            go.Scatter(
                x=hourly_data['hour'],
                y=hourly_data['total_volume'],
                mode='lines+markers',
                name='Volume (MB)',
                line=dict(color='#1f77b4', width=2)
            ),
            row=1, col=1
        )
        
        # Connexions
        fig.add_trace(
            go.Bar(
                x=hourly_data['hour'],
                y=hourly_data['connection_count'],
                name='Connexions',
                marker_color='#2ca02c',
                opacity=0.7
            ),
            row=2, col=1
        )
        
        # Anomalies
        if not anomalies_data.empty:
            fig.add_trace(
                go.Scatter(
                    x=hourly_data['hour'],
                    y=hourly_data['anomaly_count'],
                    mode='markers',
                    name='Anomalies',
                    marker=dict(color='#ff7f0e', size=8, symbol='diamond')
                ),
                row=2, col=1
            )
        
        fig.update_layout(height=400, showlegend=True)
        st.plotly_chart(fig, use_container_width=True)
    
    def _render_device_activity(self, network_data):
        """Graphique d'activité par appareil"""
        st.subheader("💻 Activité par Appareil")
        
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
            title='Top 10 Appareils par Volume de Données',
            labels={'total_volume': 'Volume (MB)', 'device_id': 'Appareil'}
        )
        fig.update_layout(xaxis_tickangle=45)
        st.plotly_chart(fig, use_container_width=True)
    
    def _render_port_analysis(self, network_data, anomalies_data):
        """Analyse des ports utilisés"""
        st.subheader("🔌 Analyse des Ports")
        
        port_usage = network_data['port'].value_counts().head(15)
        
        # Identifier les ports avec anomalies
        anomaly_ports = set()
        if not anomalies_data.empty:
            anomaly_ports = set(anomalies_data['port'].unique())
        
        colors = ['#ff7f0e' if port in anomaly_ports else '#1f77b4' 
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
            title='Top 15 Ports les Plus Utilisés',
            xaxis_title='Port',
            yaxis_title='Nombre de Connexions',
            height=300
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Légende
        if anomaly_ports:
            st.caption("🟠 Ports avec anomalies détectées | 🔵 Ports normaux")
    
    def _render_protocol_distribution(self, network_data):
        """Distribution des protocoles"""
        st.subheader("📡 Distribution des Protocoles")
        
        protocol_dist = network_data['protocol'].value_counts()
        
        fig = px.pie(
            values=protocol_dist.values,
            names=protocol_dist.index,
            title='Répartition du Trafic par Protocole'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _render_detailed_analysis(self, network_data, anomalies_data):
        """Section d'analyse détaillée"""
        st.subheader("🔍 Analyse Détaillée")
        
        tab1, tab2, tab3 = st.tabs(["📋 Données Brutes", "🚨 Anomalies", "📊 Statistiques"])
        
        with tab1:
            st.subheader("Données Réseau Récentes")
            if not network_data.empty:
                # Affichage des données les plus récentes
                recent_data = network_data.sort_values('timestamp', ascending=False).head(100)
                
                # Colonnes à afficher
                display_columns = [
                    'timestamp', 'device_id', 'ip_address', 'device_type',
                    'port', 'protocol', 'data_volume_mb'
                ]
                
                # Ajout de la colonne anomalie si disponible
                if 'is_anomaly' in network_data.columns:
                    display_columns.append('is_anomaly')
                
                st.dataframe(
                    recent_data[display_columns],
                    use_container_width=True,
                    height=400
                )
            else:
                st.info("Aucune donnée disponible")
        
        with tab2:
            st.subheader("Détails des Anomalies")
            if not anomalies_data.empty:
                # Filtres pour les anomalies
                col1, col2 = st.columns(2)
                
                with col1:
                    severity_filter = st.selectbox(
                        "Filtrer par criticité",
                        ['Toutes'] + list(self.severity_colors.keys())
                    )
                
                with col2:
                    device_filter = st.selectbox(
                        "Filtrer par appareil",
                        ['Tous'] + sorted(anomalies_data['device_id'].unique().tolist())
                    )
                
                # Application des filtres
                filtered_anomalies = anomalies_data.copy()
                
                if severity_filter != 'Toutes':
                    filtered_anomalies = filtered_anomalies[
                        filtered_anomalies['severity'] == severity_filter
                    ]
                
                if device_filter != 'Tous':
                    filtered_anomalies = filtered_anomalies[
                        filtered_anomalies['device_id'] == device_filter
                    ]
                
                # Affichage des anomalies filtrées
                display_columns = [
                    'timestamp', 'device_id', 'ip_address', 'port', 'protocol',
                    'data_volume_mb', 'severity', 'anomaly_confidence'
                ]
                
                if 'anomaly_type' in filtered_anomalies.columns:
                    display_columns.append('anomaly_type')
                
                st.dataframe(
                    filtered_anomalies[display_columns],
                    use_container_width=True,
                    height=400
                )
                
                # Téléchargement des anomalies
                csv = filtered_anomalies.to_csv(index=False)
                st.download_button(
                    label="📥 Télécharger les anomalies (CSV)",
                    data=csv,
                    file_name=f"anomalies_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
                
            else:
                st.success("✅ Aucune anomalie détectée")
        
        with tab3:
            st.subheader("Statistiques du Réseau")
            if not network_data.empty:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**Statistiques Générales**")
                    stats = {
                        "Période d'analyse": f"{network_data['timestamp'].min()} - {network_data['timestamp'].max()}",
                        "Total échantillons": len(network_data),
                        "Appareils uniques": network_data['device_id'].nunique(),
                        "Ports uniques": network_data['port'].nunique(),
                        "Volume total (MB)": f"{network_data['data_volume_mb'].sum():,.0f}",
                        "Volume moyen (MB)": f"{network_data['data_volume_mb'].mean():.2f}"
                    }
                    
                    for key, value in stats.items():
                        st.write(f"- **{key}:** {value}")
                
                with col2:
                    st.write("**Types d'Appareils**")
                    device_types = network_data['device_type'].value_counts()
                    for device_type, count in device_types.items():
                        percentage = (count / len(network_data)) * 100
                        st.write(f"- **{device_type}:** {count} ({percentage:.1f}%)")
            else:
                st.info("Aucune donnée pour les statistiques")
