"""
Project Management Tools for PROCBOT Agents
These tools allow agents to interact with project state
"""

from utils.state_manager import ProjectStateManager
from typing import Optional

class ProjectTools:
    """Tools for project management that agents can use"""
    
    def __init__(self):
        self.state_manager = ProjectStateManager()
        self.current_project = None
    
    def list_all_projects(self) -> str:
        """
        List all procurement projects.
        
        Returns:
            Formatted string with all projects
        """
        projects = self.state_manager.list_projects()
        
        if not projects:
            return "No projects found. You can create a new project anytime."
        
        result = "Here are all your projects:\n\n"
        for i, proj in enumerate(projects, 1):
            status_icon = "🟢" if proj['status'] == 'active' else "🔴"
            result += f"{i}. {status_icon} {proj['project_name']}\n"
            result += f"   ID: {proj['project_id']}\n"
            result += f"   Stage: {proj['current_stage']}\n"
            result += f"   Updated: {proj['updated_at']}\n\n"
        
        return result
    
    def create_new_project(self, project_name: str, context: Optional[dict] = None) -> str:
        """
        Create a new procurement project.
        
        Args:
            project_name: Name of the project
            context: Optional dictionary with initial context
            
        Returns:
            Confirmation message with project details
        """
        project_id = self.state_manager.create_project(project_name, context or {})
        self.current_project = self.state_manager.load_project(project_id)
        
        result = f"✅ Created new project: '{project_name}'\n"
        result += f"Project ID: {project_id}\n"
        result += f"Current Stage: {self.current_project['current_stage']}\n"
        
        if context:
            result += f"Initial Context: {context}\n"
        
        return result
    
    def get_project_status(self, project_id: Optional[str] = None) -> str:
        """
        Get status of current or specified project.
        
        Args:
            project_id: Optional project ID. If not provided, uses current project.
            
        Returns:
            Formatted project status
        """
        if project_id:
            try:
                project = self.state_manager.load_project(project_id)
            except ValueError:
                return f"Project {project_id} not found."
        else:
            if not self.current_project:
                return "No active project. Please create or load a project first."
            project = self.current_project
        
        result = f"📊 Project Status\n\n"
        result += f"Name: {project['project_name']}\n"
        result += f"ID: {project['project_id']}\n"
        result += f"Stage: {project['current_stage']}\n"
        result += f"Status: {project['status']}\n"
        result += f"Created: {project['created_at']}\n"
        result += f"Updated: {project['updated_at']}\n"
        
        if project['context']:
            result += f"\nContext:\n"
            for key, value in project['context'].items():
                result += f"  • {key}: {value}\n"
        
        result += f"\nConversations: {len(project['conversation_history'])}\n"
        
        return result
    
    def load_existing_project(self, project_id: str) -> str:
        """
        Load an existing project.
        
        Args:
            project_id: ID of the project to load
            
        Returns:
            Confirmation message
        """
        try:
            self.current_project = self.state_manager.load_project(project_id)
            
            result = f"✅ Loaded project: {self.current_project['project_name']}\n"
            result += f"Stage: {self.current_project['current_stage']}\n"
            
            # Show recent conversation context
            history = self.current_project['conversation_history']
            if history:
                result += f"\nLast message: {history[-1]['message'][:100]}...\n"
            
            return result
        except ValueError as e:
            return f"Error: {str(e)}"
    
    def add_project_context(self, key: str, value: str) -> str:
        """
        Add context information to current project.
        
        Args:
            key: Context key (e.g., 'budget', 'department')
            value: Context value
            
        Returns:
            Confirmation message
        """
        if not self.current_project:
            return "No active project. Create or load a project first."
        
        context = self.current_project.get('context', {})
        context[key] = value
        
        self.state_manager.update_project(
            self.current_project['project_id'],
            {'context': context}
        )
        
        self.current_project = self.state_manager.load_project(
            self.current_project['project_id']
        )
        
        return f"✅ Added context: {key} = {value}"
    
    def get_current_project(self) -> Optional[dict]:
        """Get current project state"""
        return self.current_project
    
    def save_conversation(self, role: str, message: str, agent: Optional[str] = None):
        """Save conversation to current project"""
        if self.current_project:
            self.state_manager.add_conversation(
                self.current_project['project_id'],
                role=role,
                message=message,
                agent=agent
            )
            self.current_project = self.state_manager.load_project(
                self.current_project['project_id']
            )
