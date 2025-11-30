"""
PROCBOT Web Application
Clean web UI for the procurement assistant
"""

from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
from agents.coordinator_agent import create_coordinator_agent
from utils.state_manager import ProjectStateManager
from utils.project_tools import ProjectTools
from dotenv import load_dotenv
import os
import uuid
from datetime import datetime

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')
CORS(app)

# Initialize components
coordinator = create_coordinator_agent()
state_manager = ProjectStateManager()
project_tools = ProjectTools()

@app.route('/')
def index():
    """Serve the main page"""
    return render_template('index.html')

@app.route('/api/projects', methods=['GET'])
def get_projects():
    """Get all projects"""
    try:
        projects = state_manager.list_projects()
        return jsonify({
            'success': True,
            'projects': projects
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/projects', methods=['POST'])
def create_project():
    """Create a new project"""
    try:
        data = request.json
        project_name = data.get('project_name')
        
        if not project_name:
            return jsonify({
                'success': False,
                'error': 'Project name is required'
            }), 400
        
        project_id = state_manager.create_project(project_name)
        project = state_manager.load_project(project_id)
        
        return jsonify({
            'success': True,
            'project': project
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/projects/<project_id>', methods=['GET'])
def get_project(project_id):
    """Get a specific project"""
    try:
        project = state_manager.load_project(project_id)
        if not project:
            return jsonify({
                'success': False,
                'error': 'Project not found'
            }), 404
        
        return jsonify({
            'success': True,
            'project': project
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages"""
    try:
        data = request.json
        message = data.get('message')
        project_id = data.get('project_id')
        
        if not message:
            return jsonify({
                'success': False,
                'error': 'Message is required'
            }), 400
        
        # Load project context if provided
        enriched_prompt = message
        current_project = None
        
        if project_id:
            current_project = state_manager.load_project(project_id)
            if current_project:
                # Save user message
                state_manager.add_message(
                    project_id,
                    'user',
                    message
                )
                
                # Build context
                context_info = f"\n\n[Current Project Context]"
                context_info += f"\nProject: {current_project['project_name']}"
                context_info += f"\nStage: {current_project['current_stage']}"
                
                if current_project['context']:
                    context_info += "\nKnown Details:"
                    for key, value in current_project['context'].items():
                        context_info += f"\n  - {key}: {value}"
                
                enriched_prompt = f"{message}{context_info}"
        
        # Get agent response
        response = coordinator.run(enriched_prompt)
        
        # Extract response text
        if hasattr(response, 'content'):
            response_text = response.content
        else:
            response_text = str(response)
        
        # Save agent response if we have a project
        if project_id and current_project:
            state_manager.add_message(
                project_id,
                'assistant',
                response_text,
                'coordinator'
            )
        
        return jsonify({
            'success': True,
            'response': response_text,
            'project': current_project
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    
    app.run(host='0.0.0.0', port=5000, debug=True)
