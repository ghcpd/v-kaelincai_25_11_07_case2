// Pre-Improvement Modal: Eager loading, poor field ordering
let modal = document.getElementById('taskModal');
let createBtn = document.getElementById('createTaskBtn');
let closeBtn = document.querySelector('.close');
let cancelBtn = document.getElementById('cancelBtn');
let form = document.getElementById('taskForm');

// Simulate network delay
function delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

// Eager loading: Load all tags immediately
async function loadTags() {
    const container = document.getElementById('tagsContainer');
    container.innerHTML = '<div class="loading">Loading tags...</div>';
    
    // Simulate slow API call
    await delay(800); // Simulate network delay
    
    const tags = window.TEST_DATA?.tags || [
        'urgent', 'bug', 'feature', 'documentation', 'design', 
        'backend', 'frontend', 'testing', 'deployment', 'review',
        'refactor', 'optimization', 'security', 'performance', 'accessibility'
    ];
    
    container.innerHTML = '';
    tags.forEach(tag => {
        const tagEl = document.createElement('div');
        tagEl.className = 'tag-item';
        tagEl.textContent = tag;
        tagEl.onclick = () => tagEl.classList.toggle('selected');
        container.appendChild(tagEl);
    });
}

// Eager loading: Load all members immediately
async function loadMembers() {
    const container = document.getElementById('membersContainer');
    container.innerHTML = '<div class="loading">Loading members...</div>';
    
    // Simulate slow API call
    await delay(600);
    
    const members = window.TEST_DATA?.members || [
        'Alice Johnson', 'Bob Smith', 'Charlie Brown', 'Diana Prince',
        'Eve Wilson', 'Frank Miller', 'Grace Lee', 'Henry Davis',
        'Ivy Chen', 'Jack Taylor', 'Kate Williams', 'Liam O\'Connor'
    ];
    
    container.innerHTML = '';
    members.forEach(member => {
        const memberEl = document.createElement('div');
        memberEl.className = 'member-item';
        memberEl.textContent = member;
        memberEl.onclick = () => memberEl.classList.toggle('selected');
        container.appendChild(memberEl);
    });
}

// Eager loading: Load all attachments immediately
async function loadAttachments() {
    const container = document.getElementById('attachmentsContainer');
    container.innerHTML = '<div class="loading">Loading attachments...</div>';
    
    // Simulate slow API call with large dataset
    await delay(1000);
    
    const attachments = window.TEST_DATA?.attachments || Array.from({length: 20}, (_, i) => ({
        name: `attachment_${i + 1}.pdf`,
        size: Math.floor(Math.random() * 5000000) + 1000000 // 1-5MB
    }));
    
    container.innerHTML = '';
    attachments.forEach(att => {
        const attEl = document.createElement('div');
        attEl.className = 'attachment-item';
        attEl.textContent = `${att.name} (${(att.size / 1024 / 1024).toFixed(2)} MB)`;
        container.appendChild(attEl);
    });
}

// Open modal and eagerly load everything
createBtn.onclick = async function() {
    modal.classList.add('show');
    document.body.style.overflow = 'hidden';
    
    // Record modal open time for testing
    window.MODAL_OPEN_TIME = Date.now();
    
    // Eager loading: Load everything immediately
    await Promise.all([
        loadTags(),
        loadMembers(),
        loadAttachments()
    ]);
    
    // Record when all content is loaded
    window.MODAL_CONTENT_LOADED_TIME = Date.now();
};

// Close modal
function closeModal() {
    modal.classList.remove('show');
    document.body.style.overflow = 'auto';
}

closeBtn.onclick = closeModal;
cancelBtn.onclick = closeModal;

window.onclick = function(event) {
    if (event.target == modal) {
        closeModal();
    }
};

// Form submission
form.onsubmit = function(e) {
    e.preventDefault();
    window.TASK_CREATE_TIME = Date.now();
    
    const formData = {
        title: document.getElementById('taskTitle').value,
        description: document.getElementById('taskDescription').value,
        dueDate: document.getElementById('dueDate').value,
        priority: document.getElementById('priority').value
    };
    
    // Validate required fields
    if (!formData.title || !formData.dueDate) {
        alert('Please fill in all required fields');
        return;
    }
    
    console.log('Task created:', formData);
    alert('Task created successfully!');
    closeModal();
    form.reset();
};

// Expose timing data for tests
window.getTimingData = function() {
    return {
        modalOpenTime: window.MODAL_OPEN_TIME,
        contentLoadedTime: window.MODAL_CONTENT_LOADED_TIME,
        taskCreateTime: window.TASK_CREATE_TIME
    };
};

