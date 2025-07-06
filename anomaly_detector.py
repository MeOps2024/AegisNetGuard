import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import classification_report, confusion_matrix
import warnings
warnings.filterwarnings('ignore')

class AnomalyDetector:
    """Détecteur d'anomalies réseau utilisant Isolation Forest"""
    
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.feature_columns = []
        self.is_trained = False
        
    def _prepare_features(self, df, fit_encoders=False):
        """
        Prépare les features pour l'entraînement ou la prédiction
        
        Args:
            df: DataFrame avec les données réseau
            fit_encoders: Si True, ajuste les encodeurs (mode entraînement)
        
        Returns:
            numpy array avec les features préparées
        """
        if df.empty:
            return np.array([])
        
        # Copie des données pour éviter les modifications
        data = df.copy()
        
        # Features temporelles
        data['hour_sin'] = np.sin(2 * np.pi * data['hour'] / 24)
        data['hour_cos'] = np.cos(2 * np.pi * data['hour'] / 24)
        data['day_sin'] = np.sin(2 * np.pi * data['day_of_week'] / 7)
        data['day_cos'] = np.cos(2 * np.pi * data['day_of_week'] / 7)
        
        # Features numériques directes
        numeric_features = [
            'port', 'data_volume_mb', 'hour_sin', 'hour_cos', 
            'day_sin', 'day_cos', 'avg_data_volume', 'std_data_volume',
            'max_data_volume', 'unique_ports'
        ]
        
        # Features catégorielles à encoder
        categorical_features = ['device_type', 'protocol']
        
        # Initialisation du DataFrame de features
        features_df = pd.DataFrame()
        
        # Ajout des features numériques
        for feature in numeric_features:
            if feature in data.columns:
                features_df[feature] = data[feature].fillna(0)
        
        # Encodage des features catégorielles
        for feature in categorical_features:
            if feature in data.columns:
                if fit_encoders:
                    # Mode entraînement: créer et ajuster l'encodeur
                    self.label_encoders[feature] = LabelEncoder()
                    features_df[f'{feature}_encoded'] = self.label_encoders[feature].fit_transform(
                        data[feature].fillna('unknown')
                    )
                else:
                    # Mode prédiction: utiliser l'encodeur existant
                    if feature in self.label_encoders:
                        # Gérer les nouvelles valeurs non vues pendant l'entraînement
                        def safe_transform(value):
                            try:
                                return self.label_encoders[feature].transform([value])[0]
                            except ValueError:
                                # Valeur non vue pendant l'entraînement
                                return -1
                        
                        features_df[f'{feature}_encoded'] = data[feature].fillna('unknown').apply(safe_transform)
                    else:
                        # Pas d'encodeur disponible
                        features_df[f'{feature}_encoded'] = 0
        
        # Features dérivées
        if 'data_volume_mb' in data.columns and 'avg_data_volume' in data.columns:
            # Écart par rapport à la moyenne de l'appareil
            features_df['volume_deviation'] = (
                data['data_volume_mb'] - data['avg_data_volume']
            ).fillna(0)
            
            # Ratio par rapport à la moyenne
            features_df['volume_ratio'] = (
                data['data_volume_mb'] / (data['avg_data_volume'] + 1)
            ).fillna(1)
        
        # Features de port
        if 'port' in data.columns:
            # Indication si le port est dans les ports communs
            common_ports = [22, 23, 25, 53, 80, 110, 143, 443, 993, 995, 3389, 5432, 3306]
            features_df['is_common_port'] = data['port'].isin(common_ports).astype(int)
            
            # Port dans les plages privilégiées/système
            features_df['is_system_port'] = (data['port'] <= 1024).astype(int)
            features_df['is_ephemeral_port'] = (data['port'] >= 32768).astype(int)
        
        # Conversion en numpy array
        self.feature_columns = features_df.columns.tolist()
        return features_df.values
    
    def train_model(self, df, contamination=0.1):
        """
        Entraîne le modèle Isolation Forest
        
        Args:
            df: DataFrame avec les données d'entraînement
            contamination: Proportion estimée d'anomalies dans les données
        """
        if df.empty:
            raise ValueError("Le DataFrame d'entraînement est vide")
        
        print(f"Entraînement du modèle avec {len(df)} échantillons...")
        
        # Préparation des features
        X = self._prepare_features(df, fit_encoders=True)
        
        if X.size == 0:
            raise ValueError("Aucune feature n'a pu être extraite des données")
        
        # Normalisation des données
        X_scaled = self.scaler.fit_transform(X)
        
        # Configuration et entraînement du modèle Isolation Forest
        self.model = IsolationForest(
            contamination=contamination,
            random_state=42,
            n_estimators=100,
            max_samples='auto',
            bootstrap=False
        )
        
        # Entraînement
        self.model.fit(X_scaled)
        self.is_trained = True
        
        print("✅ Modèle entraîné avec succès!")
        
        # Évaluation sur les données d'entraînement si les labels sont disponibles
        if 'is_anomaly' in df.columns:
            predictions = self.model.predict(X_scaled)
            predictions_binary = (predictions == -1).astype(int)
            true_labels = df['is_anomaly'].astype(int)
            
            print("\n📊 Évaluation sur les données d'entraînement:")
            print(f"Anomalies détectées: {predictions_binary.sum()}")
            print(f"Vraies anomalies: {true_labels.sum()}")
            
            if true_labels.sum() > 0:
                print("\nRapport de classification:")
                print(classification_report(true_labels, predictions_binary, 
                                          target_names=['Normal', 'Anomalie']))
    
    def detect_anomalies(self, df):
        """
        Détecte les anomalies dans les nouvelles données
        
        Args:
            df: DataFrame avec les données à analyser
        
        Returns:
            DataFrame avec les anomalies détectées et leurs scores
        """
        if not self.is_trained:
            raise ValueError("Le modèle n'a pas été entraîné. Appelez train_model() d'abord.")
        
        if df.empty:
            return pd.DataFrame()
        
        print(f"Détection d'anomalies sur {len(df)} échantillons...")
        
        # Préparation des features
        X = self._prepare_features(df, fit_encoders=False)
        
        if X.size == 0:
            return pd.DataFrame()
        
        # Normalisation
        X_scaled = self.scaler.transform(X)
        
        # Prédiction
        predictions = self.model.predict(X_scaled)
        anomaly_scores = self.model.score_samples(X_scaled)
        
        # Création du DataFrame de résultats
        results = df.copy()
        results['predicted_anomaly'] = (predictions == -1).astype(int)
        results['anomaly_score'] = anomaly_scores
        
        # Normalisation du score d'anomalie (plus négatif = plus anormal)
        # Conversion vers un score entre 0 et 1 (1 = très anormal)
        min_score = anomaly_scores.min()
        max_score = anomaly_scores.max()
        if max_score != min_score:
            results['anomaly_confidence'] = 1 - (anomaly_scores - min_score) / (max_score - min_score)
        else:
            results['anomaly_confidence'] = 0.5
        
        # Filtrage pour ne garder que les anomalies détectées
        anomalies = results[results['predicted_anomaly'] == 1].copy()
        
        if not anomalies.empty:
            # Tri par score d'anomalie (plus suspects en premier)
            anomalies = anomalies.sort_values('anomaly_confidence', ascending=False)
            
            # Classification du niveau de criticité
            def classify_severity(confidence):
                if confidence >= 0.8:
                    return 'Critique'
                elif confidence >= 0.6:
                    return 'Élevé'
                elif confidence >= 0.4:
                    return 'Moyen'
                else:
                    return 'Faible'
            
            anomalies['severity'] = anomalies['anomaly_confidence'].apply(classify_severity)
            
            print(f"🚨 {len(anomalies)} anomalies détectées!")
            print(f"   - Critiques: {len(anomalies[anomalies['severity'] == 'Critique'])}")
            print(f"   - Élevées: {len(anomalies[anomalies['severity'] == 'Élevé'])}")
            print(f"   - Moyennes: {len(anomalies[anomalies['severity'] == 'Moyen'])}")
            print(f"   - Faibles: {len(anomalies[anomalies['severity'] == 'Faible'])}")
        else:
            print("✅ Aucune anomalie détectée.")
        
        return anomalies
    
    def get_model_info(self):
        """Retourne des informations sur le modèle entraîné"""
        if not self.is_trained:
            return {"status": "Non entraîné"}
        
        return {
            "status": "Entraîné",
            "features_count": len(self.feature_columns),
            "features": self.feature_columns,
            "model_type": "Isolation Forest",
            "n_estimators": self.model.n_estimators,
            "contamination": self.model.contamination
        }
