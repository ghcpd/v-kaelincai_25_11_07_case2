(function(){
  const open = document.getElementById('openModal');
  const wizard = document.getElementById('wizard');
  const stepNo = document.getElementById('stepNo');

  function sleep(ms){ return new Promise(res=>setTimeout(res,ms)); }

  async function loadMembers(){
    const resp = await fetch('/api/members');
    const mems = await resp.json();
    const el = document.getElementById('memberList'); el.innerHTML=''; mems.forEach(m=>el.appendChild(Object.assign(document.createElement('div'), {innerText:m}))); }

  async function lazyLoadExtras(){
    // lazy: tags and attachments only load on final step
    const qs = new URLSearchParams(window.location.search);
    const lat = qs.get('lat') || '0';
    const size = qs.get('size') || '10';
    const tags = await fetch('/api/tags?lat='+lat+'&size='+size).then(r=>r.json());
    const tdom = document.getElementById('tagList'); tdom.innerHTML=''; tags.forEach(t=>{ const el=document.createElement('span'); el.className='tag'; el.innerText=t; tdom.appendChild(el);});
    const attaches = await fetch('/api/attachments?lat='+lat+'&size='+size).then(r=>r.json());
    const adom = document.getElementById('attachList'); adom.innerHTML=''; attaches.forEach(a=>{ const el=document.createElement('div'); el.className='attach'; el.innerText=a.name; adom.appendChild(el); });
  }

  function showStep(n){
    document.querySelectorAll('.step').forEach(s=>s.classList.add('hidden'));
    const s = document.querySelector('.step[data-step="'+n+'"]'); s.classList.remove('hidden'); stepNo.innerText=n;
  }

  open.addEventListener('click', async ()=>{
    wizard.classList.remove('hidden');
    window.modalOpenAt = performance.now();
    showStep(1);
    // preload lightweight members
    await loadMembers();
    window.modalReadyAt = performance.now();
  });

  document.getElementById('next1').addEventListener('click', ()=> showStep(2));
  document.getElementById('next2').addEventListener('click', ()=> showStep(3));
  document.getElementById('prev2').addEventListener('click', ()=> showStep(1));
  document.getElementById('prev3').addEventListener('click', ()=> showStep(2));

  document.getElementById('finish').addEventListener('click', async ()=>{
    window.taskSubmitAt = performance.now();
    // lazy load extras only now
    await lazyLoadExtras();
    const payload = {title: document.getElementById('title').value, due: document.getElementById('due').value};
    const r = await fetch('/api/create',{method:'POST', headers:{'content-type':'application/json'}, body: JSON.stringify(payload)});
    if(r.ok){ window.taskDoneAt = performance.now(); } else { window.taskError = await r.json(); window.taskDoneAt = performance.now(); }
  });
})();