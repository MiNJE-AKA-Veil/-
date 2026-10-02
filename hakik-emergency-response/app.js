(function(){
  // 이미지 라이브러리(IMG)를 <img data-src-id>에 채운다. 같은 그림이 여러 곳에 쓰여도 데이터는 한 번만 내장된다.
  function fill(root){
    (root||document).querySelectorAll('img[data-src-id]').forEach(function(im){
      var id=im.getAttribute('data-src-id');
      if(IMG[id]){im.src=IMG[id];im.removeAttribute('loading');}
      else{im.alt='이미지 누락: '+id;}
    });
  }
  fill();
  // 인쇄 전 모든 이미지를 확실히 로드
  window.addEventListener('beforeprint',function(){fill();});

  // ---- 확대 보기 ----
  var lb=document.getElementById('lb'),lbv=document.getElementById('lbv'),lbi=document.getElementById('lbi'),lbt=document.getElementById('lbt');
  var lastFocus=null,scale=1;
  function open(id,trigger){
    var m=META[id];if(!m||!IMG[id])return;
    lastFocus=trigger||document.activeElement;
    lbi.src=IMG[id];lbi.alt='원문 그림 '+m.no+' '+m.title;
    lbt.textContent='그림 '+m.no+(id.indexOf('-A')>0||id.indexOf('-B')>0?' ('+id.slice(-1)+')':'')+' · 원문 p.'+m.pg+' · '+m.title;
    lb.hidden=false;document.body.style.overflow='hidden';
    setMode('fit');document.getElementById('lbx').focus();
  }
  function close(){
    lb.hidden=true;document.body.style.overflow='';lbi.removeAttribute('src');
    if(lastFocus&&lastFocus.focus)lastFocus.focus();
  }
  function setMode(m){
    lbv.className='lbv '+m;lbi.style.width='';scale=1;
    if(m==='fit')lbi.style.width='';
  }
  function zoom(f){
    if(!lbv.classList.contains('zoomed')){
      scale=lbi.getBoundingClientRect().width/ (lbi.naturalWidth||1);
      lbv.className='lbv zoomed';
    }
    scale=Math.min(4,Math.max(.2,scale*f));
    lbi.style.width=(lbi.naturalWidth*scale)+'px';
  }
  document.addEventListener('click',function(e){
    var b=e.target.closest('[data-fig]');
    if(b){open(b.getAttribute('data-fig'),b);return;}
    if(e.target.id==='lbx')close();
    else if(e.target.id==='lbf')setMode('fit');
    else if(e.target.id==='lbo'){setMode('full');lbi.style.width=lbi.naturalWidth+'px';}
    else if(e.target.id==='lbp')zoom(1.25);
    else if(e.target.id==='lbm')zoom(.8);
    else if(e.target===lbv)close();
  });
  document.addEventListener('keydown',function(e){
    if(lb.hidden)return;
    if(e.key==='Escape'){e.preventDefault();close();}
    else if(e.key==='+'||e.key==='=')zoom(1.25);
    else if(e.key==='-')zoom(.8);
    else if(e.key==='Tab'){ // 포커스를 확대 창 안에 유지
      var f=lb.querySelectorAll('button');if(!f.length)return;
      var first=f[0],last=f[f.length-1];
      if(e.shiftKey&&document.activeElement===first){e.preventDefault();last.focus();}
      else if(!e.shiftKey&&document.activeElement===last){e.preventDefault();first.focus();}
    }
  });

  // ---- 원문 문장 펼치기/접기 ----
  var allOpen=false,btn=document.getElementById('btnOrig');
  btn.addEventListener('click',function(){
    allOpen=!allOpen;
    document.querySelectorAll('details.orig').forEach(function(d){d.open=allOpen;});
    btn.textContent=allOpen?'원문 문장 모두 접기':'원문 문장 모두 펼치기';
  });
  document.getElementById('btnPrint').addEventListener('click',function(){
    document.querySelectorAll('details.fcd').forEach(function(d){d.open=true;});
    fill();window.print();
  });
  window.addEventListener('beforeprint',function(){document.querySelectorAll('details.fcd').forEach(function(d){d.open=true;});});

  // ---- 목차 현재 위치 강조 ----
  var links={};document.querySelectorAll('#toc a[href^="#"]').forEach(function(a){links[a.getAttribute('href').slice(1)]=a;});
  if('IntersectionObserver' in window){
    var io=new IntersectionObserver(function(es){
      es.forEach(function(en){
        if(en.isIntersecting){
          Object.keys(links).forEach(function(k){links[k].classList.remove('on');});
          var l=links[en.target.id];if(l)l.classList.add('on');
        }
      });
    },{rootMargin:'-130px 0px -70% 0px'});
    document.querySelectorAll('section.sec,section.case').forEach(function(s){io.observe(s);});
  }
})();
