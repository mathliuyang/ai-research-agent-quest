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

  const quest=document.querySelector("[data-tool-quest]");
  const questBtn=quest ? quest.querySelector("[data-quest-next]") : null;
  const questStatus=quest ? quest.querySelector("[data-quest-status]") : null;
  let questStep=0;
  const questMessages=[
    "第 1 关：顶金币砖块，解锁网站工具。",
    "金币到手：网站系列已出现。继续顶蘑菇砖块。",
    "蘑菇到手：浏览器插件系列已出现。继续打败乌龟。",
    "乌龟退场：软件系列已出现。继续爬旗通关。",
    "通关：模型负责理解，工具负责执行，人负责判断。"
  ];

  function resetQuest(){
    questStep=0;
    quest.classList.remove("step-1","step-2","step-3","step-4","unlocked-web","unlocked-plugin","unlocked-software","cleared");
    if(questStatus) questStatus.textContent=questMessages[0];
    questBtn.textContent="START";
  }

  function runQuestStep(){
    if(!quest || !questBtn) return;
    if(questStep>=4){
      resetQuest();
      return;
    }

    questStep=Math.min(questStep+1,4);
    quest.classList.remove("step-1","step-2","step-3","step-4");
    void quest.offsetWidth;
    quest.classList.add(`step-${questStep}`);
    questBtn.disabled=true;
    questBtn.textContent="RUNNING";
    if(questStatus) questStatus.textContent=questMessages[questStep-1];

    const unlockDelay=questStep===4 ? 1500 : 1650;
    setTimeout(()=>{
      if(questStep===1) quest.classList.add("unlocked-web");
      if(questStep===2) quest.classList.add("unlocked-plugin");
      if(questStep===3) quest.classList.add("unlocked-software");
      if(questStep===4){
        quest.classList.add("cleared");
        const finale=quest.querySelector("[data-quest-finale]");
        if(finale && window.matchMedia("(max-width: 680px)").matches){
          setTimeout(()=>finale.scrollIntoView({behavior:"smooth",block:"center"}),120);
        }
      }
      if(questStatus) questStatus.textContent=questMessages[questStep];
      questBtn.disabled=false;
      questBtn.textContent=questStep>=4 ? "REPLAY" : "继续";
    },unlockDelay);
  }

  if(questBtn) questBtn.addEventListener("click",runQuestStep);
  function questIsInView(){
    const rect=quest.getBoundingClientRect();
    return rect.top < window.innerHeight*0.72 && rect.bottom > window.innerHeight*0.18;
  }
  document.addEventListener("keydown",(e)=>{
    if(e.code!=="Space" || !quest || !questBtn) return;
    const active=document.activeElement;
    const previewOpen=document.querySelector("[data-video-lightbox].open");
    if(previewOpen || ["INPUT","TEXTAREA","VIDEO"].includes(active.tagName)) return;
    if(!questIsInView()) return;
    e.preventDefault();
    if(questBtn.disabled || active.tagName==="A") return;
    runQuestStep();
  });
  document.addEventListener("keyup",(e)=>{
    if(e.code==="Space" && quest && questIsInView()) e.preventDefault();
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
