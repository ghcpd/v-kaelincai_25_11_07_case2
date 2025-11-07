const openBtn = document.getElementById('openWizard')
const wizard = document.getElementById('wizard')
const stepNum = document.getElementById('stepNum')
const stepContainer = document.getElementById('stepContainer')
const prevBtn = document.getElementById('prevBtn')
const nextBtn = document.getElementById('nextBtn')

let state = { title:'', dueDate:'', assignees:[], tagsLoaded:false, attachmentsLoaded:false }
let current = 0
const steps = [
  { id: 'meta', title: 'Basic Info', render: stepMeta },
  { id: 'assign', title: 'Assign', render: stepAssign },
  { id: 'attachments', title: 'Attachments', render: stepAttachments }
]

openBtn.addEventListener('click', ()=>{
  wizard.classList.remove('hidden')
  current = 0
  render()
})

prevBtn.addEventListener('click', ()=>{ if(current>0){ current--; render(); } })
nextBtn.addEventListener('click', ()=>{
  if(current < steps.length -1){ current++; render(); } else { submit(); }
})

function render(){
  stepNum.textContent = (current+1)
  prevBtn.disabled = current===0
  nextBtn.textContent = current===steps.length-1 ? 'Create' : 'Next'
  stepContainer.innerHTML = ''
  const step = steps[current]
  const el = step.render()
  el.classList.add('wizard-step','active')
  stepContainer.appendChild(el)
}

function stepMeta(){
  const wrapper = document.createElement('div')
  const titleField = document.createElement('div'); titleField.className='field'
  titleField.innerHTML = '<label for="title">Title</label><input id="title" />'
  const dueField = document.createElement('div'); dueField.className='field'
  dueField.innerHTML = '<label for="dueDate">Due Date</label><input id="dueDate" type="date" />'
  wrapper.appendChild(titleField); wrapper.appendChild(dueField)
  return wrapper
}

function stepAssign(){
  const wrapper = document.createElement('div')
  const assignees = document.createElement('div'); assignees.className='field'
  assignees.innerHTML = '<label for="assignees">Assignees</label><select id="assignees" multiple></select>'
  const tags = document.createElement('div'); tags.className='field'
  tags.innerHTML = '<label for="tags">Tags</label><div id="tagsContainer"></div>'
  wrapper.appendChild(assignees); wrapper.appendChild(tags)
  // Lazy load tags and members if not loaded
  if(!state.tagsLoaded){
    fetch('/api/tags').then(r=>r.json()).then(list=>{
      const c = document.getElementById('tagsContainer')
      const l = document.createElement('div'); l.className='heavy-list'
      list.forEach(t=>{ const d = document.createElement('div'); d.textContent = t; l.appendChild(d) })
      c.appendChild(l)
      state.tagsLoaded = true
    })
  }
  if(!state.assignees || state.assignees.length===0){
    fetch('/api/members').then(r=>r.json()).then(members=>{
      const sel = document.getElementById('assignees')
      sel.innerHTML = ''
      members.forEach(m=>{ const opt=document.createElement('option'); opt.value=m.id; opt.textContent=m.name; sel.appendChild(opt) })
    })
  }
  return wrapper
}

function stepAttachments(){
  const wrapper = document.createElement('div')
  const att = document.createElement('div'); att.className='field'
  att.innerHTML = '<label for="attachments">Attachments</label><div id="attachmentsContainer"></div>'
  wrapper.appendChild(att)
  if(!state.attachmentsLoaded){
    fetch('/api/attachments').then(r=>r.json()).then(list=>{
      const c = document.getElementById('attachmentsContainer')
      const l = document.createElement('div'); l.className='heavy-list'
      list.forEach(a=>{ const d=document.createElement('div'); d.textContent=a.name; l.appendChild(d) })
      c.appendChild(l)
      state.attachmentsLoaded = true
    })
  }
  return wrapper
}

function submit(){
  const title = document.getElementById('title')?.value || ''
  if(!title){ alert('Title required'); return }
  alert('Task created (post-improvement)')
  wizard.classList.add('hidden')
}
