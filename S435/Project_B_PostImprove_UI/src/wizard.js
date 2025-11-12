// Post-Improvement Wizard JS - lazy loading heavy modules and prioritizing fields

const createBtnB = document.getElementById('createTaskBtn');
const modalB = document.getElementById('taskModal');
const closeBtnB = document.querySelector('.close');
const loadingOverlayB = document.getElementById('loadingOverlay');
const assigneeSelectB = document.getElementById('assignee');
const tagsContainerB = document.getElementById('tagsContainer');
const attachmentsContainerB = document.getElementById('attachmentsContainer');
const addAttachmentBtnB = document.getElementById('addAttachment');
const step1 = document.getElementById('step-1');
const step2 = document.getElementById('step-2');
const step3 = document.getElementById('step-3');
const nextToAssignee = document.getElementById('nextToAssignee');
const nextToTags = document.getElementById('nextToTags');
const backToDetails = document.getElementById('backToDetails');
const backToAssign = document.getElementById('backToAssign');
const submitTask = document.getElementById('submitTask');

let loadedHeavy = false;

function showModalB() {
    modalB.style.display = 'flex';
    // First step only - minimal work
    // Focus title field immediately
    setTimeout(() => document.getElementById('title').focus(), 200);
}

function closeModalB() {
    modalB.style.display = 'none';
}

function showLoadingB(message='Loading...') {
    document.getElementById('loadingText').textContent = message;
    loadingOverlayB.classList.add('show');
}

function hideLoadingB() {
    loadingOverlayB.classList.remove('show');
}

function simulateNetworkDelay(ms) {
    return new Promise((resolve) => setTimeout(resolve, ms));
}

async function lazyLoadHeavyDataIfNeeded() {
    if (loadedHeavy) return;
    loadedHeavy = true;
    showLoadingB('Loading tags and attachments...');
    const latency = parseInt(localStorage.getItem('simulated_latency_ms') || '150');
    await simulateNetworkDelay(latency);
    try {
        const res = await fetch('/data/sample_data.json');
        const json = await res.json();
        // populate members (light) - used in step 2
        json.members.forEach(m => {
            const opt = document.createElement('option');
            opt.value = m.id;
            opt.textContent = `${m.name} (${m.email})`;
            assigneeSelectB.appendChild(opt);
        });

        // populate tags (heavy) - only in step 3
        json.tags.forEach(t => {
            const btn = document.createElement('button');
            btn.className = 'tag-item';
            btn.textContent = t.name;
            btn.setAttribute('data-tag-id', t.id);
            btn.addEventListener('click', () => btn.classList.toggle('selected'));
            tagsContainerB.appendChild(btn);
        });

        // attachments are loaded lazily in step 3 only
        json.attachments.forEach(a => {
            const div = document.createElement('div');
            div.className = 'attachment-item';
            div.innerHTML = `<div class="attachment-info"><strong>${a.name}</strong><span class="attachment-size">${Math.round(a.size/1024)} KB</span></div>`;
            attachmentsContainerB.appendChild(div);
        });
    } catch (err) {
        console.error('Failed to load heavy data', err);
    } finally {
        hideLoadingB();
    }
}

createBtnB.addEventListener('click', () => {
    showModalB();
});

closeBtnB.addEventListener('click', closeModalB);
modalB.addEventListener('click', (e) => { if (e.target === modalB) closeModalB(); });

nextToAssignee.addEventListener('click', async () => {
    step1.style.display = 'none';
    step2.style.display = 'block';
    // load assignee list if not loaded
    if (assigneeSelectB.options.length <= 1) {
        showLoadingB('Loading assignees...');
        await lazyLoadHeavyDataIfNeeded();
    }
    assigneeSelectB.focus();
});

nextToTags.addEventListener('click', async () => {
    step2.style.display = 'none';
    step3.style.display = 'block';
    // load tags and attachments if not loaded
    if (!loadedHeavy) await lazyLoadHeavyDataIfNeeded();
});

backToDetails.addEventListener('click', () => {
    step2.style.display = 'none';
    step1.style.display = 'block';
    document.getElementById('title').focus();
});

backToAssign.addEventListener('click', () => {
    step3.style.display = 'none';
    step2.style.display = 'block';
    assigneeSelectB.focus();
});

submitTask.addEventListener('click', () => {
    // validate required fields
    const title = document.getElementById('title').value.trim();
    const due = document.getElementById('dueDate').value.trim();
    if (!title || !due) {
        alert('Please fill out required fields: title and due date');
        return;
    }
    // naive submit
    alert('Task created (post-improvement)');
    closeModalB();
});

window.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') closeModalB();
});

// small helper to track focus flow for accessibility
document.addEventListener('focusin', (e) => {
    // Could log focus movement for test harness; no-op for now
});
