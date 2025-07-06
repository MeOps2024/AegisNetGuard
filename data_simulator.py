import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import ipaddress

class NetworkDataSimulator:
    """Simule des données de trafic réseau réalistes pour le prototype AEGISLAN"""
    
    def __init__(self):
        self.device_types = ['workstation', 'server', 'printer', 'phone', 'tablet', 'iot_device']
        self.common_ports = [22, 23, 25, 53, 80, 110, 143, 443, 993, 995, 3389, 5432, 3306]
        self.protocols = ['TCP', 'UDP', 'ICMP']
        
    def _generate_mac_address(self):
        """Génère une adresse MAC aléatoire"""
        return ":".join([f"{random.randint(0, 255):02x}" for _ in range(6)])
    
    def _generate_ip_address(self, subnet="192.168.1"):
        """Génère une adresse IP dans le subnet spécifié"""
        return f"{subnet}.{random.randint(10, 254)}"
    
    def _generate_device_profile(self, device_id):
        """Génère un profil d'appareil avec ses caractéristiques normales"""
        device_type = random.choice(self.device_types)
        
        # Profils de comportement par type d'appareil
        behavior_profiles = {
            'workstation': {
                'activity_hours': (8, 18),  # 8h-18h
                'ports_preference': [80, 443, 22, 3389],
                'connection_frequency': 'high',
                'data_volume_range': (100, 5000)  # MB
            },
            'server': {
                'activity_hours': (0, 24),  # 24/7
                'ports_preference': [22, 80, 443, 3306, 5432],
                'connection_frequency': 'very_high',
                'data_volume_range': (1000, 50000)
            },
            'printer': {
                'activity_hours': (7, 19),
                'ports_preference': [9100, 631, 80],
                'connection_frequency': 'low',
                'data_volume_range': (1, 100)
            },
            'phone': {
                'activity_hours': (7, 22),
                'ports_preference': [80, 443, 5060],
                'connection_frequency': 'medium',
                'data_volume_range': (10, 500)
            },
            'tablet': {
                'activity_hours': (8, 22),
                'ports_preference': [80, 443],
                'connection_frequency': 'medium',
                'data_volume_range': (50, 1000)
            },
            'iot_device': {
                'activity_hours': (0, 24),
                'ports_preference': [80, 443, 1883],
                'connection_frequency': 'low',
                'data_volume_range': (1, 50)
            }
        }
        
        profile = behavior_profiles[device_type].copy()
        profile['device_type'] = device_type
        profile['mac_address'] = self._generate_mac_address()
        profile['ip_address'] = self._generate_ip_address()
        profile['device_id'] = device_id
        
        return profile
    
    def _is_active_hour(self, hour, activity_hours):
        """Détermine si l'appareil est actif à cette heure"""
        start_hour, end_hour = activity_hours
        if start_hour <= end_hour:
            return start_hour <= hour <= end_hour
        else:  # Cas où l'activité traverse minuit
            return hour >= start_hour or hour <= end_hour
    
    def _generate_normal_traffic(self, device_profile, timestamp):
        """Génère du trafic normal basé sur le profil de l'appareil"""
        hour = timestamp.hour
        
        # Probabilité d'activité basée sur les heures d'activité
        if self._is_active_hour(hour, device_profile['activity_hours']):
            base_activity_prob = 0.7
        else:
            base_activity_prob = 0.1
        
        # Ajustement selon la fréquence de connexion
        freq_multiplier = {
            'low': 0.5,
            'medium': 1.0,
            'high': 1.5,
            'very_high': 2.0
        }
        
        activity_prob = base_activity_prob * freq_multiplier.get(device_profile['connection_frequency'], 1.0)
        
        if random.random() < activity_prob:
            # Sélection du port (préférence pour les ports habituels)
            if random.random() < 0.8:  # 80% du temps, utilise les ports préférés
                port = random.choice(device_profile['ports_preference'])
            else:
                port = random.choice(self.common_ports)
            
            # Volume de données
            min_vol, max_vol = device_profile['data_volume_range']
            data_volume = random.randint(min_vol, max_vol)
            
            # Protocole
            protocol = random.choice(self.protocols)
            
            return {
                'timestamp': timestamp,
                'device_id': device_profile['device_id'],
                'mac_address': device_profile['mac_address'],
                'ip_address': device_profile['ip_address'],
                'device_type': device_profile['device_type'],
                'port': port,
                'protocol': protocol,
                'data_volume_mb': data_volume,
                'is_anomaly': False
            }
        
        return None
    
    def _generate_anomalous_traffic(self, device_profile, timestamp):
        """Génère du trafic anormal pour simuler des comportements suspects"""
        anomaly_types = [
            'unusual_port',      # Port inhabituel
            'unusual_time',      # Activité à des heures inhabituelles
            'high_volume',       # Volume de données anormalement élevé
            'unusual_protocol',  # Protocole inhabituel
            'port_scanning'      # Scan de ports
        ]
        
        anomaly_type = random.choice(anomaly_types)
        
        if anomaly_type == 'unusual_port':
            # Utilisation d'un port inhabituel
            port = random.randint(1024, 65535)
            protocol = random.choice(self.protocols)
            min_vol, max_vol = device_profile['data_volume_range']
            data_volume = random.randint(min_vol, max_vol)
            
        elif anomaly_type == 'unusual_time':
            # Activité en dehors des heures normales
            port = random.choice(device_profile['ports_preference'])
            protocol = random.choice(self.protocols)
            min_vol, max_vol = device_profile['data_volume_range']
            data_volume = random.randint(min_vol, max_vol)
            
        elif anomaly_type == 'high_volume':
            # Volume de données anormalement élevé
            port = random.choice(device_profile['ports_preference'])
            protocol = random.choice(self.protocols)
            _, max_vol = device_profile['data_volume_range']
            data_volume = random.randint(max_vol * 5, max_vol * 20)  # 5-20x le volume normal
            
        elif anomaly_type == 'unusual_protocol':
            # Protocole inhabituel pour ce type d'appareil
            port = random.choice(device_profile['ports_preference'])
            unusual_protocols = [p for p in self.protocols if p not in ['TCP', 'UDP']]
            if not unusual_protocols:
                unusual_protocols = ['SCTP', 'GRE']
            protocol = random.choice(unusual_protocols) if unusual_protocols else 'TCP'
            min_vol, max_vol = device_profile['data_volume_range']
            data_volume = random.randint(min_vol, max_vol)
            
        else:  # port_scanning
            # Scan de ports (activité sur de nombreux ports)
            port = random.randint(1, 1024)
            protocol = 'TCP'
            data_volume = random.randint(1, 10)  # Très petit volume pour un scan
        
        return {
            'timestamp': timestamp,
            'device_id': device_profile['device_id'],
            'mac_address': device_profile['mac_address'],
            'ip_address': device_profile['ip_address'],
            'device_type': device_profile['device_type'],
            'port': port,
            'protocol': protocol,
            'data_volume_mb': data_volume,
            'is_anomaly': True,
            'anomaly_type': anomaly_type
        }
    
    def generate_network_data(self, num_devices=20, hours=24, anomaly_percentage=5):
        """
        Génère un dataset complet de trafic réseau simulé
        
        Args:
            num_devices: Nombre d'appareils à simuler
            hours: Nombre d'heures de données à générer
            anomaly_percentage: Pourcentage d'anomalies à inclure
        
        Returns:
            DataFrame avec les données de trafic réseau
        """
        # Génération des profils d'appareils
        device_profiles = []
        for i in range(num_devices):
            device_profiles.append(self._generate_device_profile(f"device_{i:03d}"))
        
        # Génération des données temporelles
        start_time = datetime.now() - timedelta(hours=hours)
        end_time = datetime.now()
        
        network_data = []
        
        # Génération du trafic pour chaque intervalle de 10 minutes
        current_time = start_time
        time_interval = timedelta(minutes=10)
        
        while current_time < end_time:
            for device_profile in device_profiles:
                # Décision: trafic normal ou anormal?
                if random.random() < (anomaly_percentage / 100):
                    # Générer une anomalie
                    traffic_entry = self._generate_anomalous_traffic(device_profile, current_time)
                else:
                    # Générer du trafic normal
                    traffic_entry = self._generate_normal_traffic(device_profile, current_time)
                
                if traffic_entry:
                    network_data.append(traffic_entry)
            
            current_time += time_interval
        
        # Conversion en DataFrame
        df = pd.DataFrame(network_data)
        
        if not df.empty:
            # Ajout de features calculées
            df['hour'] = df['timestamp'].dt.hour
            df['day_of_week'] = df['timestamp'].dt.dayofweek
            df['is_weekend'] = df['day_of_week'].isin([5, 6])
            
            # Calcul de statistiques par appareil
            device_stats = df.groupby('device_id').agg({
                'data_volume_mb': ['mean', 'std', 'max'],
                'port': 'nunique'
            }).round(2)
            
            device_stats.columns = ['avg_data_volume', 'std_data_volume', 'max_data_volume', 'unique_ports']
            device_stats = device_stats.reset_index()
            
            # Merge avec les données principales
            df = df.merge(device_stats, on='device_id', how='left')
            
            # Tri par timestamp
            df = df.sort_values('timestamp').reset_index(drop=True)
        
        return df
