"""
Coordinator Agent - The main interface for PROCBOT
This agent orchestrates the procurement workflow
Configuration is loaded from config/agent_config.yaml
"""

from agno.agent import Agent
from agno.models.anthropic import Claude
import os
import sys
from dotenv import load_dotenv

# Add parent directory to path to import utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.config_loader import load_agent_config

# Load environment variables
load_dotenv()

def create_coordinator_agent():
    """
    Creates the Coordinator Agent using configuration from YAML file
    """
    # Load configuration
    config = load_agent_config('coordinator')
    
    # Create agent with config
    agent = Agent(
        name=config['name'],
        role=config['role'],
        model=Claude(id=config['model_id']),
        description=config['description'],
        instructions=config['instructions'],
        markdown=config['settings']['markdown']
    )
    
    return agent

if __name__ == "__main__":
    # Create the agent
    coordinator = create_coordinator_agent()
    
    # Test interaction
    print("=" * 60)
    print("PROCBOT Coordinator Agent - MVP Test")
    print("(Configuration loaded from config/agent_config.yaml)")
    print("=" * 60)
    print()
    
    # Simple test query
    coordinator.print_response(
        "Hello! I'm starting a new procurement project for cloud storage solutions. Can you help me understand what information you'll need?",
        stream=True
    )
