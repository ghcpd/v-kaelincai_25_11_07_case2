const openBtn = document.getElementById('openWizard');
const wizard = document.getElementById('wizard');
const closeBtn = document.getElementById('close');

openBtn.addEventListener('click', ()=>{
  wizard.classList.remove('hidden');
  // Show first step immediately and prioritize title/due date
  document.querySelector('.wizard-step[data-step="1"]').classList.remove('hidden');
});

// simple flow
document.getElementById('next1').addEventListener('click', ()=>{
  document.querySelector('.wizard-step[data-step="1"]').classList.add('hidden');
  document.querySelector('.wizard-step[data-step="2"]').classList.remove('hidden');
  // lazy load members when entering assignment step
  fetch('/api/members').then(r=>r.json()).then(data=>{
    const sel = document.getElementById('assignee');
    sel.innerHTML = data.members.map(m=>`<option>${m}</option>`).join('');
  });
});

document.getElementById('next2').addEventListener('click', ()=>{
  document.querySelector('.wizard-step[data-step="2"]').classList.add('hidden');
  const third = document.querySelector('.wizard-step[data-step="3"]');
  third.classList.remove('hidden');
  // lazy load tags when entering final step
  fetch('/api/tags').then(r=>r.json()).then(data=>{
    document.getElementById('lazy-tags').innerHTML = data.tags.slice(0,20).map(t=>`<span>${t}</span>`).join(', ');
  });
});

['prev2','prev3'].forEach(id=>{ const el=document.getElementById(id); if(el) el.addEventListener('click', ()=>{ // navigate back
  const cur = document.querySelector('.wizard-step:not(.hidden)');
  const prev = document.querySelector('.wizard-step[data-step="'+(parseInt(cur.dataset.step)-1)+'"]');
  cur.classList.add('hidden'); prev.classList.remove('hidden'); });});

// finish
document.getElementById('finish').addEventListener('click', ()=>{ const title = document.getElementById('title').value; console.log('created task improved', {title}); alert('Task created (improved)'); wizard.classList.add('hidden'); });

closeBtn.addEventListener('click', ()=>wizard.classList.add('hidden'));
