(() => {
  'use strict';
  const menu = document.querySelector('#menu');
  const toggle = document.querySelector('.menu-toggle');
  const closeMenu = () => { if (menu?.open) menu.close(); };
  toggle?.addEventListener('click', () => { menu.showModal(); toggle.setAttribute('aria-expanded', 'true'); document.body.classList.add('menu-open'); });
  menu?.querySelector('[data-close-menu]')?.addEventListener('click', closeMenu);
  menu?.addEventListener('click', e => { if (e.target === menu) { const r = menu.getBoundingClientRect(); if (e.clientX < r.left || e.clientX > r.right || e.clientY < r.top || e.clientY > r.bottom) closeMenu(); } });
  menu?.addEventListener('close', () => { toggle?.setAttribute('aria-expanded', 'false'); document.body.classList.remove('menu-open'); toggle?.focus(); });
  menu?.querySelectorAll('a').forEach(a => a.addEventListener('click', closeMenu));
  const fold = text => text.toLocaleLowerCase('ru').replaceAll('ё', 'е').trim();
  const catalog = document.querySelector('[data-catalog]');
  if (catalog) {
    const search = catalog.querySelector('[data-program-search]');
    const buttons = [...catalog.querySelectorAll('button[data-category]')];
    let category = 'all';
    const update = (save = true) => {
      const query = fold(search.value); let count = 0;
      catalog.querySelectorAll('[data-program]').forEach(row => { const show = (category === 'all' || row.dataset.category === category) && fold(row.dataset.search).includes(query); row.hidden = !show; if (show) count++; });
      buttons.forEach(b => b.setAttribute('aria-pressed', String(b.dataset.category === category)));
      catalog.querySelector('[data-result-count]').textContent = `Найдено направлений: ${count}`;
      catalog.querySelector('[data-program-empty]').hidden = count > 0;
      if (save) { const url = new URL(location.href); category === 'all' ? url.searchParams.delete('category') : url.searchParams.set('category', category); search.value ? url.searchParams.set('q', search.value) : url.searchParams.delete('q'); history.replaceState(null, '', url); }
    };
    const restore = () => { const url = new URL(location.href); category = url.searchParams.get('category') || 'all'; if (!buttons.some(b => b.dataset.category === category)) category = 'all'; search.value = url.searchParams.get('q') || ''; update(false); };
    buttons.forEach(b => b.addEventListener('click', () => { category = b.dataset.category; update(); }));
    search.addEventListener('input', () => update());
    catalog.querySelector('[data-reset-programs]').addEventListener('click', () => { category = 'all'; search.value = ''; update(); search.focus(); });
    window.addEventListener('popstate', restore); restore();
  }
  const teacherSearch = document.querySelector('[data-teacher-search]');
  teacherSearch?.addEventListener('input', () => { let count = 0; document.querySelectorAll('[data-person]').forEach(p => { p.hidden = !fold(p.dataset.search).includes(fold(teacherSearch.value)); if (!p.hidden) count++; }); document.querySelector('[data-teacher-empty]').hidden = count > 0; document.querySelector('[data-teacher-count]').textContent = `Найдено: ${count}`; });
  document.querySelectorAll('[data-inquiry]').forEach(form => {
    let pending = false, submitted = false;
    form.addEventListener('submit', async e => {
      e.preventDefault(); if (pending || submitted || !form.reportValidity()) return;
      const phone = form.elements.phone, digits = phone.value.replace(/\D/g, '');
      phone.setCustomValidity(digits.length === 11 && /^[78]/.test(digits) ? '' : 'Введите российский номер из 11 цифр, начиная с +7 или 8.');
      if (!phone.reportValidity()) return;
      const status = form.querySelector('.form-status'), button = form.querySelector('[type=submit]');
      const label = button.innerHTML; pending = true; button.disabled = true; button.textContent = 'Отправляем…'; form.setAttribute('aria-busy', 'true'); status.className = 'form-status'; status.textContent = 'Отправляем ваше обращение.';
      const controller = new AbortController(); const timeout = setTimeout(() => controller.abort(), 15000);
      try {
        const response = await fetch(form.action, { method: 'POST', body: new FormData(form), headers: { Accept: 'application/json' }, signal: controller.signal });
        const data = await response.json().catch(() => null);
        if (!response.ok || !data?.ok) throw new Error(data?.message || (response.status === 503 ? 'Приём заявок временно недоступен. Позвоните в центр.' : 'Не удалось отправить заявку. Попробуйте позже или позвоните в центр.'));
        submitted = true; status.className = 'form-status success'; status.textContent = 'Заявка получена. Администратор свяжется с вами, чтобы обсудить занятие. Время посещения пока не согласовано.'; button.textContent = 'Заявка отправлена';
      } catch (error) {
        status.className = 'form-status error'; status.textContent = error.name === 'AbortError' ? 'Ответ от сервера не получен. Прежде чем отправлять ещё раз, уточните получение заявки по телефону.' : error instanceof TypeError ? 'Нет связи с сервером. Данные остались в форме — проверьте соединение и попробуйте снова.' : error.message;
      } finally { clearTimeout(timeout); pending = false; form.removeAttribute('aria-busy'); if (!submitted) { button.disabled = false; button.innerHTML = label; } status.focus(); }
    });
    form.elements.phone.addEventListener('input', () => form.elements.phone.setCustomValidity(''));
  });
})();
