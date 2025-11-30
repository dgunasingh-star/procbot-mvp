"""
Project State Manager
Handles project creation, loading, and state persistence
"""

import json
import os
from datetime import datetime
from pathlib import Path
import uuid

class ProjectStateManager:
    """Manages project state and persistence"""
    
    def __init__(self, data_dir: str = "data/projects"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.current_project_file = self.data_dir / "current_project.json"
    
    def create_project(self, project_name: str) -> str:
        """Create a new project"""
        project_id = str(uuid.uuid4())[:8]
        
        project_data = {
            "project_id": project_id,
            "project_name": project_name,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "current_stage": "business_case",
            "context": {},
            "conversation_history": [],
            "decisions": []
        }
        
        # Save project
        self._save_project(project_id, project_data)
        
        # Set as current project
        self._set_current_project(project_id)
        
        return project_id
    
    def load_project(self, project_id: str) -> dict:
        """Load a project by ID"""
        project_file = self.data_dir / f"{project_id}.json"
        
        if not project_file.exists():
            return None
        
        with open(project_file, 'r') as f:
            project_data = json.load(f)
        
        # Set as current project
        self._set_current_project(project_id)
        
        return project_data
    
    def get_current_project(self) -> dict:
        """Get the currently active project"""
        if not self.current_project_file.exists():
            return None
        
        with open(self.current_project_file, 'r') as f:
            data = json.load(f)
        
        current_id = data.get('current_project_id')
        if not current_id:
            return None
        
        return self.load_project(current_id)
    
    def list_projects(self) -> list:
        """List all projects"""
        projects = []
        
        for project_file in self.data_dir.glob("*.json"):
            if project_file.name == "current_project.json":
                continue
            
            with open(project_file, 'r') as f:
                project_data = json.load(f)
                projects.append({
                    "project_id": project_data["project_id"],
                    "project_name": project_data["project_name"],
                    "current_stage": project_data["current_stage"],
                    "updated_at": project_data["updated_at"]
                })
        
        # Sort by updated_at descending
        projects.sort(key=lambda x: x["updated_at"], reverse=True)
        
        return projects
    
    def add_message(self, project_id: str, role: str, content: str, agent_name: str = None):
        """Add a message to project conversation history"""
        project = self.load_project(project_id)
        if not project:
            raise ValueError(f"Project {project_id} not found")
        
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }
        
        if agent_name:
            message["agent"] = agent_name
        
        project["conversation_history"].append(message)
        project["updated_at"] = datetime.now().isoformat()
        
        self._save_project(project_id, project)
    
    def update_context(self, project_id: str, context_updates: dict):
        """Update project context"""
        project = self.load_project(project_id)
        if not project:
            raise ValueError(f"Project {project_id} not found")
        
        project["context"].update(context_updates)
        project["updated_at"] = datetime.now().isoformat()
        
        self._save_project(project_id, project)
    
    def update_stage(self, project_id: str, new_stage: str):
        """Update project stage"""
        project = self.load_project(project_id)
        if not project:
            raise ValueError(f"Project {project_id} not found")
        
        project["current_stage"] = new_stage
        project["updated_at"] = datetime.now().isoformat()
        
        self._save_project(project_id, project)
    
    def add_decision(self, project_id: str, decision: dict):
        """Add a decision to project history"""
        project = self.load_project(project_id)
        if not project:
            raise ValueError(f"Project {project_id} not found")
        
        decision["timestamp"] = datetime.now().isoformat()
        project["decisions"].append(decision)
        project["updated_at"] = datetime.now().isoformat()
        
        self._save_project(project_id, project)
    
    def _save_project(self, project_id: str, project_data: dict):
        """Save project to file"""
        project_file = self.data_dir / f"{project_id}.json"
        
        with open(project_file, 'w') as f:
            json.dump(project_data, f, indent=2)
    
    def _set_current_project(self, project_id: str):
        """Set the current active project"""
        with open(self.current_project_file, 'w') as f:
            json.dump({"current_project_id": project_id}, f)
