(function(){
  const progress=document.querySelector("[data-progress]");
  const sections=[...document.querySelectorAll("[data-section]")];
  const mapLinks=[...document.querySelectorAll(".map a")];
  function update(){
    const max=document.documentElement.scrollHeight-window.innerHeight;
    const pct=max>0 ? (window.scrollY/max)*100 : 0;
    if(progress) progress.style.width=pct+"%";
    let active="";
    sections.forEach(sec=>{
      if(sec.getBoundingClientRect().top < window.innerHeight*0.42) active=sec.id;
    });
    mapLinks.forEach(a=>a.classList.toggle("active",a.getAttribute("href")==="#"+active));
  }
  window.addEventListener("scroll",update,{passive:true});
  update();

  function go(delta){
    const centers=sections.map(s=>s.offsetTop);
    const current=centers.findIndex((top,i)=>window.scrollY < (centers[i+1] ?? Infinity)-80);
    const next=Math.max(0,Math.min(sections.length-1,current+delta));
    sections[next].scrollIntoView({behavior:"smooth",block:"start"});
  }
  document.addEventListener("keydown",(e)=>{
    if(["INPUT","TEXTAREA"].includes(document.activeElement.tagName)) return;
    if(e.key==="ArrowDown"||e.key==="ArrowRight"){e.preventDefault();go(1);}
    if(e.key==="ArrowUp"||e.key==="ArrowLeft"){e.preventDefault();go(-1);}
    if(e.key==="Home"){e.preventDefault();sections[0].scrollIntoView({behavior:"smooth"});}
    if(e.key==="End"){e.preventDefault();sections[sections.length-1].scrollIntoView({behavior:"smooth"});}
    if(/^[1-5]$/.test(e.key)){
      const target=document.querySelector("#level"+e.key);
      if(target){e.preventDefault();target.scrollIntoView({behavior:"smooth"});}
    }
  });

  document.querySelectorAll("[data-copy]").forEach(btn=>{
    btn.addEventListener("click",async()=>{
      const el=document.getElementById(btn.dataset.copy);
      if(!el) return;
      try{
        await navigator.clipboard.writeText(el.innerText);
        const old=btn.textContent;
        btn.textContent="COPIED";
        setTimeout(()=>btn.textContent=old,1100);
      }catch(err){
        btn.textContent="SELECT TEXT";
      }
    });
  });
})();
