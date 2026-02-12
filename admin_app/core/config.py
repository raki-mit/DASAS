"""
DASAS Core Configuration Module
================================
Handles configuration loading and management for the DASAS Admin Dashboard.

Author: DASAS Team
Version: 1.0.0
"""

import os
from pathlib import Path
from typing import Any, Dict, Optional
from functools import lru_cache

import yaml
from pydantic import BaseModel, Field


class AppConfig(BaseModel):
    """Application configuration model"""
    name: str = "DASAS Admin Dashboard"
    version: str = "1.0.0"
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8501
    secret_key: str = "change-me-in-production"
    allowed_hosts: list = ["*"]


class DatabaseConfig(BaseModel):
    """Database configuration model"""
    type: str = "sqlite"
    path: str = "./data/dasas_admin.db"
    pool_size: int = 10
    max_overflow: int = 20
    host: Optional[str] = None
    port: Optional[int] = None
    name: Optional[str] = None
    user: Optional[str] = None
    password: Optional[str] = None
    
    @property
    def connection_string(self) -> str:
        """Get database connection string"""
        if self.type == "sqlite":
            return f"sqlite:///{self.path}"
        elif self.type == "postgresql":
            return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"
        return ""


class RedisConfig(BaseModel):
    """Redis configuration model"""
    host: str = "localhost"
    port: int = 6379
    db: int = 0
    password: Optional[str] = None
    key_prefix: str = "dasas:"
    cache_ttl: int = 300


class MQTTConfig(BaseModel):
    """MQTT configuration model"""
    broker: str = "localhost"
    port: int = 1883
    username: Optional[str] = None
    password: Optional[str] = None
    client_id: str = "dasas_admin"
    topic_prefix: str = "dasas/devices"
    qos: int = 1
    keepalive: int = 60


class GRPCConfig(BaseModel):
    """gRPC configuration model"""
    host: str = "0.0.0.0"
    port: int = 50051
    max_workers: int = 10
    max_message_length: int = 104857600


class APIConfig(BaseModel):
    """REST API configuration model"""
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    title: str = "DASAS Admin API"
    description: str = "REST API for managing DASAS infrastructure"
    version: str = "1.0.0"
    docs_url: str = "/docs"
    redoc_url: str = "/redoc"


class AuthConfig(BaseModel):
    """Authentication configuration model"""
    enabled: bool = True
    jwt_secret: str = "change-jwt-secret-in-production"
    jwt_algorithm: str = "HS256"
    token_expire_minutes: int = 60
    refresh_token_expire_days: int = 7


class MonitoringConfig(BaseModel):
    """Monitoring configuration model"""
    refresh_interval: int = 30
    metrics_retention_days: int = 30
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


class DeviceConfig(BaseModel):
    """Device management configuration model"""
    heartbeat_timeout: int = 60
    max_devices_per_cluster: int = 100
    auto_register: bool = True
    registration_token: str = "device-registration-token"


class ClusterConfig(BaseModel):
    """Cluster management configuration model"""
    max_clusters: int = 50
    election_timeout: int = 5000
    heartbeat_interval: int = 1000
    join_timeout: int = 30000


class FaultToleranceConfig(BaseModel):
    """Fault tolerance configuration model"""
    quorum_size: int = 3
    faulty_nodes_tolerance: int = 1
    agreement_timeout: int = 10000
    checkpoint_interval: int = 300
    checkpoint_retention: int = 24


class AnalyticsConfig(BaseModel):
    """Analytics configuration model"""
    raw_data_retention: int = 7
    aggregated_data_retention: int = 30
    batch_size: int = 1000
    processing_interval: int = 60


class Settings(BaseModel):
    """
    Main settings class that aggregates all configuration models.
    
    This class provides a centralized configuration management system
    for the DASAS Admin Dashboard.
    """
    app: AppConfig = Field(default_factory=AppConfig)
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    redis: RedisConfig = Field(default_factory=RedisConfig)
    mqtt: MQTTConfig = Field(default_factory=MQTTConfig)
    grpc: GRPCConfig = Field(default_factory=GRPCConfig)
    api: APIConfig = Field(default_factory=APIConfig)
    auth: AuthConfig = Field(default_factory=AuthConfig)
    monitoring: MonitoringConfig = Field(default_factory=MonitoringConfig)
    devices: DeviceConfig = Field(default_factory=DeviceConfig)
    clusters: ClusterConfig = Field(default_factory=ClusterConfig)
    fault_tolerance: FaultToleranceConfig = Field(default_factory=FaultToleranceConfig)
    analytics: AnalyticsConfig = Field(default_factory=AnalyticsConfig)
    
    @classmethod
    def from_yaml(cls, config_path: str) -> "Settings":
        """
        Load settings from YAML configuration file.
        
        Args:
            config_path: Path to the YAML configuration file
            
        Returns:
            Settings instance with loaded configuration
        """
        config_file = Path(config_path)
        
        if not config_file.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        with open(config_file, "r") as f:
            config_data = yaml.safe_load(f)
        
        return cls(**config_data)
    
    @classmethod
    def from_env(cls) -> "Settings":
        """
        Load settings from environment variables.
        
        Environment variables take precedence over YAML config.
        
        Returns:
            Settings instance with configuration from environment
        """
        # Map environment variables to settings
        env_mappings = {
            "DASAS_DB_TYPE": ("database", "type"),
            "DASAS_DB_PATH": ("database", "path"),
            "DASAS_DB_HOST": ("database", "host"),
            "DASAS_DB_PORT": ("database", "port"),
            "DASAS_DB_NAME": ("database", "name"),
            "DASAS_DB_USER": ("database", "user"),
            "DASAS_DB_PASSWORD": ("database", "password"),
            "DASAS_REDIS_HOST": ("redis", "host"),
            "DASAS_REDIS_PORT": ("redis", "port"),
            "DASAS_MQTT_BROKER": ("mqtt", "broker"),
            "DASAS_MQTT_PORT": ("mqtt", "port"),
            "DASAS_API_HOST": ("api", "host"),
            "DASAS_API_PORT": ("api", "port"),
            "DASAS_JWT_SECRET": ("auth", "jwt_secret"),
            "DASAS_LOG_LEVEL": ("monitoring", "log_level"),
        }
        
        config_dict = {}
        for env_var, (section, key) in env_mappings.items():
            value = os.environ.get(env_var)
            if value:
                if section not in config_dict:
                    config_dict[section] = {}
                config_dict[section][key] = value
        
        return cls(**config_dict) if config_dict else cls()
    
    @classmethod
    def load(cls, config_path: Optional[str] = None) -> "Settings":
        """
        Load settings with multiple fallback options.
        
        Priority:
        1. Environment variables
        2. YAML configuration file
        3. Default values
        
        Args:
            config_path: Optional path to YAML configuration file
            
        Returns:
            Settings instance with loaded configuration
        """
        # First try environment variables
        settings = cls.from_env()
        
        # Then try YAML file if provided
        if config_path:
            try:
                yaml_settings = cls.from_yaml(config_path)
                # Merge YAML config (keeping environment overrides)
                settings = cls.merge_settings(settings, yaml_settings)
            except FileNotFoundError:
                pass
        
        return settings
    
    @staticmethod
    def merge_settings(base: "Settings", override: "Settings") -> "Settings":
        """
        Merge two settings objects, with override taking precedence.
        
        Args:
            base: Base settings object
            override: Override settings object
            
        Returns:
            Merged Settings instance
        """
        # This is a simplified merge - in production, use deep merge
        return override


@lru_cache()
def get_settings(config_path: Optional[str] = None) -> Settings:
    """
    Get cached settings instance.
    
    This function provides a singleton-like pattern for settings,
    ensuring configuration is loaded only once.
    
    Args:
        config_path: Optional path to YAML configuration file
        
    Returns:
        Cached Settings instance
    """
    return Settings.load(config_path)


# Global settings instance
settings = get_settings()
