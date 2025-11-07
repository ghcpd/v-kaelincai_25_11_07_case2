const openBtn = document.getElementById('openModal')
const modal = document.getElementById('modal')
const loadingStatus = document.getElementById('loadingStatus')

openBtn.addEventListener('click', async () => {
  modal.classList.remove('hidden')
  loadingStatus.textContent = 'Loading all resources (eager)...'
  // Eagerly fetch all heavy resources
  try {
    const [membersRes, tagsRes, attachmentsRes] = await Promise.all([
      fetch('/api/members').then(r=>r.json()),
      fetch('/api/tags').then(r=>r.json()),
      fetch('/api/attachments').then(r=>r.json())
    ])
    populateMembers(membersRes)
    populateTags(tagsRes)
    populateAttachments(attachmentsRes)
    loadingStatus.textContent = ''
  } catch (e) {
    loadingStatus.textContent = 'Error loading resources.'
  }
})

function populateMembers(members){
  const sel = document.getElementById('assignees')
  sel.innerHTML = ''
  members.forEach(m=>{ const opt = document.createElement('option'); opt.value=m.id; opt.textContent=m.name; sel.appendChild(opt) })
}
function populateTags(tags){
  const c = document.getElementById('tagsContainer')
  c.innerHTML = ''
  const list = document.createElement('div'); list.className='heavy-list'
  tags.forEach(t=>{ const d=document.createElement('div'); d.textContent=t; list.appendChild(d) })
  c.appendChild(list)
}
function populateAttachments(attachments){
  const c = document.getElementById('attachmentsContainer')
  c.innerHTML = ''
  const list = document.createElement('div'); list.className='heavy-list'
  attachments.forEach(a=>{ const d=document.createElement('div'); d.textContent=a.name; list.appendChild(d) })
  c.appendChild(list)
}

// Simple create button behavior
document.getElementById('createBtn').addEventListener('click', ()=>{
  const title = document.getElementById('title').value
  const due = document.getElementById('dueDate').value
  if(!title){ alert('Title required'); return }
  alert('Task created (pre-improvement)')
  modal.classList.add('hidden')
})
