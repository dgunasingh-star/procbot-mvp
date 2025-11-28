"""
Executive Summary Agent
Loads configuration from config/agent_config.yaml
"""

from agno.agent import Agent
from agno.models.anthropic import Claude
import os
import sys
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.config_loader import load_agent_config

load_dotenv()

def create_summary_agent():
    """Creates Summary Agent using external config"""
    config = load_agent_config('summary')
    
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
    agent = create_summary_agent()
    print("=" * 60)
    print("Executive Summary Agent - Test")
    print("=" * 60)
    print()
    
    agent.print_response(
        "Create an executive summary for a CRM procurement decision between Salesforce and HubSpot.",
        stream=True
    )
