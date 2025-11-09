
(function(){
  function updateCartCount(){
    try{
      const countEls = document.querySelectorAll('#cart-count');
      const cart = JSON.parse(localStorage.getItem('bm_cart')||'[]');
      const count = cart.reduce((s,i)=>s + (i.qty||0), 0);
      countEls.forEach(el=>el.textContent = count);
    }catch(e){}
  }
  document.addEventListener('DOMContentLoaded', updateCartCount);
  setInterval(updateCartCount, 1000);
})();
