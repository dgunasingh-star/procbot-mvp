"""
PROCBOT Chat with Multi-Agent Team and Full Workflow Management
"""

from utils.agent_team import ProcurementAgentTeam
from utils.project_tools import ProjectTools
from agno.tools import tool
from dotenv import load_dotenv

load_dotenv()

# Create global instances
project_tools = ProjectTools()
agent_team = ProcurementAgentTeam()

# Project management tools
@tool
def list_all_projects() -> str:
    """List all procurement projects in the system."""
    return project_tools.list_all_projects()

@tool
def create_new_project(project_name: str) -> str:
    """
    Create a new procurement project.
    
    Args:
        project_name: Name of the procurement project
    """
    return project_tools.create_new_project(project_name)

@tool
def load_project(project_id: str) -> str:
    """
    Load an existing project to continue working on it.
    
    Args:
        project_id: The project ID to load (e.g., proj_20251129_002036)
    """
    return project_tools.load_existing_project(project_id)

@tool
def get_project_status() -> str:
    """Get the status of the current project."""
    return project_tools.get_project_status()

@tool
def add_context(key: str, value: str) -> str:
    """
    Add context information to the current project.
    
    Args:
        key: The context key (e.g., 'budget', 'department', 'timeline')
        value: The context value
    """
    return project_tools.add_project_context(key, value)

@tool
def manage_project_workflow(action: str, reason: str = "", target_stage: str = "") -> str:
    """
    Comprehensive project lifecycle management.
    
    Actions supported:
    - cancel: Permanently mark project as cancelled (requires reason)
    - pause: Temporarily put project on hold (requires reason)
    - resume: Reactivate a paused project
    - complete: Mark project as successfully finished
    - advance: Move to next procurement stage
    - revert: Go back to previous stage
    - jump_to: Go to a specific stage (requires target_stage)
    
    Args:
        action: The workflow action to perform
        reason: Explanation for the action (required for cancel/pause)
        target_stage: Target stage for 'jump_to' action (business_case, market_research, rfi_rfp, evaluation, summary)
    """
    return project_tools.manage_workflow(action, reason, target_stage)

# Specialist agent tools
@tool
def consult_business_requirements_specialist(query: str) -> str:
    """
    Consult the Business Requirements Analyst for help with:
    - Gathering and documenting requirements
    - Creating business cases
    - Defining success criteria and KPIs
    - ROI analysis
    
    Args:
        query: The question or task for the specialist
    """
    return agent_team.consult_business_requirements_specialist(query)

@tool
def consult_market_research_specialist(query: str) -> str:
    """
    Consult the Market Research Analyst for help with:
    - Analyzing market trends and solutions
    - Identifying and comparing vendors
    - Market pricing and cost structures
    - Industry best practices
    
    Args:
        query: The question or task for the specialist
    """
    return agent_team.consult_market_research_specialist(query)

@tool
def consult_rfi_rfp_specialist(query: str) -> str:
    """
    Consult the RFI/RFP Specialist for help with:
    - Creating RFI/RFP documents
    - Defining evaluation criteria
    - Managing vendor communications
    
    Args:
        query: The question or task for the specialist
    """
    return agent_team.consult_rfi_rfp_specialist(query)

@tool
def consult_evaluation_specialist(query: str) -> str:
    """
    Consult the Vendor Evaluation Specialist for help with:
    - Creating evaluation frameworks
    - Analyzing proposals
    - Cost-benefit analysis
    - Risk assessment
    
    Args:
        query: The question or task for the specialist
    """
    return agent_team.consult_evaluation_specialist(query)

@tool
def consult_summary_specialist(query: str) -> str:
    """
    Consult the Executive Summary Writer for help with:
    - Creating executive summaries
    - Synthesizing information for executives
    - Writing recommendations
    
    Args:
        query: The question or task for the specialist
    """
    return agent_team.consult_summary_specialist(query)

def create_full_coordinator():
    """Create coordinator with ALL capabilities"""
    from agno.agent import Agent
    from agno.models.anthropic import Claude
    from utils.config_loader import load_agent_config
    
    config = load_agent_config('coordinator')
    
    agent = Agent(
        name=config['name'],
        role=config['role'],
        model=Claude(id=config['model_id']),
        description=config['description'] + """
        
        You manage procurement projects AND coordinate specialist consultants:
        
        PROJECT MANAGEMENT:
        - Track and manage projects
        - Handle project lifecycle (cancel, pause, resume, complete)
        - Manage stage transitions
        
        SPECIALIST TEAM:
        - Business Requirements Analyst
        - Market Research Analyst
        - RFI/RFP Specialist
        - Vendor Evaluation Specialist
        - Executive Summary Writer
        
        Use tools to take action, consult specialists for expertise.
        """,
        instructions=config['instructions'] + [
            "You have comprehensive project management capabilities",
            "Use manage_project_workflow to cancel, pause, resume, complete projects",
            "Use manage_project_workflow to advance, revert, or jump between stages",
            "Consult specialists when expertise is needed",
            "For general guidance, answer directly"
        ],
        tools=[
            list_all_projects, 
            create_new_project, 
            load_project, 
            get_project_status, 
            add_context,
            manage_project_workflow,  # NEW WORKFLOW TOOL!
            consult_business_requirements_specialist,
            consult_market_research_specialist,
            consult_rfi_rfp_specialist,
            consult_evaluation_specialist,
            consult_summary_specialist
        ],
        markdown=config['settings']['markdown']
    )
    
    return agent

class ProcbotChat:
    """Complete PROCBOT chat"""
    
    def __init__(self):
        self.coordinator = create_full_coordinator()
        self.project_tools = project_tools
    
    def display_welcome(self):
        """Display welcome message"""
        print("\n" + "=" * 70)
        print("  PROCBOT - AI-Powered Procurement Assistant")
        print("=" * 70)
        print("\nHello! I coordinate a team of procurement specialists and manage")
        print("your project lifecycle.")
        print("\nI can help you:")
        print("  • Create and track procurement projects")
        print("  • Consult specialist agents for expert advice")
        print("  • Manage project workflow (cancel, pause, resume, complete)")
        print("  • Guide you through procurement stages")
        print("\nJust talk naturally - I'll figure out what you need.")
        print("\nType 'exit', 'quit', or 'bye' to end.")
        print("=" * 70)
    
    def chat(self, user_message: str):
        """Have a conversation"""
        
        # Save user message
        self.project_tools.save_conversation('user', user_message)
        
        # Build context
        current_project = self.project_tools.get_current_project()
        enriched_prompt = user_message
        
        if current_project:
            context_info = f"\n\n[Current Project Context]"
            context_info += f"\nProject: {current_project['project_name']}"
            context_info += f"\nStage: {current_project['current_stage']}"
            context_info += f"\nStatus: {current_project['status']}"
            
            if current_project['context']:
                context_info += "\nKnown Details:"
                for key, value in current_project['context'].items():
                    context_info += f"\n  - {key}: {value}"
            
            enriched_prompt = f"{user_message}{context_info}"
        
        # Get response
        print("\n🤖 PROCBOT: ", end="", flush=True)
        
        try:
            response = self.coordinator.run(enriched_prompt)
            
            if hasattr(response, 'content'):
                full_response = response.content
                print(full_response)
            else:
                full_response = str(response)
                print(full_response)
            
            print()
            
            # Save response
            self.project_tools.save_conversation('agent', full_response, 'coordinator')
            
        except Exception as e:
            print(f"\nError: {e}")
            import traceback
            traceback.print_exc()
    
    def run(self):
        """Run the chat interface"""
        self.display_welcome()
        
        while True:
            try:
                current_project = self.project_tools.get_current_project()
                if current_project:
                    project_name = current_project['project_name']
                    status = current_project['status']
                    
                    # Show status indicator
                    status_emoji = "🟢" if status == 'active' else "⏸️" if status == 'on_hold' else "🔴" if status == 'cancelled' else "✅"
                    
                    indicator = f"[{status_emoji} {project_name[:25]}] " if len(project_name) <= 25 else f"[{status_emoji} {project_name[:22]}...] "
                else:
                    indicator = ""
                
                user_input = input(f"\n{indicator}You: ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ['exit', 'quit', 'bye', 'goodbye']:
                    print("\n👋 Thank you for using PROCBOT! Goodbye!\n")
                    break
                
                self.chat(user_input)
                
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!\n")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
                import traceback
                traceback.print_exc()

if __name__ == "__main__":
    chat = ProcbotChat()
    chat.run()
