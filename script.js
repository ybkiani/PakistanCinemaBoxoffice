const DATA_URL="data/movies.json";
let DB={movies:[],sources:[],last_updated:null};
const $=s=>document.querySelector(s);
const esc=s=>String(s??"").replace(/[&<>"']/g,m=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[m]));
async function loadData(){
  $("#statusPill").textContent="Loading cinema feed…";
  try{
    const r=await fetch(DATA_URL+"?v="+Date.now(),{cache:"no-store"});
    if(!r.ok) throw new Error("HTTP "+r.status);
    DB=await r.json();
    render();
    $("#statusPill").textContent="● Feed online";
  }catch(e){
    $("#statusPill").textContent="Feed unavailable";
    $("#lastUpdated").textContent="Could not load "+DATA_URL;
    console.error(e);
  }
}
function filtered(status){
  const q=$("#searchInput").value.toLowerCase().trim(), type=$("#typeFilter").value, city=$("#cityFilter").value;
  return (DB.movies||[]).filter(m=>{
    const hay=[m.title,m.genre,m.cast,m.director,m.language].join(" ").toLowerCase();
    return m.status===status && (!q||hay.includes(q)) && (type==="all"||m.origin===type) && (city==="all"||(m.cities||[]).includes(city));
  });
}
function card(m){
  const bg=m.poster?`style="background-image:url('${esc(m.poster)}')"`:"";
  return `<article class="card" data-id="${esc(m.id)}"><div class="poster ${m.poster?"has-img":""}" ${bg}><span class="badge">${esc(m.origin||"Movie")}</span>${m.poster?"":`<div class="poster-title">${esc(m.title)}</div>`}</div><div class="card-info"><h3>${esc(m.title)}</h3><p>${esc([m.genre,m.language,m.release_date].filter(Boolean).join(" • "))}</p></div></article>`;
}
function renderRail(id,status){
  const a=filtered(status), el=$("#"+id);
  el.innerHTML=a.length?a.map(card).join(""):`<div class="empty">No matching ${status==="now"?"now-showing":"coming-soon"} titles in the current feed.</div>`;
  el.querySelectorAll(".card").forEach(c=>c.onclick=()=>openMovie(c.dataset.id));
}
function render(){
  const dt=DB.last_updated?new Date(DB.last_updated):null;
  $("#lastUpdated").textContent=dt&&!isNaN(dt)?`Last successful update: ${dt.toLocaleString()}`:"Dataset ready";
  $("#movieCount").textContent=`${(DB.movies||[]).length} titles`;
  const cities=[...new Set((DB.movies||[]).flatMap(m=>m.cities||[]))].sort();
  const old=$("#cityFilter").value;
  $("#cityFilter").innerHTML=`<option value="all">All cities</option>`+cities.map(c=>`<option>${esc(c)}</option>`).join("");
  if(cities.includes(old)) $("#cityFilter").value=old;
  $("#sourceList").innerHTML=(DB.sources||[]).map(s=>`<a href="${esc(s.url)}" target="_blank" rel="noopener">${esc(s.name)} ↗</a>`).join("");
  renderRail("nowRail","now"); renderRail("soonRail","soon");
}
function openMovie(id){
  const m=(DB.movies||[]).find(x=>String(x.id)===String(id)); if(!m)return;
  const bg=m.backdrop||m.poster||"";
  $("#dialogBody").innerHTML=`<div class="dialog-hero" ${bg?`style="background-image:linear-gradient(0deg,#10131a 0,transparent 90%),url('${esc(bg)}')"`:""}><div class="eyebrow">${esc(m.status==="now"?"NOW SHOWING":"COMING SOON")}</div><h2>${esc(m.title)}</h2></div><div class="dialog-content"><p>${esc(m.synopsis||"Movie information collected from the current cinema feed.")}</p><div class="dialog-grid"><div class="fact"><b>RELEASE</b>${esc(m.release_date||"—")}</div><div class="fact"><b>LANGUAGE</b>${esc(m.language||"—")}</div><div class="fact"><b>GENRE</b>${esc(m.genre||"—")}</div><div class="fact"><b>RUNTIME</b>${esc(m.runtime||"—")}</div><div class="fact"><b>CAST</b>${esc(m.cast||"—")}</div><div class="fact"><b>CITIES</b>${esc((m.cities||[]).join(", ")||"—")}</div></div></div>`;
  $("#movieDialog").showModal();
}
["searchInput","typeFilter","cityFilter"].forEach(id=>$("#"+id).addEventListener(id==="searchInput"?"input":"change",()=>{renderRail("nowRail","now");renderRail("soonRail","soon")}));
document.querySelectorAll(".rail-buttons button").forEach(b=>b.onclick=()=>$("#"+b.dataset.rail).scrollBy({left:Number(b.dataset.dir)*700,behavior:"smooth"}));
$("#closeDialog").onclick=()=>$("#movieDialog").close();
$("#movieDialog").onclick=e=>{if(e.target===$("#movieDialog"))$("#movieDialog").close()};
$("#refreshBtn").onclick=loadData;
loadData();