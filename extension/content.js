function extractVisibleConversation(){
 const selectors=['[data-message-author-role]','[data-testid*=conversation-turn]','main'];
 for(const selector of selectors){
  const text=[...document.querySelectorAll(selector)].map(node=>node.innerText||'').filter(Boolean).join('\n\n');
  if(text.length>80)return text.slice(0,100000);
 }
 return (document.body?.innerText||'').slice(0,100000);
}
chrome.runtime.onMessage.addListener((message,sender,reply)=>{
 if(message?.type==='MEMORA_EXTRACT'){
  reply({content:extractVisibleConversation(),title:document.title,url:location.href,
   platform:location.hostname.includes('claude')?'claude':location.hostname.includes('gemini')?'gemini':'chatgpt'});
 }
 return true;
});