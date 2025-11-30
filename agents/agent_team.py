"""
PROCBOT Agent Team
Multi-agent system with specialized procurement experts
All configuration comes from YAML - NO hardcoded instructions!
"""

from agno import Agent
import yaml
from pathlib import Path

def load_agent_config(agent_name: str) -> dict:
    """Load configuration for a specific agent from YAML"""
    config_path = Path("config/agent_config.yaml")
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    return config.get(agent_name, {})

def create_agent_from_config(agent_name: str) -> Agent:
    """Create an agent entirely from YAML configuration"""
    config = load_agent_config(agent_name)
    
    agent = Agent(
        name=config['name'],
        role=config['role'],
        model=config['model_id'],
        description=config['description'],
        instructions=config['instructions'],
        markdown=config['settings']['markdown'],
        show_tool_calls=False
    )
    
    return agent

def create_business_requirements_agent():
    """Create the Business Requirements Analyst agent"""
    return create_agent_from_config('business_requirements')

def create_market_research_agent():
    """Create the Market Research Analyst agent"""
    return create_agent_from_config('market_research')

def create_rfi_rfp_agent():
    """Create the RFI/RFP Specialist agent"""
    return create_agent_from_config('rfi_rfp')

def create_evaluation_agent():
    """Create the Vendor Evaluation Specialist agent"""
    return create_agent_from_config('vendor_evaluation')

def create_summary_agent():
    """Create the Executive Summary Writer agent"""
    return create_agent_from_config('executive_summary')

def create_coordinator_with_team():
    """Create coordinator with full specialist team - all from YAML config"""
    
    # Load coordinator config (everything comes from YAML!)
    config = load_agent_config('coordinator')
    
    # Create specialist agents
    business_req_agent = create_business_requirements_agent()
    market_research_agent = create_market_research_agent()
    rfi_rfp_agent = create_rfi_rfp_agent()
    evaluation_agent = create_evaluation_agent()
    summary_agent = create_summary_agent()
    
    # Create coordinator with specialist tools
    coordinator = Agent(
        name=config['name'],
        role=config['role'],
        model=config['model_id'],
        description=config['description'],  # All instructions in YAML!
        instructions=config['instructions'],
        markdown=config['settings']['markdown'],
        show_tool_calls=False,
        team=[
            business_req_agent,
            market_research_agent,
            rfi_rfp_agent,
            evaluation_agent,
            summary_agent
        ]
    )
    
    return coordinator
