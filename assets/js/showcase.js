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
  function activeVideoForKeys(){
    const fullscreen=document.fullscreenElement || document.webkitFullscreenElement || document.msFullscreenElement;
    if(fullscreen){
      if(fullscreen.matches && fullscreen.matches("video")) return fullscreen;
      if(fullscreen.querySelector) return fullscreen.querySelector("video");
    }
    return document.activeElement && document.activeElement.tagName==="VIDEO" ? document.activeElement : null;
  }
  function seekVideo(video, seconds){
    if(!video || !Number.isFinite(video.duration)) return;
    video.currentTime=Math.max(0,Math.min(video.duration,video.currentTime+seconds));
  }
  document.addEventListener("keydown",(e)=>{
    const video=activeVideoForKeys();
    if(!video || (e.key!=="ArrowLeft" && e.key!=="ArrowRight")) return;
    e.preventDefault();
    e.stopPropagation();
    seekVideo(video,e.key==="ArrowRight" ? 10 : -10);
  },true);
  document.addEventListener("keydown",(e)=>{
    const active=document.activeElement;
    const previewOpen=document.querySelector("[data-video-lightbox].open");
    if(previewOpen || ["INPUT","TEXTAREA","VIDEO"].includes(active.tagName)) return;
    if(e.key==="ArrowDown"||e.key==="ArrowRight"){e.preventDefault();go(1);}
    if(e.key==="ArrowUp"||e.key==="ArrowLeft"){e.preventDefault();go(-1);}
    if(e.key==="Home"){e.preventDefault();sections[0].scrollIntoView({behavior:"smooth"});}
    if(e.key==="End"){e.preventDefault();sections[sections.length-1].scrollIntoView({behavior:"smooth"});}
    if(/^[1-3]$/.test(e.key)){
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

  const treasureStage=document.querySelector("[data-treasure-stage]");
  const treasureToggle=treasureStage ? treasureStage.querySelector("[data-treasure-toggle]") : null;
  const treasureHint=treasureStage ? treasureStage.querySelector("[data-treasure-hint]") : null;
  const treasureItems=treasureStage ? [...treasureStage.querySelectorAll(".treasure-item")] : [];
  const treasureDetail=treasureStage ? treasureStage.querySelector("[data-treasure-detail]") : null;
  const mobileTreasure=()=>window.matchMedia("(max-width: 680px)").matches;

  function setTreasureDetail(item){
    if(!treasureDetail || !item) return;
    const title=item.querySelector("span")?.textContent || "";
    const kind=item.querySelector("strong")?.textContent || "";
    const desc=item.querySelector("p")?.textContent || "";
    const link=treasureDetail.querySelector("a");
    treasureDetail.querySelector("b").textContent=`${title} · ${kind}`;
    treasureDetail.querySelector("span").textContent=desc;
    if(link) link.href=item.href;
  }
  function clearTreasureActive(){
    treasureItems.forEach(item=>item.classList.remove("active"));
  }
  function openTreasure(){
    if(!treasureStage || !treasureToggle) return;
    treasureStage.classList.remove("opened");
    void treasureStage.offsetWidth;
    treasureStage.classList.add("opened");
    treasureToggle.setAttribute("aria-expanded","true");
    if(treasureHint) treasureHint.textContent="重新开启补给箱";
    clearTreasureActive();
    if(treasureDetail){
      treasureDetail.querySelector("b").textContent="点一个图标查看简介";
      treasureDetail.querySelector("span").textContent="网站、插件和软件会分批从宝箱里蹦出来。";
      const link=treasureDetail.querySelector("a");
      if(link) link.href="#";
    }
  }
  if(treasureToggle) treasureToggle.addEventListener("click",openTreasure);
  treasureItems.forEach(item=>{
    item.addEventListener("click",(e)=>{
      if(!mobileTreasure()) return;
      e.preventDefault();
      if(!treasureStage.classList.contains("opened")) openTreasure();
      clearTreasureActive();
      item.classList.add("active");
      setTreasureDetail(item);
    });
    item.addEventListener("focus",()=>{
      if(mobileTreasure()) setTreasureDetail(item);
    });
  });

  const lightbox=document.querySelector("[data-video-lightbox]");
  const lightboxVideo=lightbox ? lightbox.querySelector("video") : null;
  const lightboxTitle=lightbox ? lightbox.querySelector("#lightboxTitle") : null;
  const closeBtn=lightbox ? lightbox.querySelector(".lightbox-close") : null;
  function playDemoLoops(){
    document.querySelectorAll(".demo-card video[autoplay]").forEach(video=>{
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
    if(e.key==="Escape" && treasureStage) clearTreasureActive();
  });
})();
