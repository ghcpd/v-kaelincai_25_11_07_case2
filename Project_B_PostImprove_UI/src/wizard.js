// Post-Improvement Wizard: Step-by-step flow, lazy loading, improved field ordering
let modal = document.getElementById('taskModal');
let createBtn = document.getElementById('createTaskBtn');
let closeBtn = document.querySelector('.close');
let cancelBtn = document.getElementById('cancelBtn');
let prevBtn = document.getElementById('prevBtn');
let nextBtn = document.getElementById('nextBtn');
let submitBtn = document.getElementById('submitBtn');
let form = document.getElementById('taskForm');

let currentStep = 1;
const totalSteps = 3;
let tagsLoaded = false;
let membersLoaded = false;
let attachmentsLoaded = false;

// Simulate network delay
function delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

// Lazy loading: Load tags only when step 2 is reached
async function loadTags() {
    if (tagsLoaded) return;
    
    const container = document.getElementById('tagsContainer');
    container.innerHTML = '<div class="loading">Loading tags...</div>';
    
    // Simulate API call
    await delay(400); // Reduced delay due to lazy loading
    
    const tags = window.TEST_DATA?.tags || Array.from({length: 15}, (_, i) => 
        ['urgent', 'bug', 'feature', 'documentation', 'design', 
         'backend', 'frontend', 'testing', 'deployment', 'review',
         'refactor', 'optimization', 'security', 'performance', 'accessibility'][i]
    );
    
    container.innerHTML = '';
    tags.forEach(tag => {
        const tagEl = document.createElement('div');
        tagEl.className = 'tag-item';
        tagEl.textContent = tag;
        tagEl.tabIndex = 0;
        tagEl.setAttribute('role', 'checkbox');
        tagEl.setAttribute('aria-checked', 'false');
        tagEl.onclick = () => {
            tagEl.classList.toggle('selected');
            tagEl.setAttribute('aria-checked', tagEl.classList.contains('selected'));
        };
        tagEl.onkeydown = (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                tagEl.click();
            }
        };
        container.appendChild(tagEl);
    });
    
    tagsLoaded = true;
}

// Lazy loading: Load members only when step 2 is reached
async function loadMembers() {
    if (membersLoaded) return;
    
    const container = document.getElementById('membersContainer');
    container.innerHTML = '<div class="loading">Loading members...</div>';
    
    // Simulate API call
    await delay(300);
    
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
        memberEl.tabIndex = 0;
        memberEl.setAttribute('role', 'checkbox');
        memberEl.setAttribute('aria-checked', 'false');
        memberEl.onclick = () => {
            memberEl.classList.toggle('selected');
            memberEl.setAttribute('aria-checked', memberEl.classList.contains('selected'));
        };
        memberEl.onkeydown = (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                memberEl.click();
            }
        };
        container.appendChild(memberEl);
    });
    
    membersLoaded = true;
}

// Lazy loading: Load attachments only when step 3 is reached
async function loadAttachments() {
    if (attachmentsLoaded) return;
    
    const container = document.getElementById('attachmentsContainer');
    container.innerHTML = '<div class="loading">Loading attachments...</div>';
    
    // Simulate API call
    await delay(500);
    
    const attachments = window.TEST_DATA?.attachments || Array.from({length: 20}, (_, i) => ({
        name: `attachment_${i + 1}.pdf`,
        size: Math.floor(Math.random() * 5000000) + 1000000
    }));
    
    container.innerHTML = '';
    attachments.forEach(att => {
        const attEl = document.createElement('div');
        attEl.className = 'attachment-item';
        attEl.textContent = `${att.name} (${(att.size / 1024 / 1024).toFixed(2)} MB)`;
        container.appendChild(attEl);
    });
    
    attachmentsLoaded = true;
}

// Update step indicator
function updateStepIndicator(step) {
    const indicators = document.querySelectorAll('.step-indicator');
    indicators.forEach((indicator, index) => {
        const stepNum = index + 1;
        indicator.classList.remove('active', 'completed');
        
        if (stepNum < step) {
            indicator.classList.add('completed');
            indicator.setAttribute('aria-selected', 'false');
        } else if (stepNum === step) {
            indicator.classList.add('active');
            indicator.setAttribute('aria-selected', 'true');
        } else {
            indicator.setAttribute('aria-selected', 'false');
        }
    });
}

// Show step
function showStep(step) {
    // Hide all steps
    document.querySelectorAll('.wizard-step').forEach(stepEl => {
        stepEl.classList.remove('active');
    });
    
    // Show current step
    const currentStepEl = document.querySelector(`.wizard-step[data-step="${step}"]`);
    if (currentStepEl) {
        currentStepEl.classList.add('active');
    }
    
    // Update buttons
    prevBtn.style.display = step > 1 ? 'inline-block' : 'none';
    nextBtn.style.display = step < totalSteps ? 'inline-block' : 'none';
    submitBtn.style.display = step === totalSteps ? 'inline-block' : 'none';
    
    updateStepIndicator(step);
    
    // Lazy load data when reaching a step
    if (step === 2 && !tagsLoaded) {
        loadTags();
        loadMembers();
    } else if (step === 3 && !attachmentsLoaded) {
        loadAttachments();
    }
    
    // Focus first input in step
    setTimeout(() => {
        const firstInput = currentStepEl?.querySelector('input, textarea, select');
        if (firstInput) {
            firstInput.focus();
        }
    }, 100);
}

// Next step
nextBtn.onclick = async function() {
    // Validate current step
    if (currentStep === 1) {
        const title = document.getElementById('taskTitle').value;
        const dueDate = document.getElementById('dueDate').value;
        
        if (!title || !dueDate) {
            alert('Please fill in all required fields');
            return;
        }
    }
    
    if (currentStep < totalSteps) {
        currentStep++;
        showStep(currentStep);
    }
};

// Previous step
prevBtn.onclick = function() {
    if (currentStep > 1) {
        currentStep--;
        showStep(currentStep);
    }
};

// Open modal and show first step (fast initial load)
createBtn.onclick = async function() {
    modal.classList.add('show');
    document.body.style.overflow = 'hidden';
    
    // Record modal open time for testing
    window.MODAL_OPEN_TIME = Date.now();
    
    // Reset wizard state
    currentStep = 1;
    tagsLoaded = false;
    membersLoaded = false;
    attachmentsLoaded = false;
    
    showStep(1);
    
    // Record when first step is visible (should be immediate)
    window.FIRST_STEP_VISIBLE_TIME = Date.now();
    
    // Focus first input
    setTimeout(() => {
        document.getElementById('taskTitle').focus();
    }, 100);
};

// Close modal
function closeModal() {
    modal.classList.remove('show');
    document.body.style.overflow = 'auto';
    form.reset();
    currentStep = 1;
    tagsLoaded = false;
    membersLoaded = false;
    attachmentsLoaded = false;
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
    currentStep = 1;
    showStep(1);
};

// Keyboard navigation
document.addEventListener('keydown', function(e) {
    if (!modal.classList.contains('show')) return;
    
    // ESC to close
    if (e.key === 'Escape') {
        closeModal();
    }
    
    // Tab navigation is handled by browser
});

// Expose timing data for tests
window.getTimingData = function() {
    return {
        modalOpenTime: window.MODAL_OPEN_TIME,
        firstStepVisibleTime: window.FIRST_STEP_VISIBLE_TIME,
        taskCreateTime: window.TASK_CREATE_TIME
    };
};

