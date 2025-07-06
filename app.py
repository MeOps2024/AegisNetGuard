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
        page_icon="⚡",
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
    st.sidebar.title("AEGISLAN Control Panel")
    st.sidebar.markdown("---")
    
    # Data simulation controls
    st.sidebar.subheader("Simulation des Données")
    
    num_devices = st.sidebar.slider("Nombre d'appareils", 5, 50, 20)
    hours_of_data = st.sidebar.slider("Heures de données", 1, 72, 24)
    anomaly_rate = st.sidebar.slider("Taux d'anomalies (%)", 1, 20, 5)
    
    if st.sidebar.button("Générer Nouvelles Données", type="primary"):
        with st.spinner("Génération des données réseau..."):
            st.session_state.network_data = st.session_state.simulator.generate_network_data(
                num_devices=num_devices,
                hours=hours_of_data,
                anomaly_percentage=anomaly_rate
            )
            st.session_state.model_trained = False
        st.sidebar.success("Données générées avec succès!")
    
    # Model training controls
    st.sidebar.subheader("Entraînement du Modèle")
    
    contamination = st.sidebar.slider("Contamination", 0.01, 0.3, 0.1, 0.01)
    
    if st.sidebar.button("Entraîner le Modèle") and not st.session_state.network_data.empty:
        # Affichage du processus d'entraînement
        training_placeholder = st.sidebar.empty()
        progress_bar = st.sidebar.progress(0)
        
        training_placeholder.info("Démarrage de l'entraînement...")
        progress_bar.progress(10)
        
        training_placeholder.info("Préparation des données...")
        progress_bar.progress(30)
        
        training_placeholder.info("Entraînement de l'IA...")
        progress_bar.progress(60)
        
        # Entraînement réel
        st.session_state.detector.train_model(
            st.session_state.network_data,
            contamination=contamination
        )
        
        progress_bar.progress(90)
        training_placeholder.info("Finalisation...")
        progress_bar.progress(100)
        
        st.session_state.model_trained = True
        
        # Message de succès avec détails
        training_placeholder.success("Modèle entraîné avec succès!")
        st.sidebar.success(f"IA opérationnelle avec {len(st.session_state.network_data)} échantillons")
        
        # Affichage des informations du modèle
        model_info = st.session_state.detector.get_model_info()
        st.sidebar.write(f"Features utilisées: {model_info['features_count']}")
        st.sidebar.write(f"Contamination: {contamination:.2f}")
        
        progress_bar.empty()
    
    # Anomaly detection
    if st.sidebar.button("Détecter les Anomalies") and st.session_state.model_trained:
        # Affichage du processus de détection
        detection_placeholder = st.sidebar.empty()
        detection_progress = st.sidebar.progress(0)
        
        detection_placeholder.info("Analyse en cours...")
        detection_progress.progress(25)
        
        detection_placeholder.info("IA examine les données...")
        detection_progress.progress(50)
        
        detection_placeholder.info("Recherche d'anomalies...")
        detection_progress.progress(75)
        
        # Détection réelle
        st.session_state.anomalies_detected = st.session_state.detector.detect_anomalies(
            st.session_state.network_data
        )
        
        detection_progress.progress(100)
        detection_placeholder.success("Analyse terminée!")
        
        # Résultats
        num_anomalies = len(st.session_state.anomalies_detected)
        if num_anomalies > 0:
            st.sidebar.warning(f"{num_anomalies} anomalies détectées!")
        else:
            st.sidebar.success("Aucune anomalie détectée")
        
        detection_progress.empty()
    
    # Main dashboard
    st.title("AEGISLAN - Système de Détection d'Anomalies Réseau")
    st.markdown("**Prototype sécurisé avec données simulées**")
    
    # Display dashboard
    st.session_state.dashboard.render_dashboard(
        st.session_state.network_data,
        st.session_state.anomalies_detected,
        st.session_state.model_trained
    )

if __name__ == "__main__":
    main()
