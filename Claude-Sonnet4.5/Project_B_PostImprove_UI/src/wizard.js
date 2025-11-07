// Post-Improvement Wizard - Step-by-Step with Lazy Loading

(function() {
    'use strict';

    // Configuration from test environment
    const config = {
        networkLatency: parseInt(localStorage.getItem('network_latency_ms') || '100'),
        tagCount: parseInt(localStorage.getItem('tag_count') || '10'),
        memberCount: parseInt(localStorage.getItem('member_count') || '5'),
        attachmentSizeKb: parseInt(localStorage.getItem('attachment_size_kb') || '0')
    };

    // Wizard state
    let currentStep = 1;
    const totalSteps = 3;
    const loadedSteps = new Set([1]); // Step 1 loads immediately

    // Performance tracking
    window.performanceMetrics = {
        modalOpenStart: 0,
        modalOpenEnd: 0,
        titleVisibleTime: 0,
        taskCreateStart: 0,
        taskCreateEnd: 0,
        lazyLoadTimes: {}
    };

    // Task data accumulator
    let taskData = {};

    // DOM Elements
    const openModalBtn = document.getElementById('openModalBtn');
    const closeModalBtn = document.getElementById('closeModalBtn');
    const cancelBtn = document.getElementById('cancelBtn');
    const taskModal = document.getElementById('taskModal');
    const taskForm = document.getElementById('taskForm');
    const nextBtn = document.getElementById('nextBtn');
    const prevBtn = document.getElementById('prevBtn');
    const submitBtn = document.getElementById('submitBtn');
    const loadingOverlay = document.getElementById('loadingOverlay');

    // Event Listeners
    openModalBtn.addEventListener('click', openModal);
    closeModalBtn.addEventListener('click', closeModal);
    cancelBtn.addEventListener('click', closeModal);
    nextBtn.addEventListener('click', nextStep);
    prevBtn.addEventListener('click', previousStep);
    taskForm.addEventListener('submit', handleSubmit);

    // Keyboard shortcuts
    document.addEventListener('keydown', (e) => {
        if (taskModal.style.display === 'block') {
            if (e.key === 'Escape') {
                closeModal();
            }
        }
    });

    // Close modal on backdrop click
    taskModal.addEventListener('click', (e) => {
        if (e.target === taskModal) {
            closeModal();
        }
    });

    // IMPROVED: Fast modal open - only load Step 1 (no network calls needed)
    async function openModal() {
        window.performanceMetrics.modalOpenStart = performance.now();
        
        taskModal.style.display = 'block';
        currentStep = 1;
        loadedSteps.clear();
        loadedSteps.add(1);
        
        // Reset wizard
        resetWizard();
        
        // Step 1 is already in DOM - no loading required!
        window.performanceMetrics.modalOpenEnd = performance.now();
        
        // Title field is immediately visible (first field in form)
        const titleField = document.getElementById('taskTitle');
        titleField.focus();
        
        // Check visibility immediately
        setTimeout(() => {
            if (isElementInViewport(titleField)) {
                window.performanceMetrics.titleVisibleTime = performance.now();
            }
        }, 50);

        // Announce to screen readers
        announceToScreenReader('Task creation wizard opened. Step 1 of 3: Task Details');
    }

    function closeModal() {
        taskModal.style.display = 'none';
        taskForm.reset();
        taskData = {};
        currentStep = 1;
        resetWizard();
        
        // Clear error messages
        document.querySelectorAll('.error-message').forEach(el => el.textContent = '');
    }

    function resetWizard() {
        // Reset step indicators
        document.querySelectorAll('.wizard-progress .step').forEach((step, index) => {
            step.classList.remove('active', 'completed');
            if (index === 0) step.classList.add('active');
        });

        // Show only first step
        document.querySelectorAll('.wizard-step').forEach((step, index) => {
            step.style.display = index === 0 ? 'block' : 'none';
        });

        // Reset buttons
        prevBtn.style.display = 'none';
        nextBtn.style.display = 'inline-block';
        submitBtn.style.display = 'none';
    }

    // Navigate to next step with lazy loading
    async function nextStep() {
        // Validate current step
        if (!validateCurrentStep()) {
            return;
        }

        // Save current step data
        saveCurrentStepData();

        if (currentStep < totalSteps) {
            // Mark current step as completed
            const currentStepEl = document.querySelector(`.wizard-progress .step[data-step="${currentStep}"]`);
            currentStepEl.classList.remove('active');
            currentStepEl.classList.add('completed');

            currentStep++;

            // Activate new step
            const newStepEl = document.querySelector(`.wizard-progress .step[data-step="${currentStep}"]`);
            newStepEl.classList.add('active');

            // Hide current wizard step
            document.querySelectorAll('.wizard-step').forEach(step => {
                step.style.display = 'none';
            });

            // Show new step
            const wizardStep = document.querySelector(`.wizard-step[data-step="${currentStep}"]`);
            wizardStep.style.display = 'block';

            // LAZY LOAD: Only load data when step becomes active
            if (!loadedSteps.has(currentStep)) {
                await loadStepData(currentStep);
                loadedSteps.add(currentStep);
            }

            // Update navigation buttons
            updateNavigationButtons();

            // Announce to screen readers
            announceToScreenReader(`Step ${currentStep} of ${totalSteps}: ${getStepName(currentStep)}`);

            // Focus first field in new step
            focusFirstField(currentStep);
        }
    }

    function previousStep() {
        if (currentStep > 1) {
            // Mark current step as inactive
            const currentStepEl = document.querySelector(`.wizard-progress .step[data-step="${currentStep}"]`);
            currentStepEl.classList.remove('active');

            currentStep--;

            // Activate previous step
            const prevStepEl = document.querySelector(`.wizard-progress .step[data-step="${currentStep}"]`);
            prevStepEl.classList.remove('completed');
            prevStepEl.classList.add('active');

            // Hide current wizard step
            document.querySelectorAll('.wizard-step').forEach(step => {
                step.style.display = 'none';
            });

            // Show previous step
            const wizardStep = document.querySelector(`.wizard-step[data-step="${currentStep}"]`);
            wizardStep.style.display = 'block';

            // Update navigation buttons
            updateNavigationButtons();

            // Announce to screen readers
            announceToScreenReader(`Step ${currentStep} of ${totalSteps}: ${getStepName(currentStep)}`);

            // Focus first field
            focusFirstField(currentStep);
        }
    }

    function updateNavigationButtons() {
        // Show/hide previous button
        prevBtn.style.display = currentStep > 1 ? 'inline-block' : 'none';

        // Show next or submit button
        if (currentStep === totalSteps) {
            nextBtn.style.display = 'none';
            submitBtn.style.display = 'inline-block';
            
            // Update summary
            updateTaskSummary();
        } else {
            nextBtn.style.display = 'inline-block';
            submitBtn.style.display = 'none';
        }
    }

    // LAZY LOADING: Load data only when step is activated
    async function loadStepData(step) {
        const loadStart = performance.now();
        loadingOverlay.style.display = 'flex';

        try {
            if (step === 2) {
                // Load members and tags
                await Promise.all([
                    loadMembers(),
                    loadTags()
                ]);
            } else if (step === 3) {
                // Load attachments functionality
                await loadAttachments();
            }
        } catch (error) {
            console.error(`Error loading step ${step}:`, error);
        } finally {
            loadingOverlay.style.display = 'none';
            window.performanceMetrics.lazyLoadTimes[`step${step}`] = performance.now() - loadStart;
        }
    }

    // Load members (lazy)
    async function loadMembers() {
        const container = document.getElementById('membersContainer');
        const select = document.getElementById('assignee');
        
        // Simulate network latency
        await simulateNetworkDelay(config.networkLatency);

        // Generate members
        const members = generateMembers(config.memberCount);
        
        // Populate select
        members.forEach(member => {
            const option = document.createElement('option');
            option.value = member.email;
            option.textContent = `${member.name} (${member.email})`;
            select.appendChild(option);
        });

        // Pre-select if data exists
        if (taskData.assignee) {
            select.value = taskData.assignee;
        }

        // Show select, hide loader
        container.classList.add('loaded');
        select.style.display = 'block';
    }

    // Load tags (lazy)
    async function loadTags() {
        const container = document.getElementById('tagsContainer');
        const select = document.getElementById('tags');
        
        // Simulate network latency
        await simulateNetworkDelay(config.networkLatency);

        // Generate tags
        const tags = generateTags(config.tagCount);
        
        // Populate select
        tags.forEach(tag => {
            const option = document.createElement('option');
            option.value = tag.id;
            option.textContent = tag.name;
            select.appendChild(option);
        });

        // Pre-select if data exists
        if (taskData.tags) {
            Array.from(select.options).forEach(option => {
                if (taskData.tags.includes(option.value)) {
                    option.selected = true;
                }
            });
        }

        // Show select, hide loader
        container.classList.add('loaded');
        select.style.display = 'block';
    }

    // Load attachments (lazy)
    async function loadAttachments() {
        const container = document.getElementById('attachmentsContainer');
        const attachmentsList = document.getElementById('attachmentsList');
        
        // Simulate network latency
        const delay = config.networkLatency + (config.attachmentSizeKb / 20);
        await simulateNetworkDelay(delay);

        // Show attachments section
        container.classList.add('loaded');
        attachmentsList.style.display = 'block';

        // Add file change listener for previews
        const fileInput = document.getElementById('attachments');
        fileInput.addEventListener('change', updateAttachmentPreviews);
    }

    function updateAttachmentPreviews() {
        const fileInput = document.getElementById('attachments');
        const previews = document.getElementById('attachmentPreviews');
        previews.innerHTML = '';

        Array.from(fileInput.files).forEach(file => {
            const preview = document.createElement('div');
            preview.className = 'attachment-preview';
            preview.textContent = `📎 ${file.name}`;
            previews.appendChild(preview);
        });
    }

    function updateTaskSummary() {
        const summary = document.getElementById('taskSummary');
        
        const html = `
            <p><strong>Title:</strong> ${escapeHtml(taskData.title || 'Not set')}</p>
            <p><strong>Due Date:</strong> ${taskData.dueDate || 'Not set'}</p>
            <p><strong>Priority:</strong> ${taskData.priority || 'Medium'}</p>
            <p><strong>Description:</strong> ${escapeHtml(taskData.description || 'None')}</p>
            <p><strong>Assignee:</strong> ${taskData.assignee || 'Unassigned'}</p>
            <p><strong>Tags:</strong> ${taskData.tags && taskData.tags.length > 0 ? taskData.tags.join(', ') : 'None'}</p>
            <p><strong>Attachments:</strong> ${taskData.attachments && taskData.attachments.length > 0 ? taskData.attachments.length + ' file(s)' : 'None'}</p>
        `;
        
        summary.innerHTML = html;
    }

    function validateCurrentStep() {
        // Clear previous errors
        document.querySelectorAll('.error-message').forEach(el => el.textContent = '');

        if (currentStep === 1) {
            let isValid = true;
            const title = document.getElementById('taskTitle').value.trim();
            const dueDate = document.getElementById('dueDate').value;

            if (!title) {
                document.getElementById('titleError').textContent = 'Task title is required';
                isValid = false;
            } else if (title.length > 200) {
                document.getElementById('titleError').textContent = 'Task title must be less than 200 characters';
                isValid = false;
            }

            if (!dueDate) {
                document.getElementById('dueDateError').textContent = 'Due date is required';
                isValid = false;
            } else if (isNaN(Date.parse(dueDate))) {
                document.getElementById('dueDateError').textContent = 'Invalid date format';
                isValid = false;
            }

            return isValid;
        }

        if (currentStep === 2) {
            const assignee = document.getElementById('assignee').value;
            if (assignee && !isValidEmail(assignee)) {
                document.getElementById('assigneeError').textContent = 'Invalid email format';
                return false;
            }
        }

        return true;
    }

    function saveCurrentStepData() {
        if (currentStep === 1) {
            taskData.title = document.getElementById('taskTitle').value.trim();
            taskData.dueDate = document.getElementById('dueDate').value;
            taskData.priority = document.getElementById('priority').value;
            taskData.description = document.getElementById('taskDescription').value.trim();
        } else if (currentStep === 2) {
            taskData.assignee = document.getElementById('assignee').value;
            const tagsSelect = document.getElementById('tags');
            taskData.tags = Array.from(tagsSelect.selectedOptions).map(o => o.textContent);
        } else if (currentStep === 3) {
            const files = document.getElementById('attachments').files;
            taskData.attachments = Array.from(files).map(f => f.name);
        }
    }

    // Handle form submission
    async function handleSubmit(e) {
        e.preventDefault();
        
        window.performanceMetrics.taskCreateStart = performance.now();

        // Final validation
        if (!validateCurrentStep()) {
            window.performanceMetrics.taskCreateEnd = performance.now();
            window.performanceMetrics.success = false;
            return;
        }

        // Save final step data
        saveCurrentStepData();

        // Disable submit button
        submitBtn.disabled = true;
        submitBtn.textContent = 'Creating...';
        loadingOverlay.style.display = 'flex';

        try {
            // Simulate API call
            await simulateNetworkDelay(config.networkLatency);
            
            // Store task
            const tasks = JSON.parse(localStorage.getItem('tasks') || '[]');
            taskData.id = Date.now();
            taskData.created = new Date().toISOString();
            tasks.push(taskData);
            localStorage.setItem('tasks', JSON.stringify(tasks));

            window.performanceMetrics.taskCreateEnd = performance.now();
            window.performanceMetrics.success = true;

            // Save metrics
            saveMetrics();

            // Show success
            alert('Task created successfully!');
            closeModal();
            displayTasks();

        } catch (error) {
            console.error('Error creating task:', error);
            alert('Error creating task. Please try again.');
            window.performanceMetrics.success = false;
        } finally {
            submitBtn.disabled = false;
            submitBtn.textContent = 'Create Task';
            loadingOverlay.style.display = 'none';
            window.performanceMetrics.taskCreateEnd = performance.now();
        }
    }

    // Utilities
    function simulateNetworkDelay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    function generateTags(count) {
        const tagNames = ['urgent', 'bug', 'feature', 'documentation', 'testing', 'design', 
                         'backend', 'frontend', 'database', 'security', 'performance', 
                         'refactoring', 'review', 'planning', 'research', 'meeting',
                         'deployment', 'monitoring', 'analytics', 'marketing'];
        
        return Array.from({length: Math.min(count, tagNames.length)}, (_, i) => ({
            id: `tag-${i}`,
            name: tagNames[i] || `tag-${i}`
        }));
    }

    function generateMembers(count) {
        const names = ['John Doe', 'Sarah Smith', 'Mike Jones', 'Emily Chen', 'David Brown',
                      'Lisa Wilson', 'Tom Anderson', 'Anna Martinez', 'Chris Taylor', 'Jessica Lee'];
        
        return Array.from({length: Math.min(count, names.length)}, (_, i) => ({
            id: i,
            name: names[i] || `User ${i}`,
            email: (names[i] || `user${i}`).toLowerCase().replace(' ', '.') + '@company.com'
        }));
    }

    function isValidEmail(email) {
        return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
    }

    function isElementInViewport(el) {
        const rect = el.getBoundingClientRect();
        return (
            rect.top >= 0 &&
            rect.left >= 0 &&
            rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
            rect.right <= (window.innerWidth || document.documentElement.clientWidth)
        );
    }

    function getStepName(step) {
        const names = ['Task Details', 'Assignment & Organization', 'Attachments & Summary'];
        return names[step - 1] || 'Unknown';
    }

    function focusFirstField(step) {
        setTimeout(() => {
            if (step === 1) {
                document.getElementById('taskTitle').focus();
            } else if (step === 2) {
                document.getElementById('assignee').focus();
            } else if (step === 3) {
                document.getElementById('attachments').focus();
            }
        }, 100);
    }

    function announceToScreenReader(message) {
        // Create live region if it doesn't exist
        let liveRegion = document.getElementById('ariaLiveRegion');
        if (!liveRegion) {
            liveRegion = document.createElement('div');
            liveRegion.id = 'ariaLiveRegion';
            liveRegion.setAttribute('aria-live', 'polite');
            liveRegion.setAttribute('aria-atomic', 'true');
            liveRegion.style.position = 'absolute';
            liveRegion.style.left = '-10000px';
            liveRegion.style.width = '1px';
            liveRegion.style.height = '1px';
            liveRegion.style.overflow = 'hidden';
            document.body.appendChild(liveRegion);
        }
        
        liveRegion.textContent = message;
    }

    function saveMetrics() {
        const metrics = {
            timestamp: new Date().toISOString(),
            modal_load_time_ms: window.performanceMetrics.modalOpenEnd - window.performanceMetrics.modalOpenStart,
            time_to_title_visible_ms: window.performanceMetrics.titleVisibleTime > 0 
                ? window.performanceMetrics.titleVisibleTime - window.performanceMetrics.modalOpenStart 
                : window.performanceMetrics.titleVisibleTime,
            task_create_time_ms: window.performanceMetrics.taskCreateEnd - window.performanceMetrics.taskCreateStart,
            title_visible_without_scroll: window.performanceMetrics.titleVisibleTime > 0,
            lazy_load_times: window.performanceMetrics.lazyLoadTimes,
            success: window.performanceMetrics.success || false,
            config: config,
            steps_completed: currentStep
        };

        // Store in localStorage for test harness
        const allMetrics = JSON.parse(localStorage.getItem('performance_metrics') || '[]');
        allMetrics.push(metrics);
        localStorage.setItem('performance_metrics', JSON.stringify(allMetrics));
        
        console.log('Performance Metrics:', metrics);
    }

    function displayTasks() {
        const tasksContainer = document.getElementById('tasks');
        const tasks = JSON.parse(localStorage.getItem('tasks') || '[]');
        
        if (tasks.length === 0) {
            tasksContainer.innerHTML = '<p>No tasks yet. Create your first task!</p>';
            return;
        }

        tasksContainer.innerHTML = tasks.map(task => `
            <div class="task-item">
                <h3>${escapeHtml(task.title)}</h3>
                <p><strong>Due:</strong> ${task.dueDate} | <strong>Priority:</strong> ${task.priority}</p>
                <p>${escapeHtml(task.description || '')}</p>
            </div>
        `).join('');
    }

    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    // Initialize
    displayTasks();

    // Expose for testing
    window.taskManager = {
        openModal,
        closeModal,
        nextStep,
        previousStep,
        getCurrentStep: () => currentStep,
        getMetrics: () => window.performanceMetrics,
        clearMetrics: () => {
            localStorage.removeItem('performance_metrics');
            localStorage.removeItem('tasks');
        }
    };
})();
