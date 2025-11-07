// Pre-Improvement JS - loads tags, members, and attachments eagerly and places critical fields low

const createBtn = document.getElementById('createTaskBtn');
const modal = document.getElementById('taskModal');
const closeBtn = document.querySelector('.close');
const cancelBtn = document.getElementById('cancelBtn');
const loadingOverlay = document.getElementById('loadingOverlay');
const projectSelect = document.getElementById('project');
const assigneeSelect = document.getElementById('assignee');
const tagsContainer = document.getElementById('tagsContainer');
const attachmentsContainer = document.getElementById('attachmentsContainer');
const addAttachmentBtn = document.getElementById('addAttachment');
const taskForm = document.getElementById('taskForm');

let dataCache = {};

function showLoading() {
    loadingOverlay.classList.add('show');
}

function hideLoading() {
    loadingOverlay.classList.remove('show');
}

function openModal() {
    modal.style.display = 'block';
    loadAllDataEagerly();
}

function closeModal() {
    modal.style.display = 'none';
}

function simulateNetworkDelay(ms) {
    return new Promise((resolve) => setTimeout(resolve, ms));
}

async function loadAllDataEagerly() {
    showLoading();
    // Simulate fetching projects, tags, members and attachments eagerly
    const latency = parseInt(localStorage.getItem('simulated_latency_ms') || '150');
    await simulateNetworkDelay(latency);

    // fetch sample data from static server
    try {
        const res = await fetch('/data/sample_data.json');
        const json = await res.json();

        // populate projects
        json.projects.forEach(p => {
            const opt = document.createElement('option');
            opt.value = p.id;
            opt.textContent = p.name;
            projectSelect.appendChild(opt);
        });

        // populate tags - all loaded eagerly
        json.tags.forEach(t => {
            const btn = document.createElement('button');
            btn.className = 'tag-item';
            btn.textContent = t.name;
            btn.setAttribute('data-tag-id', t.id);
            btn.addEventListener('click', () => btn.classList.toggle('selected'));
            tagsContainer.appendChild(btn);
        });

        // populate members
        json.members.forEach(m => {
            const opt = document.createElement('option');
            opt.value = m.id;
            opt.textContent = `${m.name} (${m.email})`;
            assigneeSelect.appendChild(opt);
        });

        // load attachments eagerly
        json.attachments.forEach(a => {
            const div = document.createElement('div');
            div.className = 'attachment-item';
            div.innerHTML = `<div class="attachment-info"><strong>${a.name}</strong><span class="attachment-size">${Math.round(a.size/1024)} KB</span></div>`;
            attachmentsContainer.appendChild(div);
        });

    } catch (err) {
        console.error('Failed to load data', err);
    } finally {
        hideLoading();
    }
}

createBtn.addEventListener('click', () => {
    showLoading();
    // small delay to simulate modal animation + fetch
    setTimeout(() => {
        openModal();
        hideLoading();
    }, 350);
});

closeBtn.addEventListener('click', closeModal);
cancelBtn.addEventListener('click', closeModal);

taskForm.addEventListener('submit', (e) => {
    e.preventDefault();
    // naive save
    const payload = new FormData(taskForm);
    console.log('Task payload:', Object.fromEntries(payload));
    alert('Task created (pre-improvement)');
    closeModal();
});

addAttachmentBtn.addEventListener('click', () => alert('Upload flow (not implemented)'));

// keyboard accessibility is not prioritized, focus management is poor
window.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') closeModal();
});

// small helper: reset form when modal closed
modal.addEventListener('click', (e) => {
    if (e.target === modal) closeModal();
});