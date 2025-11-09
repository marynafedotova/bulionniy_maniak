fetch('products.json').then(r => r.json()).then(products => {
  const tpl = document.getElementById('product-card');

  products.forEach(p => {
    const node = tpl.content.cloneNode(true);
    node.querySelector('.card-img').src = p.image || 'assets/placeholder.jpg';
    node.querySelector('.card-img').alt = p.title;
    node.querySelector('.card-title').textContent = p.title;
    node.querySelector('.card-desc').textContent = p.description;
    node.querySelector('.card-price').textContent = Math.round(p.price) + ' грн';

    // Добавление в корзину
    node.querySelector('.add-btn').addEventListener('click', () => {
      const cart = JSON.parse(localStorage.getItem('bm_cart') || '[]');
      const existing = cart.find(i => i.id === p.id);
      if (existing) existing.qty += 1;
      else cart.push({ id: p.id, title: p.title, price: p.price, qty: 1 });
      localStorage.setItem('bm_cart', JSON.stringify(cart));
      toast.success('Додано в кошик');
      document.querySelectorAll('#cart-count').forEach(el => el.textContent = cart.reduce((s, i) => s + i.qty, 0));
    });

    // Детали модального окна
    node.querySelector('.details-btn').addEventListener('click', () => {
      document.getElementById('modal-img').src = p.image || 'assets/placeholder.jpg';
      document.getElementById('modal-title').textContent = p.title;
      document.getElementById('modal-desc').textContent = p.description;
      document.getElementById('modal-price').textContent = Math.round(p.price);
      document.getElementById('modal').classList.remove('hidden');
      document.getElementById('modal-add').onclick = () => {
        const qty = Number(document.getElementById('modal-qty').value || 1);
        const cart = JSON.parse(localStorage.getItem('bm_cart') || '[]');
        const existing = cart.find(i => i.id === p.id);
        if (existing) existing.qty += qty;
        else cart.push({ id: p.id, title: p.title, price: p.price, qty: qty });
        localStorage.setItem('bm_cart', JSON.stringify(cart));
        document.getElementById('modal').classList.add('hidden');
        toast.success('Додано в кошик');
      };
    });

    // Вставка карточки в категорию
    const categoryDiv = document.getElementById(p.category);
    if (categoryDiv) categoryDiv.appendChild(node);
  });
});

// Закрытие модального окна
document.addEventListener('click', e => {
  if (e.target.matches('.modal-close') || e.target.matches('.modal')) {
    document.getElementById('modal').classList.add('hidden');
  }
});
