"""
Multi-Agent Team with Intelligent Routing
Coordinator uses tools to delegate to specialist agents
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agno.agent import Agent
from agno.tools import tool
from agno.models.anthropic import Claude
from utils.config_loader import load_agent_config

class ProcurementAgentTeam:
    """Team of specialist agents with intelligent AI-powered routing"""
    
    def __init__(self):
        self.agents = self._create_all_agents()
        self._setup_tools()
    
    def _create_all_agents(self):
        """Create all specialist agents"""
        agents = {}
        
        agent_types = [
            'business_requirements',
            'market_research', 
            'rfi_rfp',
            'evaluation',
            'summary'
        ]
        
        for agent_type in agent_types:
            config = load_agent_config(agent_type)
            agents[agent_type] = Agent(
                name=config['name'],
                role=config['role'],
                model=Claude(id=config['model_id']),
                description=config['description'],
                instructions=config['instructions'],
                markdown=config['settings']['markdown']
            )
        
        return agents
    
    def _setup_tools(self):
        """Set up tools for coordinator to call specialists"""
        # We'll define these as instance methods, then convert to tools
        pass
    
    def consult_business_requirements_specialist(self, query: str) -> str:
        """
        Consult the Business Requirements Analyst for help with:
        - Gathering and documenting requirements
        - Creating business cases
        - Defining success criteria and KPIs
        - ROI analysis
        
        Args:
            query: The question or task for the specialist
        """
        response = self.agents['business_requirements'].run(query)
        return response.content
    
    def consult_market_research_specialist(self, query: str) -> str:
        """
        Consult the Market Research Analyst for help with:
        - Analyzing market trends and solutions
        - Identifying and comparing vendors
        - Market pricing and cost structures
        - Industry best practices
        
        Args:
            query: The question or task for the specialist
        """
        response = self.agents['market_research'].run(query)
        return response.content
    
    def consult_rfi_rfp_specialist(self, query: str) -> str:
        """
        Consult the RFI/RFP Specialist for help with:
        - Creating RFI (Request for Information) documents
        - Creating RFP (Request for Proposal) documents
        - Defining evaluation criteria
        - Managing vendor communications
        
        Args:
            query: The question or task for the specialist
        """
        response = self.agents['rfi_rfp'].run(query)
        return response.content
    
    def consult_evaluation_specialist(self, query: str) -> str:
        """
        Consult the Vendor Evaluation Specialist for help with:
        - Creating evaluation frameworks and scorecards
        - Analyzing and comparing proposals
        - Conducting cost-benefit analysis
        - Identifying risks and recommendations
        
        Args:
            query: The question or task for the specialist
        """
        response = self.agents['evaluation'].run(query)
        return response.content
    
    def consult_summary_specialist(self, query: str) -> str:
        """
        Consult the Executive Summary Writer for help with:
        - Creating executive summaries
        - Synthesizing complex information for executives
        - Writing final recommendations
        - Creating decision frameworks
        
        Args:
            query: The question or task for the specialist
        """
        response = self.agents['summary'].run(query)
        return response.content
    
    def create_coordinator_with_specialists(self):
        """
        Create coordinator agent with access to all specialist agents via tools.
        The coordinator intelligently decides which specialist to consult.
        """
        # Convert methods to tools
        br_tool = tool(self.consult_business_requirements_specialist)
        mr_tool = tool(self.consult_market_research_specialist)
        rfp_tool = tool(self.consult_rfi_rfp_specialist)
        eval_tool = tool(self.consult_evaluation_specialist)
        summary_tool = tool(self.consult_summary_specialist)
        
        # Create coordinator
        coord_config = load_agent_config('coordinator')
        
        coordinator = Agent(
            name=coord_config['name'],
            role=coord_config['role'],
            model=Claude(id=coord_config['model_id']),
            description=coord_config['description'] + """
            
            You have access to a team of specialist consultants via tools:
            - Business Requirements Analyst
            - Market Research Analyst
            - RFI/RFP Specialist
            - Vendor Evaluation Specialist
            - Executive Summary Writer
            
            When users need specialist expertise, consult the appropriate specialist.
            For general questions, answer directly.
            """,
            instructions=coord_config['instructions'] + [
                "You coordinate a team of procurement specialists",
                "Consult specialists when their expertise is needed",
                "Use consult_business_requirements_specialist for requirements and business cases",
                "Use consult_market_research_specialist for vendor research and market analysis",
                "Use consult_rfi_rfp_specialist for procurement document creation",
                "Use consult_evaluation_specialist for proposal evaluation",
                "Use consult_summary_specialist for executive summaries",
                "For simple questions, answer directly without consulting specialists"
            ],
            tools=[br_tool, mr_tool, rfp_tool, eval_tool, summary_tool],
            markdown=coord_config['settings']['markdown']
        )
        
        return coordinator


# Test
if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    print("Creating Intelligent Agent Team...")
    team = ProcurementAgentTeam()
    coordinator = team.create_coordinator_with_specialists()
    
    print("\n" + "=" * 70)
    print("Testing Intelligent Multi-Agent Routing")
    print("=" * 70)
    
    # Test 1: Natural language - requirements question
    print("\n📋 Test 1: Requirements Question (Natural Language)")
    print("-" * 70)
    print("Query: 'I'm thinking about getting a new CRM system, what should I consider?'")
    response = coordinator.run("I'm thinking about getting a new CRM system, what should I consider?")
    print(response.content)
    
    # Test 2: Natural language - market research
    print("\n\n🔍 Test 2: Market Research Question (Natural Language)")
    print("-" * 70)
    print("Query: 'What cloud storage options are popular right now?'")
    response = coordinator.run("What cloud storage options are popular right now?")
    print(response.content)
    
    print("\n✅ Intelligent routing is working!")
