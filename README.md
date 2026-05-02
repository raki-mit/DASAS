# DASAS Admin Dashboard

## Distributed Android Screen Analytics System (DASAS)

### Production-Grade Admin Monitoring Application

---

## 📖 Overview

The **DASAS Admin Dashboard** is a Streamlit-based web application designed to monitor and manage the Distributed Android Screen Analytics System infrastructure. This admin interface provides comprehensive visibility into device clusters, fault tolerance mechanisms, and real-time analytics.

### Key Features

- 📱 **Device Management**: Monitor and manage Android devices in the P2P network
- 🔗 **Cluster Coordination**: Oversee cluster formation, leader election, and member management
- 🛡️ **Fault Tolerance**: Monitor Byzantine agreement and system resilience
- 📈 **Real-time Analytics**: Performance metrics and throughput visualization
- ⚙️ **System Configuration**: Customizable settings and monitoring preferences

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      DASAS Admin Dashboard                       │
│                     (Streamlit Web App)                          │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │   Devices   │  │   Clusters  │  │  Analytics  │             │
│  │   Manager   │  │   Manager   │  │   Manager   │             │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘             │
│         │                 │                 │                     │
│  ┌──────┴────────────────┴─────────────────┴──────┐              │
│  │              Database Manager                   │              │
│  │              (SQLite/PostgreSQL)               │              │
│  └─────────────────────────┬─────────────────────┘              │
│                            │                                      │
│  ┌─────────────────────────┴─────────────────────┐              │
│  │              Core Services                      │              │
│  │  • Configuration Management                     │              │
│  │  • Metrics Collection                           │              │
│  │  • Logging & Monitoring                         │              │
│  └─────────────────────────────────────────────────┘              │
│                            │                                      │
│         ┌──────────────────┴──────────────────┐                   │
│         │              External APIs           │                   │
│         │  • MQTT (Device Communication)      │                   │
│         │  • gRPC (Android Device API)        │                   │
│         │  • REST API (Optional)              │                   │
│         └──────────────────────────────────────┘                   │
└─────────────────────────────────────────────────────────────────┘
```
![High Level Diagram](https://raw.githubusercontent.com/raki-mit/DASAS/refs/heads/main/high%20level%20diragram.jpg?raw=True)

*High-level architecture diagram for DASAS.*

---

## 📁 Project Structure

```
admin_app/
├── app.py                    # Main Streamlit application
├── config.yaml               # Configuration file
├── requirements.txt          # Python dependencies
│
├── core/
│   ├── __init__.py
│   ├── config.py            # Configuration management
│   ├── logging_config.py    # Logging setup
│   └── metrics.py            # Metrics collection
│
├── db/
│   ├── __init__.py
│   └── database.py           # Database operations
│
├── api/
│   ├── __init__.py
│   ├── devices.py           # Device management API
│   ├── clusters.py          # Cluster management API
│   └── analytics.py          # Analytics & fault tolerance
│
└── ui/
    ├── __init__.py
    ├── components.py         # Reusable UI components
    └── pages.py              # Page implementations
```

---

## 🚀 Installation

### Prerequisites

- Python 3.9+
- pip or conda

### Setup

1. **Create virtual environment**
   ```bash
   python -m venv dasas_env
   source dasas_env/bin/activate  # Linux/Mac
   # or
   dasas_env\Scripts\activate     # Windows
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure application**
   ```bash
   cp config.yaml.example config.yaml
   # Edit config.yaml with your settings
   ```

4. **Initialize database**
   ```bash
   python -c "from db.database import db_manager; db_manager.initialize()"
   ```

5. **Run the application**
   ```bash
   streamlit run app.py
   ```

---

## 📋 Configuration

### config.yaml

The main configuration file controls all aspects of the application:

```yaml
# Application Settings
app:
  name: "DASAS Admin Dashboard"
  version: "1.0.0"
  host: "0.0.0.0"
  port: 8501

# Database Configuration
database:
  type: "sqlite"
  path: "./data/dasas_admin.db"
  pool_size: 10

# MQTT Configuration (Device Communication)
mqtt:
  broker: "localhost"
  port: 1883
  topic_prefix: "dasas/devices"

# Monitoring Settings
monitoring:
  refresh_interval: 30
  log_level: "INFO"
```

### Environment Variables

Override configuration with environment variables:

```bash
export DASAS_DB_TYPE=postgresql
export DASAS_DB_HOST=localhost
export DASAS_REDIS_PORT=6379
export DASAS_JWT_SECRET=your-secret-key
export DASAS_LOG_LEVEL=DEBUG
```

---

## 🎯 Usage

### Dashboard Navigation

1. **Dashboard**: Overview of system status, key metrics, and health indicators
2. **Devices**: Monitor and manage individual Android devices
3. **Clusters**: Manage device clusters and coordination
4. **Analytics**: View performance metrics and throughput
5. **Fault Tolerance**: Monitor Byzantine agreement and checkpoint status
6. **Settings**: Configure application preferences

### Device Registration

```python
from api.devices import device_manager

# Register a new device
result = device_manager.register_device(
    name="Device-001",
    device_info={
        "device_id": "abc123",
        "ip_address": "192.168.1.100",
        "android_version": "12",
        "cpu_cores": 8,
        "total_memory": 8192
    },
    cluster_id="cluster-001"
)
```

### Cluster Management

```python
from api.clusters import cluster_manager

# Create a new cluster
result = cluster_manager.create_cluster(
    name="Analytics Cluster",
    configuration={
        "election_timeout": 5000,
        "heartbeat_interval": 1000
    }
)

# Add device to cluster
cluster_manager.add_member(cluster_id, device_id)

# Start leader election
cluster_manager.start_election(cluster_id)
```

---

## 🛡️ Distributed Algorithms

The DASAS system implements several distributed algorithms:

### Ricart-Agrawala Mutual Exclusion

Used for coordinated access to shared ML services and resources across the cluster.

### Suzuki-Kasami Token-Based Allocation

Manages resource allocation using token passing for deadlock-free operation.

### Vector Clocks

Ensures causal ordering of events across the distributed mesh.

### Byzantine Agreement (Lamport-Shostak-Pease)

Provides fault tolerance against malicious or faulty nodes.

### Chain Replication

Supports high throughput and availability for checkpoint and recovery.

---

## 📊 Monitoring Features

### Real-time Metrics

- Device CPU and memory usage
- Network latency and throughput
- ML inference times
- Screen capture FPS

### Health Checks

- Database connectivity
- Cache performance
- Device heartbeat status
- Cluster coordination status

### Alerting

- Automatic alert generation for critical events
- Configurable severity levels
- Alert history and resolution tracking

---

## 🔧 API Reference

### Device Manager

| Method | Description |
|--------|-------------|
| `register_device()` | Register a new device |
| `get_device()` | Get device information |
| `get_all_devices()` | List all devices |
| `update_device_status()` | Update device status |
| `send_command()` | Send command to device |
| `restart_device()` | Restart a device |

### Cluster Manager

| Method | Description |
|--------|-------------|
| `create_cluster()` | Create a new cluster |
| `get_cluster()` | Get cluster information |
| `add_member()` | Add device to cluster |
| `remove_member()` | Remove device from cluster |
| `start_election()` | Start leader election |
| `request_resource()` | Request mutual exclusion |

### Analytics Manager

| Method | Description |
|--------|-------------|
| `create_checkpoint()` | Create system checkpoint |
| `restore_from_checkpoint()` | Restore from checkpoint |
| `detect_faulty_nodes()` | Run Byzantine agreement |
| `get_performance_metrics()` | Get performance data |
| `export_analytics()` | Export analytics data |

---


---

## 🔒 Security

### Authentication

The application supports JWT-based authentication:

```python
# Configure in config.yaml
auth:
  enabled: true
  jwt_secret: "your-secure-secret"
  jwt_algorithm: "HS256"
  token_expire_minutes: 60
```

### Rate Limiting

```python
security:
  rate_limit:
    enabled: true
    requests_per_minute: 100
    burst_size: 10
```

### SSL/TLS

```python
security:
  ssl:
    enabled: true
    cert_path: "/etc/ssl/certs/cert.pem"
    key_path: "/etc/ssl/private/key.pem"
```

---

## 📝 Logging

Logs are stored in `./logs/` directory with automatic rotation:

```python
# Configure in config.yaml
logging:
  level: "INFO"
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  file_path: "./logs/dasas_admin.log"
  max_size: 10485760  # 10MB
  backup_count: 5
```

---

## 🧪 Testing

```bash
# Run unit tests
pytest tests/

# Run with coverage
pytest --cov=admin_app tests/

# Run specific test
pytest tests/test_devices.py -v
```

---

## 📄 License

This project is part of the Distributed Android Screen Analytics System (DASAS) for academic purposes.

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

---

## 📞 Support

For issues and questions:

- Create a GitHub issue
- Contact the development team

---

## 🙏 Acknowledgments

- Android Open Source Project
- TensorFlow Lite
- Streamlit Team
- Academic references for distributed algorithms

---

**Version:** 1.0.0  
**Last Updated:** 2024  
**Author:** DASAS Development Team
