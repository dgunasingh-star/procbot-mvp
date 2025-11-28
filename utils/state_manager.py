"""
Project State Manager
Handles persistence and retrieval of project state across sessions
"""

import json
import os
import yaml
from datetime import datetime
from typing import Dict, List, Optional

class ProjectStateManager:
    """Manages project state persistence and retrieval"""
    
    def __init__(self):
        """Initialize state manager"""
        # Load configuration
        config_path = os.path.join('config', 'state_config.yaml')
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        # Create storage directory if it doesn't exist
        self.storage_dir = self.config['state_storage']['directory']
        os.makedirs(self.storage_dir, exist_ok=True)
    
    def create_project(self, project_name: str, context: Dict = None) -> str:
        """
        Create a new project
        
        Args:
            project_name: Name of the project
            context: Initial project context (optional)
            
        Returns:
            project_id: Unique identifier for the project
        """
        # Generate project ID (timestamp-based for simplicity)
        project_id = f"proj_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Initialize project state
        project_state = {
            'project_id': project_id,
            'project_name': project_name,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'current_stage': 'business_case',
            'status': 'active',
            'context': context or {},
            'conversation_history': [],
            'stage_outputs': {},
            'decisions': [],
            'next_actions': []
        }
        
        # Save to file
        self._save_project(project_id, project_state)
        
        return project_id
    
    def load_project(self, project_id: str) -> Dict:
        """
        Load project state
        
        Args:
            project_id: Project identifier
            
        Returns:
            Project state dictionary
        """
        file_path = os.path.join(self.storage_dir, f"{project_id}.json")
        
        if not os.path.exists(file_path):
            raise ValueError(f"Project {project_id} not found")
        
        with open(file_path, 'r') as f:
            return json.load(f)
    
    def update_project(self, project_id: str, updates: Dict):
        """
        Update project state
        
        Args:
            project_id: Project identifier
            updates: Dictionary of fields to update
        """
        project_state = self.load_project(project_id)
        
        # Update fields
        project_state.update(updates)
        project_state['updated_at'] = datetime.now().isoformat()
        
        # Save
        self._save_project(project_id, project_state)
    
    def add_conversation(self, project_id: str, role: str, message: str, agent: str = None):
        """
        Add a conversation entry to project history
        
        Args:
            project_id: Project identifier
            role: 'user' or 'agent'
            message: The message content
            agent: Which agent responded (if role is 'agent')
        """
        project_state = self.load_project(project_id)
        
        conversation_entry = {
            'timestamp': datetime.now().isoformat(),
            'role': role,
            'message': message,
            'agent': agent
        }
        
        project_state['conversation_history'].append(conversation_entry)
        project_state['updated_at'] = datetime.now().isoformat()
        
        self._save_project(project_id, project_state)
    
    def move_to_stage(self, project_id: str, new_stage: str):
        """
        Move project to a new stage
        
        Args:
            project_id: Project identifier
            new_stage: New stage ID
        """
        project_state = self.load_project(project_id)
        
        # Validate stage exists
        if new_stage not in self.config['stages']:
            raise ValueError(f"Stage '{new_stage}' not found in configuration")
        
        old_stage = project_state['current_stage']
        project_state['current_stage'] = new_stage
        project_state['updated_at'] = datetime.now().isoformat()
        
        # Log stage transition
        project_state['decisions'].append({
            'timestamp': datetime.now().isoformat(),
            'type': 'stage_transition',
            'from_stage': old_stage,
            'to_stage': new_stage
        })
        
        self._save_project(project_id, project_state)
    
    def save_stage_output(self, project_id: str, stage: str, output: Dict):
        """
        Save output from a specific stage
        
        Args:
            project_id: Project identifier
            stage: Stage ID
            output: Output data from the stage
        """
        project_state = self.load_project(project_id)
        
        project_state['stage_outputs'][stage] = {
            'timestamp': datetime.now().isoformat(),
            'output': output
        }
        project_state['updated_at'] = datetime.now().isoformat()
        
        self._save_project(project_id, project_state)
    
    def get_stage_info(self, stage_id: str) -> Dict:
        """
        Get information about a specific stage
        
        Args:
            stage_id: Stage identifier
            
        Returns:
            Stage configuration
        """
        if stage_id not in self.config['stages']:
            raise ValueError(f"Stage '{stage_id}' not found")
        
        return self.config['stages'][stage_id]
    
    def list_projects(self) -> List[Dict]:
        """
        List all projects
        
        Returns:
            List of project summaries
        """
        projects = []
        
        for filename in os.listdir(self.storage_dir):
            if filename.endswith('.json'):
                file_path = os.path.join(self.storage_dir, filename)
                with open(file_path, 'r') as f:
                    project = json.load(f)
                    projects.append({
                        'project_id': project['project_id'],
                        'project_name': project['project_name'],
                        'current_stage': project['current_stage'],
                        'status': project['status'],
                        'updated_at': project['updated_at']
                    })
        
        return sorted(projects, key=lambda x: x['updated_at'], reverse=True)
    
    def _save_project(self, project_id: str, project_state: Dict):
        """Save project state to file"""
        file_path = os.path.join(self.storage_dir, f"{project_id}.json")
        
        with open(file_path, 'w') as f:
            json.dump(project_state, f, indent=2)


# Example usage
if __name__ == "__main__":
    manager = ProjectStateManager()
    
    # Create a test project
    project_id = manager.create_project(
        "Cloud Storage Procurement",
        context={
            "company": "TechCorp",
            "department": "IT",
            "budget": 100000
        }
    )
    
    print(f"Created project: {project_id}")
    
    # Load it back
    project = manager.load_project(project_id)
    print(f"\nProject details:")
    print(json.dumps(project, indent=2))
