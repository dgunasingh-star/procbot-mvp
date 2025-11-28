"""
Vendor Evaluation Agent
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

def create_evaluation_agent():
    """Creates Evaluation Agent using external config"""
    config = load_agent_config('evaluation')
    
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
    agent = create_evaluation_agent()
    print("=" * 60)
    print("Vendor Evaluation Agent - Test")
    print("=" * 60)
    print()
    
    agent.print_response(
        "I need to evaluate 3 vendors for cloud storage. What evaluation framework should I use?",
        stream=True
    )
