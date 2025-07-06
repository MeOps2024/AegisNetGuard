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
        page_title="AEGISLAN - Détection d'Anomalies Réseau",
        page_icon="🛡️",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
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
    
    # Sidebar controls
    st.sidebar.title("🛡️ AEGISLAN Control Panel")
    st.sidebar.markdown("---")
    
    # Data simulation controls
    st.sidebar.subheader("📊 Simulation des Données")
    
    num_devices = st.sidebar.slider("Nombre d'appareils", 5, 50, 20)
    hours_of_data = st.sidebar.slider("Heures de données", 1, 72, 24)
    anomaly_rate = st.sidebar.slider("Taux d'anomalies (%)", 1, 20, 5)
    
    if st.sidebar.button("🔄 Générer Nouvelles Données", type="primary"):
        with st.spinner("Génération des données réseau..."):
            st.session_state.network_data = st.session_state.simulator.generate_network_data(
                num_devices=num_devices,
                hours=hours_of_data,
                anomaly_percentage=anomaly_rate
            )
            st.session_state.model_trained = False
        st.sidebar.success("Données générées avec succès!")
    
    # Model training controls
    st.sidebar.subheader("🤖 Entraînement du Modèle")
    
    contamination = st.sidebar.slider("Contamination", 0.01, 0.3, 0.1, 0.01)
    
    if st.sidebar.button("🎯 Entraîner le Modèle") and not st.session_state.network_data.empty:
        with st.spinner("Entraînement du modèle d'anomalies..."):
            st.session_state.detector.train_model(
                st.session_state.network_data,
                contamination=contamination
            )
            st.session_state.model_trained = True
        st.sidebar.success("Modèle entraîné avec succès!")
    
    # Anomaly detection
    if st.sidebar.button("🚨 Détecter les Anomalies") and st.session_state.model_trained:
        with st.spinner("Détection des anomalies..."):
            st.session_state.anomalies_detected = st.session_state.detector.detect_anomalies(
                st.session_state.network_data
            )
        st.sidebar.success("Détection terminée!")
    
    # Main dashboard
    st.title("🛡️ AEGISLAN - Système de Détection d'Anomalies Réseau")
    st.markdown("**Prototype sécurisé avec données simulées**")
    
    # Display dashboard
    st.session_state.dashboard.render_dashboard(
        st.session_state.network_data,
        st.session_state.anomalies_detected,
        st.session_state.model_trained
    )

if __name__ == "__main__":
    main()
