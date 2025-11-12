(function(){
  const open = document.getElementById('openModal');
  const modal = document.getElementById('modal');
  const tagList = document.getElementById('tagList');
  const memberList = document.getElementById('memberList');
  const attachList = document.getElementById('attachList');
  const title = document.getElementById('title');

  function sleep(ms){ return new Promise(res=>setTimeout(res,ms)); }

  async function loadData(){
    // Eagerly load everything to simulate heavy source
    const qs = new URLSearchParams(window.location.search);
    const lat = qs.get('lat') || 0;
    const size = qs.get('size') || 10;
    const tags = await fetch(`/api/tags?lat=${lat}&size=${size}`).then(r=>r.json());
    tagList.innerHTML='';
    tags.forEach(t=>{ const el=document.createElement('span'); el.className='tag'; el.innerText=t; tagList.appendChild(el); })

    const members = await fetch('/api/members').then(r=>r.json());
    memberList.innerHTML='';
    members.forEach(m=>{ const el=document.createElement('div'); el.innerText=m; memberList.appendChild(el); })

    const attaches = await fetch(`/api/attachments?lat=${lat}&size=${size}`).then(r=>r.json());
    attachList.innerHTML='';
    attaches.forEach(a=>{ const el=document.createElement('div'); el.className='attach'; el.innerText=a.name; attachList.appendChild(el); })
  }

  open.addEventListener('click', async ()=>{
    modal.classList.remove('hidden');
    modal.setAttribute('aria-hidden','false');
    window.modalOpenAt = performance.now();
    // Eager, causing blocking
    await loadData();
    window.modalReadyAt = performance.now();
  });

  // simple submit
  document.getElementById('taskForm').addEventListener('submit',(evt)=>{
    evt.preventDefault();
    const payload = {title: title.value, due: document.getElementById('due').value};
    window.taskSubmitAt = performance.now();
    // simulate server api
    fetch('/api/create', {method:'POST',headers:{'content-type':'application/json'}, body: JSON.stringify(payload)}).then(async (r)=>{ if(r.ok){ window.taskDoneAt=performance.now(); alert('Created'); } else { window.taskError = await r.json(); window.taskDoneAt = performance.now(); }});
  });
})();