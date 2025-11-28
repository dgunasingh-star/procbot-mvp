"""
Configuration Loader Utility
Loads agent configurations from YAML files
"""

import yaml
import os

def load_agent_config(agent_name):
    """
    Load configuration for a specific agent
    
    Args:
        agent_name: Name of the agent (e.g., 'coordinator', 'business_requirements')
    
    Returns:
        Dictionary with agent configuration
    """
    config_path = os.path.join('config', 'agent_config.yaml')
    
    with open(config_path, 'r') as file:
        all_configs = yaml.safe_load(file)
    
    if agent_name not in all_configs:
        raise ValueError(f"Configuration for agent '{agent_name}' not found")
    
    return all_configs[agent_name]

def get_all_agent_configs():
    """
    Load all agent configurations
    
    Returns:
        Dictionary with all agent configurations
    """
    config_path = os.path.join('config', 'agent_config.yaml')
    
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)
