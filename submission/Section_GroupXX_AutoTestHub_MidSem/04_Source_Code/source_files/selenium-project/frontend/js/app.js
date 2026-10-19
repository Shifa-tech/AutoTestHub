const $=id=>document.getElementById(id);
const TASKS=[
 {id:'demo',name:'Open Google',desc:'selenium_demo.py · load a page and read its title'},
 {id:'search',name:'Google search',desc:'interactive_selenium.py · search for your own term'},
 {id:'form',name:'Fill demo form',desc:'selenium_form.py · fill, submit and take a screenshot'},
 {id:'auto',name:'Auto-fill for many people',desc:'auto_form_fill.py · loop through a list and log each one'}
];
const S={task:'demo',running:false,stop:false,people:[['Shriya','Agarwal'],['Srishti','Neekhra'],['Shruti','Gupta'],['Shifa','Siddiqui']],
 term:'Shriya',pass:'12345',text:'Shriya',query:'',history:[],file:''};
const speedEl=$('speed');
const sleep=ms=>new Promise(r=>setTimeout(r,ms/ +speedEl.value));
const esc=s=>String(s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
function ts(){return new Date().toLocaleTimeString([], {hour12:false})}
function log(msg,cls=''){const t=$('term');t.insertAdjacentHTML('beforeend',`<span class="t">${ts()}</span> <span class="${cls}">${esc(msg)}</span>\n`);t.scrollTop=t.scrollHeight}
function setStatus(txt,cls=''){const s=$('status');s.textContent=txt;s.className='chip '+cls}
function progress(p){$('prog').style.width=p+'%'}
function nav(url){$('url').textContent=url}
function page(h){$('page').innerHTML=h}

function renderTasks(){
 $('tasks').innerHTML=TASKS.map(t=>`<button class="task" data-id="${t.id}" aria-pressed="${t.id===S.task}"><b>${t.name}</b><span>${t.desc}</span></button>`).join('');
 $('tasks').querySelectorAll('button').forEach(b=>b.onclick=()=>{if(S.running)return;S.task=b.dataset.id;renderTasks();renderOpts()});
}
function renderOpts(){
 const o=$('opts');
 if(S.task==='demo'){$('optTitle').textContent='Inputs';o.innerHTML='<label for="u">Website to open</label><input type="text" id="u" value="https://www.google.com">'}
 else if(S.task==='search'){$('optTitle').textContent='Inputs';o.innerHTML=`<label for="q">Search for anything</label><input type="text" id="q" placeholder="Type anything, e.g. weather in Lucknow" value="${esc(S.query)}"><div class="mini">${['best biryani near me','python tutorial','today news','cricket score'].map(s=>`<button class="sug">${s}</button>`).join('')}</div>`;const q=$('q');q.oninput=e=>S.query=e.target.value;q.onkeydown=e=>{if(e.key==='Enter')run()};o.querySelectorAll('.sug').forEach(b=>b.onclick=()=>{q.value=S.query=b.textContent;q.focus()})}
 else if(S.task==='form'){$('optTitle').textContent='Inputs';o.innerHTML=`<label for="ft">Text box</label><input type="text" id="ft" value="${esc(S.text)}"><label for="fp">Password box</label><input type="password" id="fp" value="${esc(S.pass)}"><p class="note">Demo form only. Don’t enter a real password.</p>`;$('ft').oninput=e=>S.text=e.target.value;$('fp').oninput=e=>S.pass=e.target.value}
 else{$('optTitle').textContent='People to submit';drawPeople()}
}
function drawPeople(){
 $('opts').innerHTML=`<ul class="people" id="pl">${S.people.map((p,i)=>`<li id="p${i}"><span>${esc(p[0])} ${esc(p[1])}</span><button data-i="${i}" aria-label="Remove ${esc(p[0])}">Remove</button></li>`).join('')||'<li class="empty">Add at least one person.</li>'}</ul>
 <div class="row"><input type="text" id="fn" placeholder="First name" aria-label="First name"><input type="text" id="ln" placeholder="Last name" aria-label="Last name"><button id="add">Add</button></div>`;
 $('pl').querySelectorAll('button').forEach(b=>b.onclick=()=>{if(S.running)return;S.people.splice(+b.dataset.i,1);drawPeople()});
 const add=()=>{const f=$('fn').value.trim(),l=$('ln').value.trim();if(!f||!l){log('Enter both a first and last name before adding.','warn');return}S.people.push([f,l]);drawPeople();$('fn').focus()};
 $('add').onclick=add;$('ln').onkeydown=e=>{if(e.key==='Enter')add()};
}

const G=(typed,extra='')=>`<div class="g">Google</div><div class="fake-in focus ${typed!==null?'cursor':''}">${esc(typed||'')}</div>${extra}`;
async function typeInto(target,text,render){let s='';for(const ch of text){s+=ch;render(s);await sleep(70);if(S.stop)return}}
function check(){if(S.stop)throw new Error('stopped')}

async function launch(){
 log('Starting ChromeDriverManager().install() …');await sleep(500);check();
 log('ChromeDriver ready','ok');await sleep(300);check();
 log('webdriver.Chrome(service=service) launched','ok');
 if($('headless').checked)log('Headless: preview hidden','warn');
}
const RUN={
 async demo(){
  const u=($('u').value||'https://www.google.com').trim();
  await launch();progress(30);
  log(`driver.get("${u}")`);nav(u);page('<p class="hint">Loading …</p>');await sleep(900);check();
  page(G(null));progress(70);
  const title=/google/i.test(u)?'Google':new URL(u.startsWith('http')?u:'https://'+u).hostname;
  log(`Title of the page is: ${title}`,'ok');return`Opened ${u} · title “${title}”`;
 },
 async search(){
  const q=S.query.trim();if(!q)throw new Error('Type a search term first.');
  log(`Enter something to search on Google: ${q}`);
  await launch();progress(20);
  log('driver.get("https://www.google.com")');nav('https://www.google.com');page(G(''));await sleep(700);check();
  log('find_element(By.NAME, "q")');await sleep(300);progress(40);
  await typeInto(0,q,s=>page(G(s)));check();
  log('search_box.send_keys(Keys.RETURN)');await sleep(300);progress(70);
  nav('https://www.google.com/search?q='+encodeURIComponent(q));
  page(`<div class="hint" style="margin-bottom:8px">About 12,400,000 results</div>`+[1,2,3].map(i=>`<div class="res"><u>${esc(q)} – result ${i}</u><div class="hint">example${i}.com › ${esc(q.split(' ')[0])}</div></div>`).join(''));
  log('time.sleep(3)  # wait for results');await sleep(1200);check();
  log(`Page title after search: ${q} - Google Search`,'ok');return`Searched “${q}”`;
 },
 async form(){
  await launch();progress(15);
  const u='https://www.selenium.dev/selenium/web/web-form.html';
  log(`driver.get("${u}")`);nav(u);
  const draw=(a,b,btn,msg)=>page(`<h3>Web form</h3><div class="hint">Text input</div><div class="fake-in ${a!==null&&b===null?'focus cursor':''}">${esc(a||'')}</div><div class="hint">Password</div><div class="fake-in ${b!==null?'focus cursor':''}">${'•'.repeat((b||'').length)}</div><span class="fake-btn ${btn?'press':''}">Submit</span>${msg||''}`);
  draw(null,null);await sleep(900);check();progress(30);
  log('find_element(By.NAME, "my-text").send_keys(...)');await typeInto(0,S.text,s=>draw(s,null));check();progress(55);
  log('find_element(By.NAME, "my-password").send_keys(...)');await typeInto(0,S.pass,s=>draw(S.text,s));check();progress(75);
  log('find_element(By.CSS_SELECTOR, "button").click()');draw(S.text,S.pass,true);await sleep(500);
  nav('https://www.selenium.dev/selenium/web/submitted-form.html');
  page('<h3>Form submitted</h3><p>Received!</p><span class="shot">📷 form_result.png</span>');
  log('driver.save_screenshot("form_result.png")','ok');await sleep(600);check();
  log('Form submitted successfully!','ok');log('Page title: Web form - target page','ok');return'Form submitted · screenshot saved';
 },
 async auto(){
  if(!S.people.length)throw new Error('Add at least one person first.');
  await launch();
  S.file='Form Submission Report\n=======================\n\n';$('file').textContent=S.file;
  log('Created log file: form_submissions.txt');
  const url='https://www.w3schools.com/html/tryit.asp?filename=tryhtml_form_submit';
  let n=0;
  for(const [f,l] of S.people){
   check();document.querySelectorAll('.people li').forEach(x=>x.classList.remove('active'));
   const li=$('p'+n);if(li)li.classList.add('active');
   log(`driver.get(form_url)  # reload fresh for ${f}`);nav(url);
   const draw=(a,b,press)=>page(`<h3>HTML form</h3><div class="hint">First name:</div><div class="fake-in ${b===null?'focus cursor':''}">${esc(a)}</div><div class="hint">Last name:</div><div class="fake-in ${b!==null?'focus cursor':''}">${esc(b||'')}</div><span class="fake-btn ${press?'press':''}">Submit</span>`);
   draw('',null);await sleep(500);
   log('WebDriverWait → switched into iframe "iframeResult"');await sleep(400);check();
   await typeInto(0,f,s=>draw(s,null));await typeInto(0,l,s=>draw(f,s));check();
   log('click input[type=\'submit\']');draw(f,l,true);await sleep(400);
   page(`<h3>Result</h3><p>fname=${esc(f)}&amp;lname=${esc(l)}</p>`);
   log(`Form submitted for: ${f} ${l}`,'ok');
   S.file+=`Form submitted for: ${f} ${l}\n`;$('file').textContent=S.file;
   if(li){li.classList.remove('active');li.classList.add('ok')}
   n++;progress(15+85*n/S.people.length);await sleep(600);
  }
  log('driver.quit()');log('All submissions saved in: form_submissions.txt','ok');
  return`Submitted ${n} form${n>1?'s':''}`;
 }
};

async function run(){
 if(S.running)return;
 S.running=true;S.stop=false;progress(0);
 ['run','stop'].forEach(i=>0);$('run').disabled=true;$('stop').disabled=false;setStatus('Running','run');
 const name=TASKS.find(t=>t.id===S.task).name;
 log(`▶ ${name}`);
 if($('headless').checked)$('browserWrap').style.display='none';else $('browserWrap').style.display='';
 let res,cls='done';
 try{res=await (REAL?realRun():RUN[S.task]());progress(100);setStatus('Done','done');if(!REAL)log('driver.quit()  # browser closed','ok')}
 catch(e){
  if(e.message==='stopped'){res='Stopped by you';cls='fail';setStatus('Stopped','fail');log('Run stopped. Browser closed.','warn')}
  else{res=e.message;cls='fail';setStatus('Error','fail');log('Error: '+e.message,'err')}
 }
 S.history.unshift({name,res,cls,t:ts()});drawHist();
 S.running=false;$('run').disabled=false;$('stop').disabled=true;
 if(S.task==='auto')document.querySelectorAll('.people li').forEach(x=>x.classList.remove('active'));
}
function drawHist(){
 $('histEmpty').style.display=S.history.length?'none':'';
 $('hist').innerHTML=S.history.slice(0,20).map(h=>`<li><span><b>${esc(h.name)}</b><br><span style="color:var(--mute)">${esc(h.res)}</span></span><span style="color:var(--${h.cls==='done'?'ok':'err'})">${h.t}</span></li>`).join('');
}
$('run').onclick=run;
$('stop').onclick=()=>{S.stop=true;if(REAL&&RID)fetch('/api/stop/'+RID,{method:'POST'})};
$('clear').onclick=()=>{$('term').innerHTML=''};
speedEl.oninput=()=>$('speedv').textContent=speedEl.value+'×';
$('copy').onclick=async()=>{try{await navigator.clipboard.writeText(S.file||'');$('copy').textContent='Copied';}catch(e){$('copy').textContent='Select the text and copy';}setTimeout(()=>$('copy').textContent='Copy log',1600)};
$('theme').onclick=()=>{const r=document.documentElement,d=getComputedStyle(r).colorScheme.includes('dark');r.dataset.theme=d?'light':'dark'};
renderTasks();renderOpts();drawHist();
log('Ready. Choose a task and press Run task.');

/* ---- Real Chrome mode: active when served by app.py ---- */
let REAL=false,RID=null;
async function realRun(){
 nav('Real Chrome window on your computer');
 page('<p class="hint">Chrome is running on your computer. Watch the window that just opened. Progress appears in the terminal below.</p>');
 const params={query:S.query,text:S.text,pass:S.pass,people:S.people,url:($('u')&&$('u').value)||''};
 const r=await fetch('/api/run',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({task:S.task,headless:$('headless').checked,params})});
 const j=await r.json();if(!r.ok)throw new Error(j.error||'Backend error');
 RID=j.id;let since=0;
 while(true){
  const e=await (await fetch('/api/events/'+RID+'?since='+since)).json();
  e.lines.forEach(l=>log(l.msg,l.cls));since=e.next;progress(e.progress);
  if(e.file!==null&&e.file!==undefined){S.file=e.file;$('file').textContent=S.file}
  if(e.state==='done')return e.result;
  if(e.state==='error')throw new Error(e.error);
  if(e.state==='stopped')throw new Error('stopped');
  await new Promise(r=>setTimeout(r,500));
 }
}
fetch('/api/health').then(r=>r.ok?r.json():Promise.reject()).then(()=>{
 REAL=true;
 document.querySelector('.sub').textContent='Connected to your Python backend. Tasks open a real Chrome window.';
 document.querySelector('.note').textContent='Real mode: every task runs Selenium on this computer.';
 log('Backend connected. Tasks will launch real Chrome.','ok');
}).catch(()=>{});
