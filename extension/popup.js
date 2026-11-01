const $=id=>document.getElementById(id);
chrome.storage.local.get(['api','token'],v=>{if(v.api)$('#api').value=v.api;if(v.token)$('#token').value=v.token});
$('#save').onclick=async()=>{
 const [tab]=await chrome.tabs.query({active:true,currentWindow:true});
 $('#status').textContent='Reading visible page…';
 chrome.tabs.sendMessage(tab.id,{type:'MEMORA_EXTRACT'},async data=>{
  if(chrome.runtime.lastError||!data){$('#status').textContent='Reload the AI conversation tab and try again.';return}
  try{
   const base=$('#api').value.trim().replace(/\/+$/,'');const target=new URL(base);
   if(target.protocol!=='https:'&&target.hostname!=='127.0.0.1'&&target.hostname!=='localhost')throw new Error('Remote servers must use HTTPS.');
   if(target.protocol==='https:'){const ok=await chrome.permissions.request({origins:[target.origin+'/*']});if(!ok)throw new Error('Server permission was not granted.')}
   const token=$('#token').value.trim();chrome.storage.local.set({api:base,token});
   const headers={'Content-Type':'application/json'};if(token)headers.Authorization='Bearer '+token;
   const response=await fetch(base+'/api/ingest/conversation',{method:'POST',headers,body:JSON.stringify({platform:data.platform,title:data.title,content:data.content,conversation_url:data.url,tags:['browser-capture']})});
   if(!response.ok)throw new Error('API returned HTTP '+response.status);
   $('#status').textContent='Conversation saved to MEMORA.';
  }catch(error){$('#status').textContent='Error: '+error.message}
 });
};