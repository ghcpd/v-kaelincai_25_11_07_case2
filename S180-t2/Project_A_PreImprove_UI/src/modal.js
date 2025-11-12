// Eagerly loads all data on modal open, including heavy tags and attachments rendering which simulates slowness.
const openBtn = document.getElementById('openModal');
const modal = document.getElementById('modal');
const closeBtn = document.getElementById('close');

openBtn.addEventListener('click', async () => {
  modal.classList.remove('hidden');
  const start = performance.now();
  // Eagerly fetch everything
  await fetch('/api/tags').then(r=>r.json()).then(data=>{
    const el = document.getElementById('tags');
    el.innerHTML = data.tags.map(t=>`<span class='tag'>${t}</span>`).join(', ');
  });

  await fetch('/api/members').then(r=>r.json()).then(data=>{
    const el = document.getElementById('members');
    el.innerHTML = data.members.map(m=>`<div>${m}</div>`).join('');
  });

  // Simulate attachment rendering cost
  const attachmentsEl = document.getElementById('attachments');
  const heavy = document.createElement('div');
  heavy.innerText = 'Rendered attachments (eager)';
  attachmentsEl.appendChild(heavy);
  const end = performance.now();
  console.log('Modal open took', Math.round(end-start),'ms');
});

closeBtn.addEventListener('click', ()=>{ modal.classList.add('hidden'); });

// Form submit just logs
const form = document.getElementById('createTaskForm');
form.addEventListener('submit', (e)=>{ e.preventDefault(); console.log('create task', {title: form.title.value}); alert('Task created (pre-improve)'); modal.classList.add('hidden'); });
