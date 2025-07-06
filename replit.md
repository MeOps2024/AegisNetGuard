# AEGISLAN - Network Anomaly Detection System

## Overview

AEGISLAN is a real-time network anomaly detection system built with Python and Streamlit. It uses machine learning algorithms (specifically Isolation Forest) to identify suspicious network behavior and provides an interactive dashboard for monitoring network security. The system simulates realistic network traffic data and applies AI-powered anomaly detection to help identify potential security threats.

## System Architecture

The application follows a modular architecture with four main components:

1. **Frontend**: Streamlit-based web interface for interactive dashboards and controls
2. **Data Layer**: Network traffic simulation engine that generates realistic data patterns
3. **ML Engine**: Anomaly detection using scikit-learn's Isolation Forest algorithm
4. **Visualization**: Plotly-based charts and graphs for data analysis

The architecture is designed for simplicity and educational purposes, making it easy to understand and extend.

## Key Components

### 1. Application Core (`app.py`)
- **Purpose**: Main Streamlit application entry point
- **Responsibilities**: Session state management, UI layout, component coordination
- **Key Features**: Sidebar controls, data simulation parameters, model training interface

### 2. Data Simulation (`data_simulator.py`)
- **Purpose**: Generates realistic network traffic data for testing and demonstration
- **Capabilities**: 
  - Simulates different device types (workstations, servers, printers, phones, tablets, IoT devices)
  - Creates behavioral patterns based on device profiles
  - Generates network metadata (IP addresses, MAC addresses, ports, protocols)
  - Injects configurable anomaly rates for testing

### 3. Anomaly Detection Engine (`anomaly_detector.py`)
- **Purpose**: Core ML component for detecting network anomalies
- **Algorithm**: Isolation Forest (unsupervised learning)
- **Features**:
  - Feature engineering for temporal and categorical data
  - Standard scaling and label encoding
  - Configurable anomaly thresholds
  - Model persistence capabilities

### 4. Dashboard Interface (`dashboard.py`)
- **Purpose**: Interactive visualization and monitoring interface
- **Components**:
  - Real-time system status indicators
  - Key performance metrics
  - Alert management system
  - Traffic timeline visualizations
  - Device activity monitoring

## Data Flow

1. **Data Generation**: NetworkDataSimulator creates realistic network traffic patterns
2. **Feature Engineering**: AnomalyDetector processes raw data into ML-ready features
3. **Model Training**: Isolation Forest algorithm learns normal network behavior patterns
4. **Anomaly Detection**: Trained model identifies deviations from normal patterns
5. **Visualization**: Dashboard renders results through interactive charts and alerts
6. **User Interaction**: Streamlit interface allows real-time parameter adjustment

## External Dependencies

### Core Libraries
- **Streamlit**: Web application framework for the user interface
- **Pandas**: Data manipulation and analysis
- **NumPy**: Numerical computing for feature engineering
- **Scikit-learn**: Machine learning algorithms and preprocessing
- **Plotly**: Interactive data visualization

### Rationale for Technology Choices
- **Streamlit**: Chosen for rapid prototyping and ease of deployment
- **Isolation Forest**: Selected for its effectiveness with unlabeled data and ability to detect outliers
- **Plotly**: Provides interactive charts that enhance user experience
- **Pandas**: Industry standard for data manipulation in Python

## Deployment Strategy

The application is designed for simple deployment scenarios:

1. **Development**: Local Streamlit server for testing and development
2. **Demo Environment**: Single-container deployment suitable for demonstrations
3. **Educational Use**: Easy setup for learning environments

The system does not currently include:
- Database persistence (uses in-memory storage)
- Authentication mechanisms
- Production-scale optimizations
- Distributed processing capabilities

## User Preferences

Preferred communication style: Simple, everyday language.

## Changelog

Changelog:
- July 06, 2025. Initial setup