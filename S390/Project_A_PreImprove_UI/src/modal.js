const openBtn = document.getElementById('openModal');
const modal = document.getElementById('modal');
const closeBtn = document.getElementById('closeModal');
const createBtn = document.getElementById('createTask');

const tagsSelect = document.getElementById('tags');
const assigneesSelect = document.getElementById('assignees');
const attachmentsDiv = document.getElementById('attachments');

openBtn.addEventListener('click', async () => {
  modal.classList.remove('hidden');
  // eager load heavy modules (tags, members, attachments)
  await loadTags();
  await loadAssignees();
  await loadAttachments();
});

closeBtn.addEventListener('click', () => modal.classList.add('hidden'));

createBtn.addEventListener('click', async () => {
  const title = document.getElementById('title').value;
  const description = document.getElementById('description').value;
  const due = document.getElementById('due').value;
  const assignee = assigneesSelect.value;
  const tags = Array.from(tagsSelect.selectedOptions).map(o => o.value);

  const res = await fetch('/api/create_task', {
    method: 'POST',
    headers: {'Content-Type':'application/json'},
    body: JSON.stringify({ title, description, due, assignee, tags })
  });

  if (res.status === 200) {
    alert('Task created');
    modal.classList.add('hidden');
  } else {
    alert('Error creating task');
  }
});

function queryParam(key, defaultValue) { const params = new URLSearchParams(window.location.search); return params.get(key) || defaultValue; }

async function loadTags() {
  const delay = queryParam('delay', '0');
  const resp = await fetch(`/api/tags?delay=${delay}`);
  const data = await resp.json();
  tagsSelect.innerHTML = '';
  data.tags.forEach(t => {
    const opt = document.createElement('option'); opt.value = t; opt.textContent = t; tagsSelect.appendChild(opt);
  });
}

async function loadAssignees() {
  const delay = queryParam('delay', '0');
  const resp = await fetch(`/api/members?delay=${delay}`);
  const data = await resp.json();
  assigneesSelect.innerHTML = '';
  data.members.forEach(m => {
    const opt = document.createElement('option'); opt.value = m; opt.textContent = m; assigneesSelect.appendChild(opt);
  });
}

async function loadAttachments() {
  const delay = queryParam('delay', '0');
  const size = queryParam('attachments_size', '1');
  const resp = await fetch(`/api/attachments?delay=${delay}&size=${size}`);
  const data = await resp.json();
  attachmentsDiv.innerHTML = data.attachments.map(a => `<div>${a.name} (${a.size}KB)</div>`).join('');
}