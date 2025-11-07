// Pre-Improvement JavaScript - Eager loading and poor UX
class TaskModalPre {
    constructor() {
        this.modal = document.getElementById('modalOverlay');
        this.createTaskBtn = document.getElementById('createTaskBtn');
        this.closeModal = document.getElementById('closeModal');
        this.cancelBtn = document.getElementById('cancelBtn');
        this.taskForm = document.getElementById('taskForm');
        this.loadingIndicator = document.getElementById('loadingIndicator');
        this.formContent = document.getElementById('formContent');
        this.submitBtn = document.getElementById('submitBtn');
        
        this.startTime = 0;
        this.loadTime = 0;
        this.isDataLoaded = false;
        
        this.initEventListeners();
        this.loadTestData();
    }
    
    initEventListeners() {
        this.createTaskBtn.addEventListener('click', () => this.openModal());
        this.closeModal.addEventListener('click', () => this.closeModalHandler());
        this.cancelBtn.addEventListener('click', () => this.closeModalHandler());
        this.taskForm.addEventListener('submit', (e) => this.handleSubmit(e));
        
        // Close modal when clicking overlay
        this.modal.addEventListener('click', (e) => {
            if (e.target === this.modal) {
                this.closeModalHandler();
            }
        });
        
        // ESC key support
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.modal.classList.contains('active')) {
                this.closeModalHandler();
            }
        });
    }
    
    async loadTestData() {
        try {
            const response = await fetch('/api/test-data');
            if (response.ok) {
                this.testData = await response.json();
            } else {
                // Fallback to local test data
                this.testData = {
                    available_assignees: [
                        {email: "john.doe@company.com", name: "John Doe", department: "Engineering"},
                        {email: "jane.smith@company.com", name: "Jane Smith", department: "Design"},
                        {email: "team.lead@company.com", name: "Alex Johnson", department: "Management"}
                    ],
                    available_tags: ["urgent", "documentation", "project", "coordination", "planning"],
                    priority_levels: ["low", "medium", "high", "critical"]
                };
            }
        } catch (error) {
            console.log('Using fallback test data');
            this.testData = {
                available_assignees: [
                    {email: "john.doe@company.com", name: "John Doe", department: "Engineering"},
                    {email: "jane.smith@company.com", name: "Jane Smith", department: "Design"},
                    {email: "team.lead@company.com", name: "Alex Johnson", department: "Management"}
                ],
                available_tags: ["urgent", "documentation", "project", "coordination", "planning"],
                priority_levels: ["low", "medium", "high", "critical"]
            };
        }
    }
    
    async openModal() {
        this.startTime = performance.now();
        
        // Show modal with loading state
        this.modal.classList.add('active');
        this.loadingIndicator.style.display = 'block';
        this.formContent.style.display = 'none';
        
        // Emit performance event
        window.dispatchEvent(new CustomEvent('modalOpened', {
            detail: { timestamp: this.startTime }
        }));
        
        // Simulate slow, eager loading of ALL data
        await this.loadAllDataEagerly();
        
        this.loadTime = performance.now() - this.startTime;
        console.log(`Modal loaded in ${this.loadTime}ms (Pre-improvement - eager loading)`);
        
        // Hide loading, show form
        this.loadingIndicator.style.display = 'none';
        this.formContent.style.display = 'block';
        
        // Emit load complete event
        window.dispatchEvent(new CustomEvent('modalLoadComplete', {
            detail: { 
                loadTime: this.loadTime,
                timestamp: performance.now()
            }
        }));
        
        // Focus on the LAST input (poor UX - title is buried at bottom)
        setTimeout(() => {
            const titleField = document.getElementById('title');
            if (titleField) {
                titleField.scrollIntoView({ behavior: 'smooth', block: 'center' });
                titleField.focus();
            }
        }, 100);
        
        this.isDataLoaded = true;
        this.submitBtn.disabled = false;
    }
    
    async loadAllDataEagerly() {
        // Simulate loading ALL data at once (poor performance)
        const loadPromises = [
            this.loadProjectCategories(),
            this.loadDepartments(),
            this.loadTags(),
            this.loadTeamMembers(),
            this.loadAttachmentOptions(),
            this.loadCustomFields()
        ];
        
        // Add artificial delays to simulate slow network
        const networkLatency = this.getNetworkLatency();
        await new Promise(resolve => setTimeout(resolve, networkLatency));
        
        await Promise.all(loadPromises);
    }
    
    getNetworkLatency() {
        // Check URL parameters for simulated network conditions
        const urlParams = new URLSearchParams(window.location.search);
        const latency = urlParams.get('network_latency_ms');
        return latency ? parseInt(latency) : 500; // Default to 500ms delay
    }
    
    async loadProjectCategories() {
        await this.simulateDelay(200);
        const select = document.getElementById('projectCategory');
        const categories = ['Development', 'Design', 'Marketing', 'Operations', 'Research'];
        
        categories.forEach(cat => {
            const option = document.createElement('option');
            option.value = cat.toLowerCase();
            option.textContent = cat;
            select.appendChild(option);
        });
    }
    
    async loadDepartments() {
        await this.simulateDelay(150);
        const select = document.getElementById('department');
        const departments = ['Engineering', 'Design', 'Product', 'Marketing', 'Sales', 'Support'];
        
        departments.forEach(dept => {
            const option = document.createElement('option');
            option.value = dept.toLowerCase();
            option.textContent = dept;
            select.appendChild(option);
        });
    }
    
    async loadTags() {
        await this.simulateDelay(300);
        const container = document.getElementById('tagsContainer');
        const tags = this.testData.available_tags;
        
        container.innerHTML = '';
        tags.forEach(tag => {
            const tagElement = document.createElement('span');
            tagElement.className = 'tag';
            tagElement.textContent = tag;
            tagElement.addEventListener('click', () => {
                tagElement.classList.toggle('selected');
            });
            container.appendChild(tagElement);
        });
    }
    
    async loadTeamMembers() {
        await this.simulateDelay(400);
        const assigneeSelect = document.getElementById('assignee');
        const watchersContainer = document.getElementById('watchersContainer');
        const members = this.testData.available_assignees;
        
        // Clear loading states
        assigneeSelect.innerHTML = '<option value="">Select assignee...</option>';
        watchersContainer.innerHTML = '';
        
        // Populate assignee dropdown
        members.forEach(member => {
            const option = document.createElement('option');
            option.value = member.email;
            option.textContent = `${member.name} (${member.department})`;
            assigneeSelect.appendChild(option);
        });
        
        // Populate watchers
        members.forEach(member => {
            const checkbox = document.createElement('label');
            checkbox.innerHTML = `
                <input type="checkbox" name="watchers" value="${member.email}">
                ${member.name} (${member.department})
            `;
            checkbox.style.display = 'block';
            checkbox.style.marginBottom = '8px';
            watchersContainer.appendChild(checkbox);
        });
    }
    
    async loadAttachmentOptions() {
        await this.simulateDelay(350);
        const container = document.getElementById('attachmentsContainer');
        
        container.innerHTML = `
            <input type="file" multiple style="margin-bottom: 10px;">
            <div style="font-size: 14px; color: #666;">
                <p>Supported formats: PDF, DOC, XLS, PNG, JPG</p>
                <p>Max file size: 10MB per file</p>
                <p>Max total size: 50MB</p>
            </div>
        `;
    }
    
    async loadCustomFields() {
        await this.simulateDelay(200);
        const container = document.getElementById('customFieldsContainer');
        
        container.innerHTML = `
            <div style="margin-bottom: 15px;">
                <label>Customer Impact:</label>
                <select style="width: 100%; padding: 8px; margin-top: 5px;">
                    <option value="">Select impact level...</option>
                    <option value="low">Low</option>
                    <option value="medium">Medium</option>
                    <option value="high">High</option>
                </select>
            </div>
            <div>
                <label>Sprint:</label>
                <input type="text" placeholder="Sprint name" style="width: 100%; padding: 8px; margin-top: 5px;">
            </div>
        `;
    }
    
    async simulateDelay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
    
    closeModalHandler() {
        this.modal.classList.remove('active');
        
        // Reset form
        this.taskForm.reset();
        this.isDataLoaded = false;
        this.submitBtn.disabled = true;
        
        // Reset form display
        this.loadingIndicator.style.display = 'block';
        this.formContent.style.display = 'none';
        
        // Clear any error states
        const errorGroups = document.querySelectorAll('.form-group.error');
        errorGroups.forEach(group => group.classList.remove('error'));
        
        const errorMessages = document.querySelectorAll('.error-message');
        errorMessages.forEach(msg => msg.remove());
    }
    
    async handleSubmit(e) {
        e.preventDefault();
        
        const formData = new FormData(this.taskForm);
        const taskData = Object.fromEntries(formData.entries());
        
        // Add selected tags
        const selectedTags = Array.from(document.querySelectorAll('.tag.selected'))
            .map(tag => tag.textContent);
        taskData.tags = selectedTags;
        
        // Add selected watchers
        const selectedWatchers = Array.from(document.querySelectorAll('input[name="watchers"]:checked'))
            .map(checkbox => checkbox.value);
        taskData.watchers = selectedWatchers;
        
        if (!this.validateForm(taskData)) {
            return;
        }
        
        // Show loading state
        this.submitBtn.disabled = true;
        this.submitBtn.textContent = 'Creating Task...';
        
        try {
            // Simulate API call
            await this.simulateDelay(1000);
            
            // Emit task creation event for testing
            window.dispatchEvent(new CustomEvent('taskCreated', {
                detail: { 
                    taskData,
                    creationTime: performance.now() - this.startTime
                }
            }));
            
            alert('Task created successfully!');
            this.closeModalHandler();
            
        } catch (error) {
            console.error('Error creating task:', error);
            alert('Error creating task. Please try again.');
        } finally {
            this.submitBtn.disabled = false;
            this.submitBtn.textContent = 'Create Task';
        }
    }
    
    validateForm(taskData) {
        let isValid = true;
        
        // Clear previous errors
        const errorGroups = document.querySelectorAll('.form-group.error');
        errorGroups.forEach(group => group.classList.remove('error'));
        
        const errorMessages = document.querySelectorAll('.error-message');
        errorMessages.forEach(msg => msg.remove());
        
        // Validate required fields
        const requiredFields = ['title', 'priority', 'dueDate'];
        
        requiredFields.forEach(field => {
            if (!taskData[field] || taskData[field].trim() === '') {
                this.showFieldError(field, 'This field is required');
                isValid = false;
            }
        });
        
        // Validate email format for assignee
        if (taskData.assignee && !this.isValidEmail(taskData.assignee)) {
            this.showFieldError('assignee', 'Please select a valid assignee');
            isValid = false;
        }
        
        // Validate date
        if (taskData.dueDate) {
            const dueDate = new Date(taskData.dueDate);
            const today = new Date();
            today.setHours(0, 0, 0, 0);
            
            if (dueDate < today) {
                this.showFieldError('dueDate', 'Due date cannot be in the past');
                isValid = false;
            }
        }
        
        return isValid;
    }
    
    showFieldError(fieldName, message) {
        const field = document.getElementById(fieldName);
        if (!field) return;
        
        const formGroup = field.closest('.form-group');
        formGroup.classList.add('error');
        
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        errorDiv.textContent = message;
        formGroup.appendChild(errorDiv);
        
        // Scroll to first error
        if (document.querySelectorAll('.form-group.error').length === 1) {
            field.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
    }
    
    isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }
}

// Performance monitoring
class PerformanceMonitor {
    constructor() {
        this.metrics = {};
        this.events = [];
        this.setupEventListeners();
    }
    
    setupEventListeners() {
        window.addEventListener('modalOpened', (e) => {
            this.metrics.modalOpenedAt = e.detail.timestamp;
        });
        
        window.addEventListener('modalLoadComplete', (e) => {
            this.metrics.modalLoadTime = e.detail.loadTime;
            this.metrics.modalLoadedAt = e.detail.timestamp;
        });
        
        window.addEventListener('taskCreated', (e) => {
            this.metrics.taskCreationTime = e.detail.creationTime;
            this.metrics.taskData = e.detail.taskData;
        });
    }
    
    getMetrics() {
        return {
            ...this.metrics,
            events: this.events,
            performance: {
                modalLoadTime: this.metrics.modalLoadTime,
                timeToTitleVisible: this.calculateTimeToTitleVisible(),
                totalTaskCreationTime: this.metrics.taskCreationTime
            }
        };
    }
    
    calculateTimeToTitleVisible() {
        // In pre-improvement version, title is at bottom, so it's not immediately visible
        return this.metrics.modalLoadTime + 2000; // Additional time to scroll to title
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.taskModal = new TaskModalPre();
    window.performanceMonitor = new PerformanceMonitor();
    
    // Expose metrics for testing
    window.getPerformanceMetrics = () => window.performanceMonitor.getMetrics();
});