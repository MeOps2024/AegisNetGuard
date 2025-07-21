import subprocess
import json
import pandas as pd
from datetime import datetime
import xml.etree.ElementTree as ET
import re
import socket
import psutil
import time
import threading
from database_manager import DatabaseManager

# Gérer l'import optionnel de pysnmp au niveau du module
try:
    from pysnmp.hlapi import (
        SnmpEngine, CommunityData, UdpTransportTarget,
        ContextData, ObjectType, ObjectIdentity, nextCmd
    )
    pysnmp_available = True
except ImportError:
    pysnmp_available = False

class RealNetworkCollector:
    """Collecteur de données réseau réelles pour AEGISLAN"""
    
    def __init__(self, network_range="192.168.1.0/24", db_manager=None):
        self.network_range = network_range
        self.db_manager = db_manager or DatabaseManager()
        self.is_monitoring = False
        self.monitoring_thread = None
        
    def scan_network_nmap(self, ports="1-1000"):
        """Scan réseau avec Nmap"""
        try:
            # Utiliser -oX - pour une sortie XML sur stdout, plus robuste à parser
            cmd = f"nmap -sS -O -p {ports} {self.network_range} -oX -"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                return self._parse_nmap_output(result.stdout)
            else:
                self.db_manager.log_system_event("ERROR", "NetworkCollector", f"Nmap scan failed: {result.stderr}")
                return pd.DataFrame()
                
        except subprocess.TimeoutExpired:
            self.db_manager.log_system_event("ERROR", "NetworkCollector", "Nmap scan timed out")
            return pd.DataFrame()
        except Exception as e:
            self.db_manager.log_system_event("ERROR", "NetworkCollector", f"Nmap error: {str(e)}")
            return pd.DataFrame()
    
    def _parse_nmap_output(self, output):
        """Parse la sortie Nmap"""
        """Parse la sortie XML de Nmap pour plus de robustesse."""
        try:
            devices = []
            root = ET.fromstring(output)

            for host in root.findall('host'):
                ip_address = host.find('address[@addrtype="ipv4"]').get('addr')
                mac_address_element = host.find('address[@addrtype="mac"]')
                mac_address = mac_address_element.get('addr') if mac_address_element is not None else 'Unknown'
                vendor = mac_address_element.get('vendor') if mac_address_element is not None else 'Unknown'

                device_type = self._detect_device_type(mac_address)
                if device_type == 'Unknown' and vendor != 'Unknown':
                    device_type = vendor

                devices.append({
                    'timestamp': datetime.now(),
                    'device_id': f"device_{ip_address.replace('.', '_')}",
                    'ip_address': ip_address,
                    'mac_address': mac_address,
                    'device_type': device_type,
                    'port': 0, # Le scan de base ne donne pas de port de connexion
                    'protocol': 'ARP/ICMP', # Le scan de découverte utilise ces protocoles
                    'data_volume_mb': 0,
                    'is_anomaly': False
                })
            return pd.DataFrame(devices)
        except ET.ParseError as e:
            self.db_manager.log_system_event("ERROR", "NetworkCollector", f"Nmap XML parsing failed: {e}")
            return pd.DataFrame()
    
    def _detect_device_type(self, mac_address):
        """Détecte le type d'appareil basé sur l'adresse MAC"""
        # Prefixes OUI courants
        oui_database = {
            '00:50:56': 'VMware',
            '08:00:27': 'VirtualBox',
            '00:0C:29': 'VMware',
            '00:1C:42': 'Parallels',
            '00:16:3E': 'Xen',
            '52:54:00': 'QEMU',
            '00:25:90': 'Samsung',
            '28:6A:BA': 'Apple',
            '70:56:81': 'Apple',
            '00:1B:63': 'Apple',
            '00:26:BB': 'Apple',
            '3C:07:54': 'Apple',
            '00:50:C2': 'Microsoft',
            '00:15:5D': 'Microsoft',
            '00:03:FF': 'Microsoft'
        }
        
        prefix = mac_address[:8].upper()
        return oui_database.get(prefix, 'Unknown')
    
    def collect_network_interfaces(self):
        """Collecte les informations des interfaces réseau"""
        interfaces_data = []
        
        try:
            # Utilisation de psutil pour obtenir les statistiques réseau
            net_io = psutil.net_io_counters(pernic=True)
            
            for interface, stats in net_io.items():
                if stats.bytes_sent > 0 or stats.bytes_recv > 0:
                    interfaces_data.append({
                        'timestamp': datetime.now(),
                        'interface': interface,
                        'bytes_sent': stats.bytes_sent,
                        'bytes_recv': stats.bytes_recv,
                        'packets_sent': stats.packets_sent,
                        'packets_recv': stats.packets_recv,
                        'errin': stats.errin,
                        'errout': stats.errout,
                        'dropin': stats.dropin,
                        'dropout': stats.dropout
                    })
            
            return pd.DataFrame(interfaces_data)
            
        except Exception as e:
            self.db_manager.log_system_event("ERROR", "NetworkCollector", f"Interface collection error: {str(e)}")
            return pd.DataFrame()
    
    def collect_active_connections(self):
        """Collecte les connexions actives"""
        connections_data = []
        
        try:
            connections = psutil.net_connections(kind='inet')
            
            for conn in connections:
                if conn.status == 'ESTABLISHED':
                    # Calculer le volume de données (approximatif)
                    data_volume = self._estimate_connection_volume(conn)
                    
                    connections_data.append({
                        'timestamp': datetime.now(),
                        'device_id': f"localhost_{conn.pid}",
                        'ip_address': conn.laddr.ip if conn.laddr else 'unknown',
                        'mac_address': 'localhost',
                        'device_type': 'workstation',
                        'port': conn.laddr.port if conn.laddr else 0,
                        'protocol': 'TCP' if conn.type == socket.SOCK_STREAM else 'UDP',
                        'data_volume_mb': data_volume,
                        'is_anomaly': False
                    })
            
            return pd.DataFrame(connections_data)
            
        except Exception as e:
            self.db_manager.log_system_event("ERROR", "NetworkCollector", f"Connections collection error: {str(e)}")
            return pd.DataFrame()
    
    def _estimate_connection_volume(self, connection):
        """Estime le volume de données pour une connexion"""
        # Estimation basique - pourrait être améliorée avec des outils comme netstat
        if connection.laddr and connection.laddr.port:
            # Ports connus et leurs volumes typiques
            port_volumes = {
                80: 0.5,    # HTTP
                443: 0.8,   # HTTPS
                22: 0.1,    # SSH
                21: 0.3,    # FTP
                25: 0.2,    # SMTP
                53: 0.05,   # DNS
                3389: 1.0,  # RDP
                5432: 0.3,  # PostgreSQL
                3306: 0.3,  # MySQL
            }
            return port_volumes.get(connection.laddr.port, 0.1)
        return 0.1
    
    def parse_router_logs(self, log_file_path):
        """Parse les logs de routeur/firewall"""
        try:
            with open(log_file_path, 'r') as f:
                lines = f.readlines()
            
            log_data = []
            for line in lines:
                # Format basique de log : timestamp src_ip dst_ip port protocol action
                parts = line.strip().split()
                if len(parts) >= 6:
                    try:
                        timestamp = datetime.strptime(parts[0] + ' ' + parts[1], '%Y-%m-%d %H:%M:%S')
                        src_ip = parts[2]
                        dst_ip = parts[3]
                        port = int(parts[4])
                        protocol = parts[5]
                        action = parts[6] if len(parts) > 6 else 'allow'
                        
                        log_data.append({
                            'timestamp': timestamp,
                            'device_id': f"device_{src_ip.split('.')[-1]}",
                            'ip_address': src_ip,
                            'mac_address': 'unknown',
                            'device_type': 'unknown',
                            'port': port,
                            'protocol': protocol,
                            'data_volume_mb': 0.1,
                            'is_anomaly': action == 'deny'
                        })
                    except (ValueError, IndexError):
                        continue
            
            return pd.DataFrame(log_data)
            
        except Exception as e:
            self.db_manager.log_system_event("ERROR", "NetworkCollector", f"Log parsing error: {str(e)}")
            return pd.DataFrame()
    
    def collect_snmp_data(self, router_ip, community="public"):
        """Collecte données SNMP depuis équipements réseau"""
        if not pysnmp_available:
            self.db_manager.log_system_event("WARNING", "NetworkCollector", "pysnmp not installed, SNMP collection disabled")
            return pd.DataFrame()

        try:
            snmp_data = []
            
            # OID pour interfaces réseau
            for (errorIndication, errorStatus, errorIndex, varBinds) in nextCmd(
                SnmpEngine(),
                CommunityData(community),
                UdpTransportTarget((router_ip, 161)),
                ContextData(),
                ObjectType(ObjectIdentity('1.3.6.1.2.1.2.2.1.10')),
                lexicographicMode=False,
                maxRows=10):
                
                if errorIndication:
                    break
                
                for varBind in varBinds:
                    oid, value = varBind
                    snmp_data.append({
                        'timestamp': datetime.now(),
                        'device_id': f"router_{router_ip.split('.')[-1]}",
                        'ip_address': router_ip,
                        'mac_address': 'router',
                        'device_type': 'router',
                        'port': 161,
                        'protocol': 'SNMP',
                        'data_volume_mb': float(value) / (1024 * 1024), # ifInOctets
                        'is_anomaly': False
                    })
            
            return pd.DataFrame(snmp_data)

        except Exception as e:
            self.db_manager.log_system_event("ERROR", "NetworkCollector", f"SNMP collection error: {str(e)}")
            return pd.DataFrame()
    
    def start_continuous_monitoring(self, interval=300):
        """Démarre la surveillance continue (toutes les 5 minutes par défaut)"""
        self.is_monitoring = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, args=(interval,))
        self.monitoring_thread.daemon = True
        self.monitoring_thread.start()
        
        self.db_manager.log_system_event("INFO", "NetworkCollector", "Continuous monitoring started")
    
    def stop_continuous_monitoring(self):
        """Arrête la surveillance continue"""
        self.is_monitoring = False
        if self.monitoring_thread:
            self.monitoring_thread.join()
        
        self.db_manager.log_system_event("INFO", "NetworkCollector", "Continuous monitoring stopped")
    
    def _monitoring_loop(self, interval):
        """Boucle de surveillance continue"""
        while self.is_monitoring:
            try:
                # Collecte des données depuis différentes sources
                nmap_data = self.scan_network_nmap()
                connections_data = self.collect_active_connections()
                interface_data = self.collect_network_interfaces()
                
                # Sauvegarde en base
                if not nmap_data.empty:
                    self.db_manager.insert_network_data(nmap_data)
                
                if not connections_data.empty:
                    self.db_manager.insert_network_data(connections_data)
                
                self.db_manager.log_system_event("INFO", "NetworkCollector", 
                                                f"Collected {len(nmap_data)} network devices, {len(connections_data)} connections")
                
                # Attendre avant le prochain cycle
                time.sleep(interval)
                
            except Exception as e:
                self.db_manager.log_system_event("ERROR", "NetworkCollector", f"Monitoring loop error: {str(e)}")
                time.sleep(60)  # Attendre 1 minute avant de réessayer
    
    def get_network_summary(self):
        """Résumé de l'état du réseau"""
        try:
            # Statistiques générales
            stats = self.db_manager.get_system_statistics()
            
            # Informations sur les interfaces
            interfaces = self.collect_network_interfaces()
            
            return {
                'network_stats': stats['network'],
                'interfaces_count': len(interfaces),
                'monitoring_status': 'active' if self.is_monitoring else 'stopped',
                'last_scan': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.db_manager.log_system_event("ERROR", "NetworkCollector", f"Summary generation error: {str(e)}")
            return {}