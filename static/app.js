// PROCBOT Web Application JavaScript

let currentProjectId = null;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadProjects();
    setupEventListeners();
});

function setupEventListeners() {
    // New Project Button
    document.getElementById('newProjectBtn').addEventListener('click', showNewProjectModal);
    document.getElementById('cancelProjectBtn').addEventListener('click', hideNewProjectModal);
    document.getElementById('createProjectBtn').addEventListener('click', createProject);
    
    // Send Message
    document.getElementById('sendBtn').addEventListener('click', sendMessage);
    document.getElementById('messageInput').addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
    
    // Menu Toggle (mobile)
    document.getElementById('menuToggle').addEventListener('click', toggleSidebar);
    
    // Auto-resize textarea
    document.getElementById('messageInput').addEventListener('input', autoResizeTextarea);
}

function autoResizeTextarea() {
    const textarea = document.getElementById('messageInput');
    textarea.style.height = 'auto';
    textarea.style.height = Math.min(textarea.scrollHeight, 200) + 'px';
}

function toggleSidebar() {
    document.getElementById('sidebar').classList.toggle('hidden');
}

function showNewProjectModal() {
    document.getElementById('newProjectModal').classList.remove('hidden');
    document.getElementById('projectNameInput').focus();
}

function hideNewProjectModal() {
    document.getElementById('newProjectModal').classList.add('hidden');
    document.getElementById('projectNameInput').value = '';
}

async function loadProjects() {
    try {
        const response = await fetch('/api/projects');
        const data = await response.json();
        
        if (data.success) {
            displayProjects(data.projects);
        }
    } catch (error) {
        console.error('Error loading projects:', error);
    }
}

function displayProjects(projects) {
    const projectsList = document.getElementById('projectsList');
    
    if (projects.length === 0) {
        projectsList.innerHTML = '<p class="text-sm text-gray-500 italic">No projects yet</p>';
        return;
    }
    
    projectsList.innerHTML = projects.map(project => `
        <div 
            class="project-item p-3 rounded-lg cursor-pointer hover:bg-gray-100 transition ${project.project_id === currentProjectId ? 'bg-blue-50 border border-blue-200' : 'bg-white border border-gray-200'}"
            onclick="selectProject('${project.project_id}')"
        >
            <div class="font-medium text-gray-800 text-sm truncate">${escapeHtml(project.project_name)}</div>
            <div class="text-xs text-gray-500 mt-1">${formatStage(project.current_stage)}</div>
        </div>
    `).join('');
}

function formatStage(stage) {
    const stages = {
        'business_case': 'Business Case',
        'rfi': 'RFI',
        'rfp': 'RFP',
        'evaluation': 'Evaluation',
        'summary': 'Executive Summary'
    };
    return stages[stage] || stage;
}

async function createProject() {
    const projectName = document.getElementById('projectNameInput').value.trim();
    
    if (!projectName) {
        alert('Please enter a project name');
        return;
    }
    
    try {
        const response = await fetch('/api/projects', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ project_name: projectName })
        });
        
        const data = await response.json();
        
        if (data.success) {
            hideNewProjectModal();
            await loadProjects();
            selectProject(data.project.project_id);
        } else {
            alert('Error creating project: ' + data.error);
        }
    } catch (error) {
        console.error('Error creating project:', error);
        alert('Error creating project');
    }
}

async function selectProject(projectId) {
    try {
        const response = await fetch(`/api/projects/${projectId}`);
        const data = await response.json();
        
        if (data.success) {
            currentProjectId = projectId;
            loadProjectView(data.project);
            await loadProjects(); // Refresh project list to update selection
        }
    } catch (error) {
        console.error('Error loading project:', error);
    }
}

function loadProjectView(project) {
    // Update header
    document.getElementById('currentProjectName').textContent = project.project_name;
    document.getElementById('currentProjectStage').textContent = `Stage: ${formatStage(project.current_stage)}`;
    
    // Hide welcome message
    const welcomeMsg = document.getElementById('welcomeMessage');
    if (welcomeMsg) {
        welcomeMsg.classList.add('hidden');
    }
    
    // Enable input
    document.getElementById('messageInput').disabled = false;
    document.getElementById('sendBtn').disabled = false;
    document.getElementById('messageInput').placeholder = 'Type your message here...';
    
    // Load conversation history
    const messagesContainer = document.getElementById('messagesContainer');
    messagesContainer.innerHTML = '';
    
    if (project.conversation_history && project.conversation_history.length > 0) {
        project.conversation_history.forEach(msg => {
            addMessage(msg.role, msg.content, false);
        });
    } else {
        addMessage('assistant', `Hi! I'm ready to help with "${project.project_name}". What would you like to work on?`, false);
    }
    
    scrollToBottom();
}

async function sendMessage() {
    const input = document.getElementById('messageInput');
    const message = input.value.trim();
    
    if (!message || !currentProjectId) return;
    
    // Add user message to UI
    addMessage('user', message);
    input.value = '';
    input.style.height = 'auto';
    
    // Show typing indicator
    showTypingIndicator();
    
    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message: message,
                project_id: currentProjectId
            })
        });
        
        const data = await response.json();
        
        hideTypingIndicator();
        
        if (data.success) {
            addMessage('assistant', data.response);
            
            // Update project stage if changed
            if (data.project) {
                document.getElementById('currentProjectStage').textContent = `Stage: ${formatStage(data.project.current_stage)}`;
            }
        } else {
            addMessage('assistant', 'Sorry, I encountered an error: ' + data.error);
        }
    } catch (error) {
        hideTypingIndicator();
        console.error('Error sending message:', error);
        addMessage('assistant', 'Sorry, I encountered a network error. Please try again.');
    }
}

function addMessage(role, content, animate = true) {
    const messagesContainer = document.getElementById('messagesContainer');
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `flex ${role === 'user' ? 'justify-end' : 'justify-start'} mb-4`;
    
    messageDiv.innerHTML = `
        <div class="max-w-3xl ${role === 'user' ? 'bg-blue-600 text-white' : 'bg-white border border-gray-200'} rounded-lg px-4 py-3 ${animate ? 'message' : ''}">
            <div class="text-sm ${role === 'user' ? '' : 'text-gray-800'} whitespace-pre-wrap">${escapeHtml(content)}</div>
        </div>
    `;
    
    messagesContainer.appendChild(messageDiv);
    scrollToBottom();
}

function showTypingIndicator() {
    const messagesContainer = document.getElementById('messagesContainer');
    const typingDiv = document.createElement('div');
    typingDiv.id = 'typingIndicator';
    typingDiv.className = 'flex justify-start mb-4';
    typingDiv.innerHTML = `
        <div class="bg-white border border-gray-200 rounded-lg px-4 py-3">
            <div class="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
            </div>
        </div>
    `;
    messagesContainer.appendChild(typingDiv);
    scrollToBottom();
}

function hideTypingIndicator() {
    const indicator = document.getElementById('typingIndicator');
    if (indicator) {
        indicator.remove();
    }
}

function scrollToBottom() {
    const container = document.getElementById('messagesContainer');
    container.scrollTop = container.scrollHeight;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
