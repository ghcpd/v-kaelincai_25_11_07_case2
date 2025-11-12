const openBtn = document.getElementById('openWizard');
const wizard = document.getElementById('wizard');
const closeBtn = document.getElementById('closeWizard');
const next1 = document.getElementById('next1');
const next2 = document.getElementById('next2');
const prev2 = document.getElementById('prev2');
const prev3 = document.getElementById('prev3');
const createBtn = document.getElementById('createTask');

const tagsSelect = document.getElementById('tags');
const assigneesSelect = document.getElementById('assignees');
const attachmentsDiv = document.getElementById('attachments');

let currentStep = 1;

openBtn.addEventListener('click', () => {
  wizard.classList.remove('hidden');
  goToStep(1);
});

closeBtn.addEventListener('click', () => wizard.classList.add('hidden'));

next1.addEventListener('click', () => {
  // Validate title/due quickly
  const title = document.getElementById('title').value;
  if (!title) { alert('Please enter a title'); return; }
  goToStep(2);
});

prev2.addEventListener('click', () => goToStep(1));
next2.addEventListener('click', () => goToStep(3));
prev3.addEventListener('click', () => goToStep(2));

createBtn.addEventListener('click', async () => {
  const title = document.getElementById('title').value;
  const description = document.getElementById('description') ? document.getElementById('description').value : '';
  const due = document.getElementById('due').value;
  const assignee = assigneesSelect.value;
  const tags = Array.from(tagsSelect.selectedOptions).map(o => o.value);

  const res = await fetch('/api/create_task', {
    method: 'POST', headers: {'Content-Type':'application/json'},
    body: JSON.stringify({title, description, due, assignee, tags})
  });
  if (res.status === 200) { alert('Task created'); wizard.classList.add('hidden'); }
  else { alert('Error creating task'); }
});

function queryParam(key, defaultValue) { const params = new URLSearchParams(window.location.search); return params.get(key) || defaultValue; }

async function loadTags() {
  if (tagsSelect.childElementCount > 0) return; // already loaded
  const delay = queryParam('delay', '0');
  const resp = await fetch(`/api/tags?delay=${delay}`);
  const data = await resp.json();
  data.tags.forEach(t => { const opt = document.createElement('option'); opt.value = t; opt.textContent = t; tagsSelect.appendChild(opt); });
}

async function loadAssignees() {
  if (assigneesSelect.childElementCount > 0) return;
  const delay = queryParam('delay', '0');
  const resp = await fetch(`/api/members?delay=${delay}`);
  const data = await resp.json();
  data.members.forEach(m => { const opt = document.createElement('option'); opt.value = m; opt.textContent = m; assigneesSelect.appendChild(opt); });
}

async function loadAttachments() {
  if (attachmentsDiv.childElementCount > 0) return;
  const delay = queryParam('delay', '0');
  const size = queryParam('attachments_size', '1');
  const resp = await fetch(`/api/attachments?delay=${delay}&size=${size}`);
  const data = await resp.json();
  attachmentsDiv.innerHTML = data.attachments.map(a => `<div>${a.name} (${a.size}KB)</div>`).join('');
}

async function goToStep(step) {
  currentStep = step; document.getElementById('stepNumber').textContent = step;
  document.querySelectorAll('.step').forEach(s => s.classList.add('hidden'));
  const el = document.getElementById('step'+step); if (el) el.classList.remove('hidden');
  if (step === 2) {
    // lazy-load tags and assignees
    loadAssignees(); loadTags();
  }
  if (step === 3) {
    loadAttachments();
  }
}
