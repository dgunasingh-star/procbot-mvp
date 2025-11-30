"""
Project State Management
Handles creation, loading, and persistence of procurement projects
"""

import json
import os
from datetime import datetime
from pathlib import Path

class ProjectTools:
    """Manages project state and persistence"""
    
    def __init__(self, state_dir="project_states"):
        self.state_dir = Path(state_dir)
        self.state_dir.mkdir(exist_ok=True)
        self.current_project = None
    
    def create_new_project(self, project_name: str, context: dict = None) -> str:
        """Create a new procurement project"""
        
        project_id = f"proj_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        project_state = {
            "project_id": project_id,
            "project_name": project_name,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "current_stage": "business_case",
            "status": "active",
            "context": context or {},
            "conversation_history": [],
            "stage_outputs": {},
            "decisions": [],
            "next_actions": []
        }
        
        self.current_project = project_state
        self._save_to_file(project_state)
        
        return f"✅ Created new project: {project_name}\n📋 Project ID: {project_id}\n📍 Stage: Business Case\n🟢 Status: Active"
    
    def load_existing_project(self, project_id: str) -> str:
        """Load an existing project by ID"""
        
        project_file = self.state_dir / f"{project_id}.json"
        
        if not project_file.exists():
            return f"❌ Project {project_id} not found."
        
        with open(project_file, 'r') as f:
            project_state = json.load(f)
        
        self.current_project = project_state
        
        return f"✅ Loaded project: {project_state['project_name']}\n📋 ID: {project_id}\n📍 Stage: {project_state['current_stage']}\n🟢 Status: {project_state['status']}"
    
    def list_all_projects(self) -> str:
        """List all projects in the system"""
        
        project_files = list(self.state_dir.glob("*.json"))
        
        if not project_files:
            return "No projects found. Create a new project to get started!"
        
        projects = []
        for file in project_files:
            with open(file, 'r') as f:
                project = json.load(f)
                projects.append(project)
        
        # Sort by updated_at
        projects.sort(key=lambda x: x['updated_at'], reverse=True)
        
        output = "## Your Projects\n\n"
        
        for i, proj in enumerate(projects, 1):
            status_emoji = "🟢" if proj['status'] == 'active' else "⏸️" if proj['status'] == 'on_hold' else "🔴" if proj['status'] == 'cancelled' else "✅"
            output += f"{i}. **{status_emoji} {proj['project_name']}**\n"
            output += f"   - **ID:** {proj['project_id']}\n"
            output += f"   - **Stage:** {proj['current_stage'].replace('_', ' ').title()}\n"
            output += f"   - **Last Updated:** {proj['updated_at'][:10]}\n\n"
        
        active_count = sum(1 for p in projects if p['status'] == 'active')
        output += f"All {len(projects)} project(s) currently in the system"
        if active_count < len(projects):
            output += f", {active_count} active"
        output += "."
        
        return output
    
    def get_project_status(self, project_id: str = None) -> str:
        """Get detailed status of a project"""
        
        if not self.current_project:
            return "No project currently loaded. Use load_project() first."
        
        proj = self.current_project
        
        output = f"# Project Status\n\n"
        output += f"**Project:** {proj['project_name']}\n"
        output += f"**ID:** {proj['project_id']}\n"
        output += f"**Current Stage:** {proj['current_stage'].replace('_', ' ').title()}\n"
        output += f"**Status:** {proj['status'].replace('_', ' ').title()}\n"
        output += f"**Created:** {proj['created_at'][:10]}\n"
        output += f"**Last Updated:** {proj['updated_at'][:10]}\n\n"
        
        if proj.get('context'):
            output += "## Context\n"
            for key, value in proj['context'].items():
                output += f"- **{key.title()}:** {value}\n"
            output += "\n"
        
        if proj.get('decisions'):
            output += f"## Recent Decisions ({len(proj['decisions'])})\n"
            for decision in proj['decisions'][-3:]:
                output += f"- {decision.get('action', 'Unknown')}"
                if decision.get('reason'):
                    output += f": {decision['reason']}"
                output += f" ({decision.get('timestamp', '')[:10]})\n"
        
        return output
    
    def add_project_context(self, key: str, value: str) -> str:
        """Add context metadata to current project"""
        
        if not self.current_project:
            return "No project currently loaded."
        
        self.current_project['context'][key] = value
        self.current_project['updated_at'] = datetime.now().isoformat()
        self._save_to_file(self.current_project)
        
        return f"✅ Added {key} = {value} to project context"
    
    def get_current_project(self) -> dict:
        """Get the current project state"""
        return self.current_project
    
    def save_conversation(self, role: str, message: str, agent: str = None):
        """Save conversation to project history"""
        
        if not self.current_project:
            return
        
        entry = {
            "timestamp": datetime.now().isoformat(),
            "role": role,
            "message": message
        }
        
        if agent:
            entry["agent"] = agent
        
        self.current_project['conversation_history'].append(entry)
        self._save_to_file(self.current_project)
    
    def save_project_state(self, project_state: dict):
        """Save project state (used by workflow manager)"""
        project_state['updated_at'] = datetime.now().isoformat()
        self.current_project = project_state
        self._save_to_file(project_state)
    
    def manage_workflow(self, action: str, reason: str = "", target_stage: str = "") -> str:
        """
        Comprehensive project lifecycle management.
        
        Actions supported:
        - cancel: Permanently mark project as cancelled
        - pause: Temporarily put project on hold
        - resume: Reactivate a paused project
        - complete: Mark project as successfully finished
        - advance: Move to next procurement stage
        - revert: Go back to previous stage
        - jump_to: Go to a specific stage
        """
        
        if not self.current_project:
            return "No active project to manage. Please load or create a project first."
        
        project_id = self.current_project['project_id']
        project_name = self.current_project['project_name']
        
        # STATUS CHANGES
        if action == "cancel":
            if not reason:
                return "Please provide a reason for cancellation."
            
            self.current_project['status'] = 'cancelled'
            self.current_project['cancellation_reason'] = reason
            self.current_project['cancelled_at'] = datetime.now().isoformat()
            
            self.current_project['decisions'].append({
                'timestamp': datetime.now().isoformat(),
                'action': 'cancel',
                'reason': reason
            })
            
            self.save_project_state(self.current_project)
            
            return f"✅ Project '{project_name}' has been cancelled.\n\n**Reason:** {reason}\n\nThe project has been archived and marked as cancelled. All project data has been preserved for future reference."
        
        elif action == "pause":
            if not reason:
                return "Please provide a reason for pausing the project."
            
            self.current_project['status'] = 'on_hold'
            self.current_project['hold_reason'] = reason
            self.current_project['paused_at'] = datetime.now().isoformat()
            
            self.current_project['decisions'].append({
                'timestamp': datetime.now().isoformat(),
                'action': 'pause',
                'reason': reason
            })
            
            self.save_project_state(self.current_project)
            
            return f"⏸️ Project '{project_name}' has been put on hold.\n\n**Reason:** {reason}\n\nYou can resume this project anytime by asking me to resume it."
        
        elif action == "resume":
            if self.current_project['status'] != 'on_hold':
                return f"Cannot resume: Project is currently {self.current_project['status']}, not on hold. Only paused projects can be resumed."
            
            self.current_project['status'] = 'active'
            self.current_project['resumed_at'] = datetime.now().isoformat()
            
            self.current_project['decisions'].append({
                'timestamp': datetime.now().isoformat(),
                'action': 'resume'
            })
            
            self.save_project_state(self.current_project)
            
            return f"▶️ Project '{project_name}' has been resumed and is now active again!\n\nWe can continue from where we left off in the {self.current_project['current_stage'].replace('_', ' ')} stage."
        
        elif action == "complete":
            self.current_project['status'] = 'completed'
            self.current_project['completed_at'] = datetime.now().isoformat()
            
            self.current_project['decisions'].append({
                'timestamp': datetime.now().isoformat(),
                'action': 'complete'
            })
            
            self.save_project_state(self.current_project)
            
            return f"🎉 Congratulations! Project '{project_name}' has been marked as completed!\n\nAll project data has been saved and the project is now in completed status."
        
        # STAGE TRANSITIONS
        elif action == "advance":
            stage_flow = [
                'business_case',
                'market_research',
                'rfi_rfp',
                'evaluation',
                'summary'
            ]
            
            stage_names = {
                'business_case': 'Business Case',
                'market_research': 'Market Research',
                'rfi_rfp': 'RFI/RFP Development',
                'evaluation': 'Vendor Evaluation',
                'summary': 'Executive Summary'
            }
            
            current_stage = self.current_project['current_stage']
            
            if current_stage not in stage_flow:
                return f"Unknown current stage: {current_stage}"
            
            current_index = stage_flow.index(current_stage)
            
            if current_index >= len(stage_flow) - 1:
                return "Project is already at the final stage (Executive Summary). Consider marking the project as complete instead."
            
            next_stage = stage_flow[current_index + 1]
            self.current_project['current_stage'] = next_stage
            
            self.current_project['decisions'].append({
                'timestamp': datetime.now().isoformat(),
                'action': 'advance',
                'from_stage': current_stage,
                'to_stage': next_stage
            })
            
            self.save_project_state(self.current_project)
            
            return f"➡️ Advanced to the next stage!\n\n**From:** {stage_names[current_stage]}\n**To:** {stage_names[next_stage]}\n\nThe project is now in the {stage_names[next_stage]} phase."
        
        elif action == "revert":
            stage_flow = [
                'business_case',
                'market_research',
                'rfi_rfp',
                'evaluation',
                'summary'
            ]
            
            stage_names = {
                'business_case': 'Business Case',
                'market_research': 'Market Research',
                'rfi_rfp': 'RFI/RFP Development',
                'evaluation': 'Vendor Evaluation',
                'summary': 'Executive Summary'
            }
            
            current_stage = self.current_project['current_stage']
            current_index = stage_flow.index(current_stage)
            
            if current_index <= 0:
                return "Already at the first stage (Business Case). Cannot go back further."
            
            previous_stage = stage_flow[current_index - 1]
            self.current_project['current_stage'] = previous_stage
            
            self.current_project['decisions'].append({
                'timestamp': datetime.now().isoformat(),
                'action': 'revert',
                'from_stage': current_stage,
                'to_stage': previous_stage
            })
            
            self.save_project_state(self.current_project)
            
            return f"⬅️ Reverted to previous stage.\n\n**From:** {stage_names[current_stage]}\n**Back to:** {stage_names[previous_stage]}\n\nYou can now work on the {stage_names[previous_stage]} phase."
        
        elif action == "jump_to":
            if not target_stage:
                return "Please specify which stage to jump to."
            
            valid_stages = ['business_case', 'market_research', 'rfi_rfp', 'evaluation', 'summary']
            
            stage_names = {
                'business_case': 'Business Case',
                'market_research': 'Market Research',
                'rfi_rfp': 'RFI/RFP Development',
                'evaluation': 'Vendor Evaluation',
                'summary': 'Executive Summary'
            }
            
            if target_stage not in valid_stages:
                return f"Invalid stage: {target_stage}. Valid stages are: business_case, market_research, rfi_rfp, evaluation, summary"
            
            old_stage = self.current_project['current_stage']
            self.current_project['current_stage'] = target_stage
            
            self.current_project['decisions'].append({
                'timestamp': datetime.now().isoformat(),
                'action': 'jump_to',
                'from_stage': old_stage,
                'to_stage': target_stage
            })
            
            self.save_project_state(self.current_project)
            
            return f"�� Jumped to {stage_names[target_stage]}!\n\n**From:** {stage_names[old_stage]}\n**To:** {stage_names[target_stage]}\n\nThe project is now in the {stage_names[target_stage]} phase."
        
        else:
            return f"Unknown action: {action}\n\nValid actions are: cancel, pause, resume, complete, advance, revert, jump_to"
    
    def _save_to_file(self, project_state: dict):
        """Save project state to JSON file"""
        project_file = self.state_dir / f"{project_state['project_id']}.json"
        with open(project_file, 'w') as f:
            json.dump(project_state, f, indent=2)
