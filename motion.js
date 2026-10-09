/* V8 enhancements: CSS motion; preserve existing classroom state. */
(function(){
  'use strict';
  const media=window.matchMedia('(prefers-reduced-motion: reduce)');
  const button=document.createElement('button');button.type='button';button.className='wf-motion-control';
  button.setAttribute('aria-label','Toggle interface animations');
  let enabled= !media.matches;
  try{const saved=localStorage.getItem('wf-animations');if(saved==='off')enabled=false;if(saved==='on'&&!media.matches)enabled=true;}catch(_e){}
  function apply(){document.body.classList.toggle('wf-motion-on',enabled&&!media.matches);document.body.classList.toggle('wf-motion-off',!enabled||media.matches);button.textContent=enabled&&!media.matches?'✦ Motion on':'◌ Motion off';button.setAttribute('aria-pressed',String(enabled&&!media.matches));}
  button.addEventListener('click',()=>{enabled=!enabled;try{localStorage.setItem('wf-animations',enabled?'on':'off');}catch(_e){}apply();});
  const nav=document.querySelector('header.top nav');if(nav)nav.appendChild(button);apply();
  if(media.addEventListener)media.addEventListener('change',apply);
  if('IntersectionObserver' in window){const observer=new IntersectionObserver(entries=>{for(const entry of entries){if(entry.isIntersecting){entry.target.classList.add('wf-visible');observer.unobserve(entry.target);}}},{threshold:.04,rootMargin:'0px 0px 80px 0px'});
    const observed=new WeakSet();const scan=()=>{document.querySelectorAll('.card:not(#auth):not(.summary .card),.assignment,.fact-card').forEach(el=>{if(!observed.has(el)){observed.add(el);observer.observe(el);}});};
    scan();const dashboard=document.querySelector('#dashboard');if(dashboard){const mo=new MutationObserver(scan);mo.observe(dashboard,{childList:true,subtree:true});}
  }
  const flip=document.querySelector('.flashcard-body');if(flip){document.querySelectorAll('#flashReveal,#flashAgain,#flashKnow,#flashReset').forEach(el=>{el.addEventListener('click',()=>{if(!document.body.classList.contains('wf-motion-on'))return;flip.classList.remove('is-flipping');void flip.offsetWidth;flip.classList.add('is-flipping');});});flip.addEventListener('animationend',()=>flip.classList.remove('is-flipping'));}
})();
