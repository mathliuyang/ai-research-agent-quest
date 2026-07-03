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
    const active=document.activeElement;
    const previewOpen=document.querySelector("[data-video-lightbox].open");
    if(previewOpen || ["INPUT","TEXTAREA","VIDEO"].includes(active.tagName)) return;
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

  const lightbox=document.querySelector("[data-video-lightbox]");
  const lightboxVideo=lightbox ? lightbox.querySelector("video") : null;
  const lightboxTitle=lightbox ? lightbox.querySelector("#lightboxTitle") : null;
  const closeBtn=lightbox ? lightbox.querySelector(".lightbox-close") : null;
  function playDemoLoops(){
    document.querySelectorAll(".demo-card video").forEach(video=>{
      video.play().catch(()=>{});
    });
  }
  function closePreview(){
    if(!lightbox || !lightboxVideo) return;
    lightbox.classList.remove("open");
    lightbox.setAttribute("aria-hidden","true");
    lightboxVideo.pause();
    lightboxVideo.removeAttribute("src");
    lightboxVideo.load();
    playDemoLoops();
  }
  playDemoLoops();
  document.querySelectorAll(".demo-card").forEach(card=>{
    card.addEventListener("click",(e)=>{
      if(!lightbox || !lightboxVideo) return;
      e.preventDefault();
      document.querySelectorAll(".demo-card video").forEach(video=>video.pause());
      lightboxVideo.src=card.dataset.video;
      if(lightboxTitle) lightboxTitle.textContent=card.dataset.title || "演示预览";
      lightbox.classList.add("open");
      lightbox.setAttribute("aria-hidden","false");
      lightboxVideo.focus();
      lightboxVideo.play().catch(()=>{});
    });
  });
  if(closeBtn) closeBtn.addEventListener("click",closePreview);
  if(lightbox){
    lightbox.addEventListener("click",(e)=>{
      if(e.target===lightbox) closePreview();
    });
  }
  document.addEventListener("keydown",(e)=>{
    if(e.key==="Escape" && lightbox && lightbox.classList.contains("open")) closePreview();
  });
})();
