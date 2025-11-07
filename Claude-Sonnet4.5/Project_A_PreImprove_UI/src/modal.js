// Pre-Improvement Modal - Eager Loading, Poor UX

(function() {
    'use strict';

    // Configuration from test environment
    const config = {
        networkLatency: parseInt(localStorage.getItem('network_latency_ms') || '100'),
        tagCount: parseInt(localStorage.getItem('tag_count') || '10'),
        memberCount: parseInt(localStorage.getItem('member_count') || '5'),
        attachmentSizeKb: parseInt(localStorage.getItem('attachment_size_kb') || '0')
    };

    // Performance tracking
    window.performanceMetrics = {
        modalOpenStart: 0,
        modalOpenEnd: 0,
        titleVisibleTime: 0,
        taskCreateStart: 0,
        taskCreateEnd: 0
    };

    // DOM Elements
    const openModalBtn = document.getElementById('openModalBtn');
    const closeModalBtn = document.getElementById('closeModalBtn');
    const cancelBtn = document.getElementById('cancelBtn');
    const taskModal = document.getElementById('taskModal');
    const taskForm = document.getElementById('taskForm');
    const submitBtn = document.getElementById('submitBtn');

    // Event Listeners
    openModalBtn.addEventListener('click', openModal);
    closeModalBtn.addEventListener('click', closeModal);
    cancelBtn.addEventListener('click', closeModal);
    taskForm.addEventListener('submit', handleSubmit);

    // Close modal on ESC key
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && taskModal.style.display === 'block') {
            closeModal();
        }
    });

    // Close modal on backdrop click
    taskModal.addEventListener('click', (e) => {
        if (e.target === taskModal) {
            closeModal();
        }
    });

    // POOR UX: Open modal with eager loading of ALL data
    async function openModal() {
        window.performanceMetrics.modalOpenStart = performance.now();
        
        taskModal.style.display = 'block';
        submitBtn.disabled = true;

        // PROBLEM: Load everything at once, causing slow initial render
        try {
            // Simulate parallel loading of all heavy resources
            await Promise.all([
                loadTags(),
                loadMembers(),
                loadAttachments()
            ]);

            window.performanceMetrics.modalOpenEnd = performance.now();
            
            // Title field is far down in the form, not immediately visible
            setTimeout(() => {
                const titleField = document.getElementById('taskTitle');
                if (isElementInViewport(titleField)) {
                    window.performanceMetrics.titleVisibleTime = performance.now();
                } else {
                    // User has to scroll to see title
                    window.performanceMetrics.titleVisibleTime = -1;
                }
            }, 100);

            submitBtn.disabled = false;

            // Focus first field (which is NOT the title)
            const tagsSelect = document.getElementById('tags');
            if (tagsSelect) {
                tagsSelect.focus();
            }

        } catch (error) {
            console.error('Error loading modal data:', error);
            submitBtn.disabled = false;
        }
    }

    function closeModal() {
        taskModal.style.display = 'none';
        taskForm.reset();
        
        // Clear error messages
        document.querySelectorAll('.error-message').forEach(el => el.textContent = '');
    }

    // Simulate loading tags with network delay
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

        // Hide loader, show select
        container.style.display = 'none';
        select.style.display = 'block';
    }

    // Simulate loading members with network delay
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

        // Hide loader, show select
        container.style.display = 'none';
        select.style.display = 'block';
    }

    // Simulate loading attachments with network delay
    async function loadAttachments() {
        const container = document.getElementById('attachmentsContainer');
        const attachmentsList = document.getElementById('attachmentsList');
        
        // Simulate network latency + large data transfer
        const delay = config.networkLatency + (config.attachmentSizeKb / 10);
        await simulateNetworkDelay(delay);

        // Hide loader, show attachments
        container.style.display = 'none';
        attachmentsList.style.display = 'block';
    }

    // Handle form submission
    async function handleSubmit(e) {
        e.preventDefault();
        
        window.performanceMetrics.taskCreateStart = performance.now();

        // Clear previous errors
        document.querySelectorAll('.error-message').forEach(el => el.textContent = '');

        // Get form data
        const formData = new FormData(taskForm);
        const taskData = {
            title: formData.get('taskTitle'),
            description: formData.get('taskDescription'),
            assignee: formData.get('assignee'),
            dueDate: formData.get('dueDate'),
            priority: formData.get('priority'),
            tags: Array.from(document.getElementById('tags').selectedOptions).map(o => o.value),
            attachments: Array.from(document.getElementById('attachments').files).map(f => f.name)
        };

        // Validate
        const errors = validateTaskData(taskData);
        if (Object.keys(errors).length > 0) {
            displayErrors(errors);
            window.performanceMetrics.taskCreateEnd = performance.now();
            window.performanceMetrics.success = false;
            return;
        }

        // Simulate API call
        submitBtn.disabled = true;
        submitBtn.textContent = 'Creating...';

        try {
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

            // Show success and close
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
            window.performanceMetrics.taskCreateEnd = performance.now();
        }
    }

    // Validation
    function validateTaskData(data) {
        const errors = {};

        if (!data.title || data.title.trim() === '') {
            errors.title = 'Task title is required';
        } else if (data.title.length > 200) {
            errors.title = 'Task title must be less than 200 characters';
        }

        if (!data.dueDate) {
            errors.dueDate = 'Due date is required';
        } else if (isNaN(Date.parse(data.dueDate))) {
            errors.dueDate = 'Invalid date format';
        }

        if (data.assignee && !isValidEmail(data.assignee)) {
            errors.assignee = 'Invalid email format';
        }

        return errors;
    }

    function displayErrors(errors) {
        if (errors.title) {
            document.getElementById('titleError').textContent = errors.title;
        }
        if (errors.dueDate) {
            document.getElementById('dueDateError').textContent = errors.dueDate;
        }
        if (errors.assignee) {
            const assigneeField = document.getElementById('assignee');
            const errorSpan = document.createElement('span');
            errorSpan.className = 'error-message';
            errorSpan.textContent = errors.assignee;
            assigneeField.parentNode.appendChild(errorSpan);
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

    function saveMetrics() {
        const metrics = {
            timestamp: new Date().toISOString(),
            modal_load_time_ms: window.performanceMetrics.modalOpenEnd - window.performanceMetrics.modalOpenStart,
            time_to_title_visible_ms: window.performanceMetrics.titleVisibleTime > 0 
                ? window.performanceMetrics.titleVisibleTime - window.performanceMetrics.modalOpenStart 
                : -1,
            task_create_time_ms: window.performanceMetrics.taskCreateEnd - window.performanceMetrics.taskCreateStart,
            title_visible_without_scroll: window.performanceMetrics.titleVisibleTime > 0,
            success: window.performanceMetrics.success || false,
            config: config
        };

        // Store in localStorage for test harness to retrieve
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
        getMetrics: () => window.performanceMetrics,
        clearMetrics: () => {
            localStorage.removeItem('performance_metrics');
            localStorage.removeItem('tasks');
        }
    };
})();
