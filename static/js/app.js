function updateTransport(select, productId) {
  const state = select.value;
  fetch('/api/transport/' + encodeURIComponent(state))
    .then(r => r.json())
    .then(data => {
      const el = document.getElementById('transport-' + productId);
      if (el) el.textContent = '₹' + Number(data.transport).toFixed(2);
    })
    .catch(() => {});
}

setTimeout(() => {
  document.querySelectorAll('.flash').forEach(el => {
    el.style.opacity = '0';
    setTimeout(() => el.remove(), 500);
  });
}, 4500);

/* Text-to-speech for AI descriptions */
function speakText(text) {
  if (!text || !window.speechSynthesis) {
    alert('Speech not supported in this browser.');
    return;
  }
  window.speechSynthesis.cancel();
  const u = new SpeechSynthesisUtterance(text);
  const sel = document.getElementById('aiLanguage');
  const map = {en:'en-IN',hi:'hi-IN',bn:'bn-IN',gu:'gu-IN',mr:'mr-IN',ta:'ta-IN',te:'te-IN',kn:'kn-IN',ml:'ml-IN',pa:'pa-IN'};
  u.lang = map[(sel && sel.value) || 'hi'] || 'hi-IN';
  u.rate = 0.95;
  window.speechSynthesis.speak(u);
}
function stopSpeaking() {
  if (window.speechSynthesis) window.speechSynthesis.cancel();
}
