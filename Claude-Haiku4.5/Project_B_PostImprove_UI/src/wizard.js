// Post-Improvement JavaScript - Wizard with lazy loading and optimized UX
class TaskWizard {
    constructor() {
        this.modal = document.getElementById('modalOverlay');
        this.createTaskBtn = document.getElementById('createTaskBtn');
        this.closeModal = document.getElementById('closeModal');
        this.cancelBtn = document.getElementById('cancelBtn');
        this.prevBtn = document.getElementById('prevBtn');
        this.nextBtn = document.getElementById('nextBtn');
        this.submitBtn = document.getElementById('submitBtn');
        this.taskForm = document.getElementById('taskForm');
        
        this.currentStep = 1;
        this.totalSteps = 3;
        this.startTime = 0;
        this.stepLoadTimes = {};
        this.lazyLoadedData = {};
        
        this.initEventListeners();
        this.loadTestData();
    }
    
    initEventListeners() {
        this.createTaskBtn.addEventListener('click', () => this.openWizard());
        this.closeModal.addEventListener('click', () => this.closeWizard());
        this.cancelBtn.addEventListener('click', () => this.closeWizard());
        this.prevBtn.addEventListener('click', () => this.previousStep());
        this.nextBtn.addEventListener('click', () => this.nextStep());
        this.taskForm.addEventListener('submit', (e) => this.handleSubmit(e));
        
        // File upload handling
        this.setupFileUpload();
        
        // Custom tag handling
        this.setupCustomTags();
        
        // Real-time validation
        this.setupValidation();
        
        // Close modal when clicking overlay
        this.modal.addEventListener('click', (e) => {
            if (e.target === this.modal) {
                this.closeWizard();
            }
        });
        
        // ESC key support
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.modal.classList.contains('active')) {
                this.closeWizard();
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
    
    async openWizard() {
        this.startTime = performance.now();
        
        // Show modal immediately with first step (no loading delay)
        this.modal.classList.add('active');
        this.currentStep = 1;
        this.showStep(1);
        
        // Emit performance event
        window.dispatchEvent(new CustomEvent('modalOpened', {
            detail: { timestamp: this.startTime }
        }));
        
        // Focus on first input immediately (improved UX)
        setTimeout(() => {
            const titleField = document.getElementById('title');
            if (titleField) {
                titleField.focus();
                
                // Emit title visible event
                window.dispatchEvent(new CustomEvent('titleVisible', {
                    detail: { 
                        timestamp: performance.now(),
                        timeToVisible: performance.now() - this.startTime
                    }
                }));
            }
        }, 100);
        
        // Pre-load next step data in background
        setTimeout(() => this.preloadStep2Data(), 500);
        
        const loadTime = performance.now() - this.startTime;
        console.log(`Wizard opened in ${loadTime}ms (Post-improvement - instant load)`);
        
        // Emit load complete event
        window.dispatchEvent(new CustomEvent('modalLoadComplete', {
            detail: { 
                loadTime: loadTime,
                timestamp: performance.now()
            }
        }));
    }
    
    showStep(stepNumber) {
        // Hide all steps
        document.querySelectorAll('.wizard-step').forEach(step => {
            step.classList.remove('active');
        });
        
        // Show current step
        document.getElementById(`step${stepNumber}`).classList.add('active');
        
        // Update progress indicators
        document.querySelectorAll('.step').forEach((step, index) => {
            const stepNum = index + 1;
            if (stepNum < stepNumber) {
                step.classList.remove('active');
                step.classList.add('completed');
            } else if (stepNum === stepNumber) {
                step.classList.remove('completed');
                step.classList.add('active');
            } else {
                step.classList.remove('active', 'completed');
            }
        });
        
        // Update button states
        this.prevBtn.disabled = stepNumber === 1;
        
        if (stepNumber === this.totalSteps) {
            this.nextBtn.style.display = 'none';
            this.submitBtn.style.display = 'block';
        } else {
            this.nextBtn.style.display = 'block';
            this.submitBtn.style.display = 'none';
        }
        
        this.currentStep = stepNumber;
    }
    
    async nextStep() {
        // Validate current step
        if (!this.validateCurrentStep()) {
            return;
        }
        
        const nextStepNum = this.currentStep + 1;
        if (nextStepNum <= this.totalSteps) {
            // Load data for next step if needed
            await this.loadStepData(nextStepNum);
            this.showStep(nextStepNum);
        }
    }
    
    previousStep() {
        const prevStepNum = this.currentStep - 1;
        if (prevStepNum >= 1) {
            this.showStep(prevStepNum);
        }
    }
    
    async loadStepData(stepNumber) {
        if (stepNumber === 2 && !this.lazyLoadedData.step2) {
            await this.loadStep2Data();
        } else if (stepNumber === 3 && !this.lazyLoadedData.step3) {
            await this.loadStep3Data();
        }
    }
    
    async preloadStep2Data() {
        // Preload step 2 data in background for better perceived performance
        if (!this.lazyLoadedData.step2) {
            this.loadStep2Data();
        }
    }
    
    async loadStep2Data() {
        if (this.lazyLoadedData.step2) return;
        
        const loadingElement = document.getElementById('assignmentLoading');
        const contentElement = document.getElementById('assignmentContent');
        
        try {
            const startTime = performance.now();
            
            // Simulate minimal network delay
            const networkLatency = this.getNetworkLatency();
            if (networkLatency > 50) {
                await new Promise(resolve => setTimeout(resolve, Math.min(networkLatency, 200)));
            }
            
            // Load team members
            await this.loadTeamMembers();
            
            // Load departments
            await this.loadDepartments();
            
            const loadTime = performance.now() - startTime;
            this.stepLoadTimes.step2 = loadTime;
            
            // Hide loading, show content
            loadingElement.style.display = 'none';
            contentElement.style.display = 'block';
            
            this.lazyLoadedData.step2 = true;
            console.log(`Step 2 data loaded in ${loadTime}ms (lazy loading)`);
            
        } catch (error) {
            console.error('Error loading step 2 data:', error);
            loadingElement.innerHTML = '<span style="color: #e74c3c;">Error loading data. Please try again.</span>';
        }
    }
    
    async loadStep3Data() {
        if (this.lazyLoadedData.step3) return;
        
        const loadingElement = document.getElementById('additionalLoading');
        const contentElement = document.getElementById('additionalContent');
        
        try {
            const startTime = performance.now();
            
            // Simulate minimal network delay
            const networkLatency = this.getNetworkLatency();
            if (networkLatency > 50) {
                await new Promise(resolve => setTimeout(resolve, Math.min(networkLatency, 150)));
            }
            
            // Load tags
            await this.loadTags();
            
            // Load project categories
            await this.loadProjectCategories();
            
            const loadTime = performance.now() - startTime;
            this.stepLoadTimes.step3 = loadTime;
            
            // Hide loading, show content
            loadingElement.style.display = 'none';
            contentElement.style.display = 'block';
            
            this.lazyLoadedData.step3 = true;
            console.log(`Step 3 data loaded in ${loadTime}ms (lazy loading)`);
            
        } catch (error) {
            console.error('Error loading step 3 data:', error);
            loadingElement.innerHTML = '<span style="color: #e74c3c;">Error loading data. Please try again.</span>';
        }
    }
    
    getNetworkLatency() {
        // Check URL parameters for simulated network conditions
        const urlParams = new URLSearchParams(window.location.search);
        const latency = urlParams.get('network_latency_ms');
        return latency ? parseInt(latency) : 50; // Default to 50ms delay
    }
    
    async loadTeamMembers() {
        const assigneeSelect = document.getElementById('assignee');
        const watchersContainer = document.getElementById('watchersContainer');
        const members = this.testData.available_assignees;
        
        // Clear existing content
        assigneeSelect.innerHTML = '<option value="">Select assignee...</option>';
        watchersContainer.innerHTML = '';
        
        // Populate assignee dropdown
        members.forEach(member => {
            const option = document.createElement('option');
            option.value = member.email;
            option.textContent = `${member.name} (${member.department})`;
            assigneeSelect.appendChild(option);
        });
        
        // Populate watchers with improved UI
        members.forEach(member => {
            const watcherDiv = document.createElement('div');
            watcherDiv.className = 'watcher-item';
            watcherDiv.innerHTML = `
                <input type="checkbox" id="watcher_${member.email}" name="watchers" value="${member.email}">
                <label for="watcher_${member.email}">${member.name} (${member.department})</label>
            `;
            watchersContainer.appendChild(watcherDiv);
        });
    }
    
    async loadDepartments() {
        const select = document.getElementById('department');
        const departments = ['Engineering', 'Design', 'Product', 'Marketing', 'Sales', 'Support'];
        
        select.innerHTML = '<option value="">Select department...</option>';
        departments.forEach(dept => {
            const option = document.createElement('option');
            option.value = dept.toLowerCase();
            option.textContent = dept;
            select.appendChild(option);
        });
    }
    
    async loadTags() {
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
    
    async loadProjectCategories() {
        const select = document.getElementById('projectCategory');
        const categories = ['Development', 'Design', 'Marketing', 'Operations', 'Research'];
        
        select.innerHTML = '<option value="">Select a category...</option>';
        categories.forEach(cat => {
            const option = document.createElement('option');
            option.value = cat.toLowerCase();
            option.textContent = cat;
            select.appendChild(option);
        });
    }
    
    setupFileUpload() {
        const fileUploadZone = document.getElementById('fileUploadZone');
        const fileInput = document.getElementById('attachments');
        const selectedFilesDiv = document.getElementById('selectedFiles');
        
        fileUploadZone.addEventListener('click', () => {
            fileInput.click();
        });
        
        fileUploadZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            fileUploadZone.style.borderColor = '#3498db';
        });
        
        fileUploadZone.addEventListener('dragleave', () => {
            fileUploadZone.style.borderColor = '#ddd';
        });
        
        fileUploadZone.addEventListener('drop', (e) => {
            e.preventDefault();
            fileUploadZone.style.borderColor = '#ddd';
            
            const files = Array.from(e.dataTransfer.files);
            this.handleFileSelection(files, selectedFilesDiv);
        });
        
        fileInput.addEventListener('change', (e) => {
            const files = Array.from(e.target.files);
            this.handleFileSelection(files, selectedFilesDiv);
        });
    }
    
    handleFileSelection(files, container) {
        container.innerHTML = '';
        
        files.forEach(file => {
            const fileDiv = document.createElement('div');
            fileDiv.className = 'file-item';
            fileDiv.innerHTML = `
                <span>${file.name} (${this.formatFileSize(file.size)})</span>
                <button type="button" onclick="this.parentElement.remove()">Remove</button>
            `;
            container.appendChild(fileDiv);
        });
    }
    
    formatFileSize(bytes) {
        if (bytes === 0) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
    }
    
    setupCustomTags() {
        const customTagInput = document.getElementById('customTag');
        const addTagBtn = document.getElementById('addTagBtn');
        const tagsContainer = document.getElementById('tagsContainer');
        
        const addCustomTag = () => {
            const tagText = customTagInput.value.trim();
            if (tagText && !this.tagExists(tagText)) {
                const tagElement = document.createElement('span');
                tagElement.className = 'tag selected';
                tagElement.textContent = tagText;
                tagElement.addEventListener('click', () => {
                    tagElement.classList.toggle('selected');
                });
                tagsContainer.appendChild(tagElement);
                customTagInput.value = '';
            }
        };
        
        addTagBtn.addEventListener('click', addCustomTag);
        customTagInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                addCustomTag();
            }
        });
    }
    
    tagExists(tagText) {
        const existingTags = document.querySelectorAll('#tagsContainer .tag');
        return Array.from(existingTags).some(tag => tag.textContent === tagText);
    }
    
    setupValidation() {
        // Real-time validation for better UX
        const titleField = document.getElementById('title');
        const dueDateField = document.getElementById('dueDate');
        const priorityField = document.getElementById('priority');
        
        [titleField, dueDateField, priorityField].forEach(field => {
            if (field) {
                field.addEventListener('blur', () => this.validateField(field));
                field.addEventListener('input', () => this.clearFieldError(field));
            }
        });
    }
    
    validateCurrentStep() {
        const currentStepElement = document.getElementById(`step${this.currentStep}`);
        const requiredFields = currentStepElement.querySelectorAll('[required]');
        
        let isValid = true;
        
        requiredFields.forEach(field => {
            if (!this.validateField(field)) {
                isValid = false;
            }
        });
        
        return isValid;
    }
    
    validateField(field) {
        const value = field.value.trim();
        const fieldType = field.type;
        let isValid = true;
        let errorMessage = '';
        
        // Check required fields
        if (field.hasAttribute('required') && !value) {
            isValid = false;
            errorMessage = 'This field is required';
        }
        
        // Validate date
        if (fieldType === 'date' && value) {
            const dueDate = new Date(value);
            const today = new Date();
            today.setHours(0, 0, 0, 0);
            
            if (dueDate < today) {
                isValid = false;
                errorMessage = 'Due date cannot be in the past';
            }
        }
        
        // Validate email
        if (fieldType === 'email' && value) {
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(value)) {
                isValid = false;
                errorMessage = 'Please enter a valid email address';
            }
        }
        
        if (isValid) {
            this.clearFieldError(field);
            this.showFieldSuccess(field);
        } else {
            this.showFieldError(field, errorMessage);
        }
        
        return isValid;
    }
    
    showFieldError(field, message) {
        const formGroup = field.closest('.form-group');
        formGroup.classList.remove('success');
        formGroup.classList.add('error');
        
        // Remove existing error message
        const existingError = formGroup.querySelector('.error-message');
        if (existingError) {
            existingError.remove();
        }
        
        // Add new error message
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        errorDiv.textContent = message;
        formGroup.appendChild(errorDiv);
    }
    
    showFieldSuccess(field) {
        const formGroup = field.closest('.form-group');
        formGroup.classList.remove('error');
        formGroup.classList.add('success');
        
        // Remove error message
        const existingError = formGroup.querySelector('.error-message');
        if (existingError) {
            existingError.remove();
        }
    }
    
    clearFieldError(field) {
        const formGroup = field.closest('.form-group');
        formGroup.classList.remove('error', 'success');
        
        const existingError = formGroup.querySelector('.error-message');
        if (existingError) {
            existingError.remove();
        }
    }
    
    closeWizard() {
        this.modal.classList.remove('active');
        
        // Reset wizard state
        this.currentStep = 1;
        this.showStep(1);
        this.taskForm.reset();
        this.lazyLoadedData = {};
        
        // Reset lazy loading states
        document.getElementById('assignmentLoading').style.display = 'flex';
        document.getElementById('assignmentContent').style.display = 'none';
        document.getElementById('additionalLoading').style.display = 'flex';
        document.getElementById('additionalContent').style.display = 'none';
        
        // Clear any error states
        const errorGroups = document.querySelectorAll('.form-group.error, .form-group.success');
        errorGroups.forEach(group => {
            group.classList.remove('error', 'success');
        });
        
        const errorMessages = document.querySelectorAll('.error-message');
        errorMessages.forEach(msg => msg.remove());
        
        // Clear file selections
        document.getElementById('selectedFiles').innerHTML = '';
        
        // Reset tags
        const tags = document.querySelectorAll('.tag.selected');
        tags.forEach(tag => tag.classList.remove('selected'));
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
        
        // Final validation
        if (!this.validateCurrentStep()) {
            return;
        }
        
        // Show loading state
        this.submitBtn.disabled = true;
        this.submitBtn.textContent = 'Creating Task...';
        
        try {
            // Simulate API call
            await new Promise(resolve => setTimeout(resolve, 500)); // Faster than pre-improvement
            
            // Emit task creation event for testing
            window.dispatchEvent(new CustomEvent('taskCreated', {
                detail: { 
                    taskData,
                    creationTime: performance.now() - this.startTime,
                    stepLoadTimes: this.stepLoadTimes
                }
            }));
            
            // Success animation/feedback
            this.submitBtn.textContent = '✓ Task Created!';
            this.submitBtn.style.background = '#27ae60';
            
            setTimeout(() => {
                alert('Task created successfully!');
                this.closeWizard();
            }, 1000);
            
        } catch (error) {
            console.error('Error creating task:', error);
            alert('Error creating task. Please try again.');
        } finally {
            setTimeout(() => {
                this.submitBtn.disabled = false;
                this.submitBtn.textContent = 'Create Task';
                this.submitBtn.style.background = '';
            }, 1500);
        }
    }
}

// Performance monitoring for improved version
class ImprovedPerformanceMonitor {
    constructor() {
        this.metrics = {};
        this.events = [];
        this.setupEventListeners();
    }
    
    setupEventListeners() {
        window.addEventListener('modalOpened', (e) => {
            this.metrics.modalOpenedAt = e.detail.timestamp;
        });
        
        window.addEventListener('titleVisible', (e) => {
            this.metrics.timeToTitleVisible = e.detail.timeToVisible;
            this.metrics.titleVisibleAt = e.detail.timestamp;
        });
        
        window.addEventListener('modalLoadComplete', (e) => {
            this.metrics.modalLoadTime = e.detail.loadTime;
            this.metrics.modalLoadedAt = e.detail.timestamp;
        });
        
        window.addEventListener('taskCreated', (e) => {
            this.metrics.taskCreationTime = e.detail.creationTime;
            this.metrics.taskData = e.detail.taskData;
            this.metrics.stepLoadTimes = e.detail.stepLoadTimes;
        });
    }
    
    getMetrics() {
        return {
            ...this.metrics,
            events: this.events,
            performance: {
                modalLoadTime: this.metrics.modalLoadTime,
                timeToTitleVisible: this.metrics.timeToTitleVisible,
                totalTaskCreationTime: this.metrics.taskCreationTime,
                lazyLoadingEnabled: Object.keys(this.metrics.stepLoadTimes || {}).length > 0,
                progressiveLoading: true
            }
        };
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.taskWizard = new TaskWizard();
    window.performanceMonitor = new ImprovedPerformanceMonitor();
    
    // Expose metrics for testing
    window.getPerformanceMetrics = () => window.performanceMonitor.getMetrics();
});