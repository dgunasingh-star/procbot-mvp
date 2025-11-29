"""
Natural Language Chat with Tool Use
Agents intelligently call tools based on conversation
"""

from agents.coordinator_agent import create_coordinator_agent
from utils.project_tools import ProjectTools
from agno.tools import tool
from dotenv import load_dotenv

load_dotenv()

# Create global project tools instance
project_tools = ProjectTools()

# Define tools that agents can use
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

def create_tool_enabled_coordinator():
    """Create coordinator with project management tools"""
    from agno.agent import Agent
    from agno.models.anthropic import Claude
    from utils.config_loader import load_agent_config
    
    config = load_agent_config('coordinator')
    
    agent = Agent(
        name=config['name'],
        role=config['role'],
        model=Claude(id=config['model_id']),
        description=config['description'],
        instructions=config['instructions'] + [
            "You have access to project management tools",
            "Use list_all_projects when users ask about their projects",
            "Use create_new_project when starting new procurement",
            "Use load_project to load an existing project by ID",
            "Use get_project_status when users ask about status",
            "Use add_context to save important details about the project"
        ],
        tools=[list_all_projects, create_new_project, load_project, get_project_status, add_context],
        markdown=config['settings']['markdown']
    )
    
    return agent

class ToolEnabledChat:
    """Chat interface with intelligent tool use"""
    
    def __init__(self):
        self.coordinator = create_tool_enabled_coordinator()
        self.project_tools = project_tools
    
    def display_welcome(self):
        """Display welcome message"""
        print("\n" + "=" * 70)
        print("  PROCBOT - Your Intelligent Procurement Assistant")
        print("=" * 70)
        print("\nHello! I'm your procurement coordinator with full project management.")
        print("\nI can help you with:")
        print("  • Starting and tracking procurement projects")
        print("  • Gathering requirements and building business cases")
        print("  • Market research and vendor analysis")
        print("  • Creating RFI/RFP documents")
        print("  • Evaluating proposals")
        print("  • Executive summaries")
        print("\nJust talk naturally - I understand what you need!")
        print("\nType 'exit', 'quit', or 'bye' to end our chat.")
        print("=" * 70)
    
    def chat(self, user_message: str):
        """Have a conversation"""
        
        # Save user message if we have a project
        self.project_tools.save_conversation('user', user_message)
        
        # Build context if we have a current project
        current_project = self.project_tools.get_current_project()
        enriched_prompt = user_message
        
        if current_project:
            context_info = f"\n\n[Current Project Context]"
            context_info += f"\nProject: {current_project['project_name']}"
            context_info += f"\nStage: {current_project['current_stage']}"
            
            if current_project['context']:
                context_info += "\nKnown Details:"
                for key, value in current_project['context'].items():
                    context_info += f"\n  - {key}: {value}"
            
            enriched_prompt = f"{user_message}{context_info}"
        
        # Get response (non-streaming for tool compatibility)
        print("\n🤖 PROCBOT: ", end="", flush=True)
        
        try:
            # Use non-streaming for better tool response handling
            response = self.coordinator.run(enriched_prompt)
            
            # Extract and print the response
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
            print(f"\nError getting response: {e}")
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
                    indicator = f"[{project_name[:30]}] " if len(project_name) <= 30 else f"[{project_name[:27]}...] "
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
    chat = ToolEnabledChat()
    chat.run()
