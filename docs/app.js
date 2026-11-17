'use strict';
const $ = id => document.getElementById(id);
const esc = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const C = {teal:'#177d69', mint:'#b9dda3', orange:'#efac87', muted:'#aec3b4', ink:'#172e2d', gray:'#a2aba2'};
let DATA;
const names = ['握拳 · 女性','双手点赞','举指 · 女性','托抱圣诞树','手势 / 文本歧义','举指近景','L 形手势','握拳 · 男性'];
function svg(w,h,title,body){return `<svg viewBox="0 0 ${w} ${h}" role="img" aria-label="${esc(title)}"><title>${esc(title)}</title>${body}</svg>`;}
function txt(x,y,value,options=''){return `<text x="${x}" y="${y}" font-size="12" fill="${C.ink}" ${options}>${esc(value)}</text>`;}
function svgText(x,y,value,color=C.muted,size=12,anchor='start'){return `<text x="${x}" y="${y}" fill="${color}" font-size="${size}" text-anchor="${anchor}">${esc(value)}</text>`;}
function line(x1,y1,x2,y2,color,width=1,extra=''){return `<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="${color}" stroke-width="${width}" ${extra}/>`;}
function table(headers,rows){return `<details class="chart-data"><summary>查看数值表</summary><div class="table-scroll"><table><thead><tr>${headers.map(h=>`<th>${esc(h)}</th>`).join('')}</tr></thead><tbody>${rows.map(r=>`<tr>${r.map(c=>`<td>${esc(c)}</td>`).join('')}</tr>`).join('')}</tbody></table></div></details>`;}
function barChart(target, labels, values, max, {dark=false,decimals=3,suffix='',title='',colors=[]}={}){
  const w=480, x0=160, right=435, top=32, row=59, bottom=top+labels.length*row;
  const text=dark?'#cfdfce':C.ink, grid=dark?'#496153':'#dfe5db';
  let b='';
  for(let i=0;i<=4;i++){const x=x0+(right-x0)*i/4;b+=line(x,top-15,x,bottom-22,grid)+svgText(x,bottom+2,(max*i/4).toFixed(max<=1?2:0),text,10,'middle');}
  values.forEach((v,i)=>{const y=top+i*row;b+=svgText(x0-13,y+13,labels[i],text,12,'end');b+=`<rect x="${x0}" y="${y}" width="${(right-x0)*v/max}" height="23" rx="3" fill="${colors[i]|| (dark?C.mint:C.teal)}"><title>${esc(labels[i])}: ${v.toFixed(decimals)}${esc(suffix)}</title></rect>`;b+=svgText(Math.min(right+34,x0+(right-x0)*v/max+8),y+16,v.toFixed(decimals)+suffix,text,12);});
  $(target).innerHTML=svg(w,bottom+22,title,b)+table(['范围',title||'数值'],labels.map((l,i)=>[l,values[i].toFixed(decimals)+suffix]));
}
function charts(){
  const count=DATA.dataset.accepted_pairs, q=DATA.dataset.methods.qwen, pct=q/count;
  const radius=75, circ=2*Math.PI*radius;
  $('dataset-chart').innerHTML=svg(480,225,'人工采用配对来源：Qwen 3947，RealisHuman 507',`<circle cx="113" cy="110" r="${radius}" stroke="#e5c09a" stroke-width="24" fill="none"/><circle cx="113" cy="110" r="${radius}" stroke="${C.teal}" stroke-width="24" fill="none" stroke-dasharray="${pct*circ} ${circ}" transform="rotate(-90 113 110)"/>${svgText(113,110,'4,454',C.ink,31,'middle')}${svgText(113,135,'人工采用配对','#6a7e6e',11,'middle')}<circle cx="240" cy="77" r="5" fill="${C.teal}"/>${svgText(255,82,'Qwen',C.ink,15)}${svgText(255,106,'3,947 对 · 88.6%','#6a7e6e',12)}<circle cx="240" cy="145" r="5" fill="#e5c09a"/>${svgText(255,150,'RealisHuman',C.ink,15)}${svgText(255,174,'507 对 · 11.4%','#6a7e6e',12)}`);
  const xs=[128,256,384,512], train=[.311,.0948,.055,.0286], dev=[.805,.8778,.8805,.9140], left=48, top=30, right=433, bottom=213;
  let b='';
  for(let i=0;i<=4;i++){let v=i/4,y=bottom-(bottom-top)*v;b+=line(left,y,right,y,'#496153',1,i===4?'stroke-dasharray="4 4"':'')+svgText(left-10,y+4,v.toFixed(2),C.muted,10,'end');}
  [train,dev].forEach((values,series)=>{const color=series?C.orange:C.mint;let points=values.map((v,i)=>`${left+(right-left)*i/3},${bottom-(bottom-top)*v}`).join(' ');b+=`<polyline points="${points}" fill="none" stroke="${color}" stroke-width="3"/>`;values.forEach((v,i)=>{let x=left+(right-left)*i/3,y=bottom-(bottom-top)*v;b+=`<circle cx="${x}" cy="${y}" r="5" fill="${color}"/><text x="${x}" y="${y+(series?-12:22)}" fill="${color}" font-size="11" text-anchor="middle">${v.toFixed(i===0?3:4)}</text>`;});});
  xs.forEach((x,i)=>b+=svgText(left+(right-left)*i/3,bottom+38,x,C.muted,11,'middle'));
  b+=svgText(430,273,'优化器更新次数',C.muted,10,'end')+line(55,292,75,292,C.mint,3)+svgText(83,296,'训练 8 对',C.mint,11)+line(233,292,253,292,C.orange,3)+svgText(261,296,'开发 8 对',C.orange,11);
  $('fit-chart').innerHTML=svg(480,315,'端点8对模型的训练与开发误差随更新变化',b)+table(['更新','训练误差比','开发误差比'],xs.map((x,i)=>[x,train[i],dev[i]]));
  barChart('direction-chart',['训练探针 · 8 图','开发 · 32 图','同 prompt 新图 · 32'],['train8','development32','sameprompt32'].map(k=>DATA.direction[k].summary.cosine.mean),1,{dark:true,title:'平均方向余弦',colors:[C.mint,C.orange,C.orange]});
  const direction=DATA.direction.development32.summary;
  barChart('amplitude-chart',['保持 Bad','原幅度 1×','放大 2×','Good 最佳幅度'],[1,direction.error_at_one.mean,direction.error_at_two.mean,direction.oracle_scalar_error.mean],2.5,{dark:true,title:'归一化残差误差',colors:['#849b8b',C.mint,C.orange,'#b6c6a1']});
  barChart('noise-chart',['0 · VAE 重建','0.25 · 部分加噪','0.50 · 部分加噪','0.75 · 部分加噪'],DATA.noise.map(n=>n.group_mean_mask_mae255),35,{dark:true,decimals:2,title:'Good Mask 内 MAE',colors:[C.mint,'#cad5a3','#e3c296',C.orange]});
  barChart('scorer-chart',['图像特征对照','图像 / 伪影 / 骨架','四模块全融合'],['image_only','without_handcraft','all_modules'].map(k=>DATA.scorer[k].classification.all.balanced_accuracy*100),100,{decimals:1,suffix:'%',title:'开发平衡准确率',colors:['#94a999','#6b9a7f',C.teal]});
  const conf=DATA.scorer.all_modules.classification.all;
  $('confusion').innerHTML=`<div></div><div class="cell-label">预测：好</div><div class="cell-label">预测：坏</div><div class="cell-label">人工采用<br>312 张</div><div class="cell"><b>${conf.tp}</b>匹配采用</div><div class="cell error"><b>${conf.fn}</b>漏掉采用</div><div class="cell-label">人工拒绝<br>132 张</div><div class="cell error"><b>${conf.fp}</b>误接受拒绝</div><div class="cell"><b>${conf.tn}</b>识别拒绝</div>`;
  const rows=DATA.score_groups.filter(g=>g.split==='dev8'), max=70, x0=190, x1=865, y0=35, h=43;let c='';
  for(let v=0;v<=70;v+=10){let x=x0+(x1-x0)*v/max;c+=line(x,20,x,366,'#e2e8de')+svgText(x,391,v,'#617270',11,'middle');}
  rows.forEach((r,i)=>{const y=y0+i*h,a=x0+(x1-x0)*r.mean_base/max,z=x0+(x1-x0)*r.mean_lora/max;const col=r.mean_lora>=r.mean_base?C.teal:'#bd6548';c+=svgText(0,y+4,`${i+1}. ${names[i]}`,C.ink,13);c+=line(a,y,z,y,col,4)+`<circle cx="${a}" cy="${y}" r="5.5" fill="#a2aba2"/><circle cx="${z}" cy="${y}" r="6" fill="${C.teal}"/>`;c+=svgText(a,y-11,r.mean_base.toFixed(2),'#77867a',10,'middle')+svgText(z,y+20,r.mean_lora.toFixed(2),C.teal,11,'middle');c+=svgText(944,y+4,(r.mean_lora-r.mean_base>=0?'+':'')+(r.mean_lora-r.mean_base).toFixed(2),col,13,'end');});
  c+=svgText(944,391,'均分变化','#617270',11,'end');
  $('group-score-chart').innerHTML=svg(960,410,'开发8组原模型与LoRA平均评分逐组对照',c)+table(['开发组','原模型均分','LoRA 均分','变化'],rows.map((r,i)=>[`${i+1}. ${names[i]}`,r.mean_base.toFixed(4),r.mean_lora.toFixed(4),(r.mean_lora-r.mean_base).toFixed(4)]));
}
function renderRoutes(filter='全部'){
  const families=['全部',...new Set(DATA.routes.map(r=>r.family))];
  $('route-filters').innerHTML=families.map(f=>`<button data-filter="${esc(f)}" aria-pressed="${filter===f}">${esc(f)}</button>`).join('');
  $('route-list').innerHTML=DATA.routes.filter(r=>filter==='全部'||r.family===filter).map(r=>{
    const danger=/失败|止损|未通过/.test(r.status);
    return `<article class="route-item"><div class="route-date">${esc(r.date)}<b>${esc(r.family)}</b></div><div><div class="route-heading"><h3>${esc(r.name)}</h3><span class="tag ${danger?'danger':/局部|未形成/.test(r.status)?'amber':''}">${esc(r.status)}</span></div><p class="route-method">${esc(r.method)}</p><p class="route-scale">${esc(r.scale)}</p><p class="route-result">${esc(r.result)}</p><a class="route-source" href="evidence/${esc(r.source)}.json">查看证据 ↗</a></div></article>`;
  }).join('');
  $('route-filters').querySelectorAll('button').forEach(btn=>btn.addEventListener('click',()=>renderRoutes(btn.dataset.filter)));
}
function options(el,values,selected){el.innerHTML=values.map(([v,label])=>`<option value="${esc(v)}" ${String(v)===String(selected)?'selected':''}>${esc(label)}</option>`).join('');}
function currentGroup(){return DATA.gallery.find(g=>g.split===$('split').value && g.group===Number($('group').value));}
function updateGroups(){const split=$('split').value;options($('group'),DATA.gallery.filter(g=>g.split===split).map(g=>[g.group,`${g.group+1}. ${split==='dev8'?names[g.group]:'训练示例 '+(g.group+1)}`]),0);updateCheckpoint();}
function updateCheckpoint(){const g=currentGroup(), available=[...new Set(g.records.map(r=>r.variant))];let desired=$('checkpoint').value;const choices=[['step00512','512 更新 · 最终'],['step00256','256 更新'],['step00128','128 更新']].filter(([v])=>available.includes(v));if(!choices.some(([v])=>v===desired))desired='step00512';options($('checkpoint'),choices,desired);updateSeeds();}
function updateSeeds(){const g=currentGroup(),desired=Number($('seed').value),v=$('checkpoint').value;let seeds=g.records.filter(r=>r.variant===v).map(r=>r.seed).sort();options($('seed'),seeds.map(s=>[s,s]),seeds.includes(desired)?desired:seeds[0]);renderGallery();}
function renderGallery(){
  const g=currentGroup(),seed=Number($('seed').value),cp=$('checkpoint').value;
  const matched=g.records.filter(r=>r.variant==='bad_reference'||r.variant==='good_reference'||r.seed===seed&&(r.variant==='base'||r.variant===cp));
  const count=Math.min(...matched.map(r=>r.review_assets.crops.length));let view=$('view').value;
  const views=[['full','整图'],...Array.from({length:count},(_,i)=>[String(i),`手部上下文 ${i+1}`])];if(!views.some(([v])=>v===view))view='full';options($('view'),views,view);
  $('gallery-caption').textContent=`${g.split==='dev8'?'开发':'训练示例'}第 ${g.group+1} 组 · seed ${seed} · ${Number(cp.slice(4))} 更新 · 原 Prompt 保持不变`;
  const variants=[['bad_reference','原始 Bad'],['base','原模型 inpainting'],[cp,'LoRA inpainting'],['good_reference','人工采用 Good']];
  $('image-grid').innerHTML=variants.map(([v,label])=>{const r=matched.find(r=>r.variant===v);if(!r)return `<div class="error-message">该条件没有记录</div>`;const src=view==='full'?r.review_assets.full:r.review_assets.crops[Number(view)];const score=r.score?.quality_score;return `<figure class="image-card ${v===cp?'lora':''}"><figcaption>${esc(label)}<span>${Number.isFinite(score)?score.toFixed(2)+' 分':'参考图'}</span></figcaption><a href="${esc(src)}" target="_blank" rel="noopener" title="打开预览放大"><img src="${esc(src)}" alt="${esc(label)}，${g.split==='dev8'?'开发':'训练示例'}第${g.group+1}组，种子${seed}，${view==='full'?'整图':'手部上下文'}" width="512" height="512"></a></figure>`;}).join('');
  const seeds=g.records.filter(r=>r.variant===cp).sort((a,b)=>a.seed-b.seed);
  $('seed-strip').innerHTML=seeds.map(r=>{const baseline=g.records.find(b=>b.variant==='base'&&b.seed===r.seed);const delta=r.score.quality_score-baseline.score.quality_score;return `<button data-seed="${r.seed}" class="${delta<0?'negative ':''}${r.seed===seed?'selected':''}" aria-pressed="${r.seed===seed}" aria-label="切换到种子${r.seed}，分数差${delta.toFixed(2)}"><small>…${String(r.seed).slice(-3)}</small>${delta>=0?'+':''}${delta.toFixed(1)}</button>`;}).join('');
  $('seed-strip').querySelectorAll('button').forEach(btn=>btn.addEventListener('click',()=>{$('seed').value=btn.dataset.seed;renderGallery();}));
  let note=g.notes, seedNote='';
  if(cp!=='step00512')note=DATA.intermediate_reviews[cp]?.find(n=>n.group===g.group&&n.split===g.split)||{};
  seedNote=note.seed_notes?.find(n=>n.seed===seed)?.note||'';
  $('visual-note').innerHTML=`<strong>已有逐图记录 · 助手视觉初筛</strong>${seedNote?`<p>当前 seed：${esc(seedNote)}</p>`:''}${note.note?`<p>本组 / 检查点：${esc(note.note)}</p>`:''}<p class="scope-note">不是独立人工验收。评分的含义是人工采用偏好预测；姿态与 Good 不同不直接等于解剖错误。</p>`;
  $('prompt-text').innerHTML=`<p lang="en">${esc(g.prompt)}</p><p>${esc(g.sample_id)}</p>`;
}
function preset(group,seed){$('split').value='dev8';updateGroups();$('group').value=String(group);$('checkpoint').value='step00512';updateCheckpoint();$('seed').value=String(seed);$('view').value='0';renderGallery();}
async function init(){
 const response=await fetch('data.json');if(!response.ok)throw new Error('报告数据加载失败');DATA=await response.json();charts();renderRoutes();
 $('sources-list').innerHTML=DATA.sources.map((s,i)=>`<div class="source-item"><span>${String(i+1).padStart(2,'0')}</span><a href="${esc(s.path)}">${esc(s.title)} ↗</a></div>`).join('');
 $('not-completed').innerHTML=DATA.not_completed.map(s=>`<li>${esc(s)}</li>`).join('');
 $('split').addEventListener('change',updateGroups);$('group').addEventListener('change',updateCheckpoint);$('checkpoint').addEventListener('change',updateSeeds);$('seed').addEventListener('change',renderGallery);$('view').addEventListener('change',renderGallery);
 document.querySelectorAll('[data-preset]').forEach(b=>b.addEventListener('click',()=>{let [g,s]=b.dataset.preset.split(',').map(Number);preset(g,s);}));
 $('open-failure').addEventListener('click',()=>{preset(3,2026110509);$('gallery').scrollIntoView({behavior:'smooth'});});
 $('print-page').addEventListener('click',()=>{renderRoutes();window.print();});
 updateGroups();preset(2,2026110502);
 document.documentElement.dataset.ready='true';
}
init().catch(error=>{const e=document.createElement('p');e.className='wrap error-message';e.textContent='交互数据加载失败，请刷新页面，或通过下方证据链接查看原始结果。';$('main').prepend(e);console.error(error);});
