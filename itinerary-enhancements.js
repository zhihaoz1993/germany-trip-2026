(() => {
  const style = document.createElement('style');
  style.textContent = `.day-map{position:relative}.route-status{position:absolute;z-index:500;left:10px;bottom:10px;margin:0;padding:5px 8px;border-radius:6px;background:#fffdfae8;color:#52645e;font-size:12px;box-shadow:0 2px 8px #17352f22}.xhs-grid{align-items:stretch}.xhs-card{position:relative}.xhs-photo{display:block;width:100%;height:156px;object-fit:cover;background:#e8e1d5}.xhs-meta{display:flex;justify-content:space-between;gap:6px;color:#8a4a36;font-size:11px;font-weight:800}.food-card{background:#fffaf4}.food-card .xhs-cover{min-height:0;padding:10px;background:linear-gradient(135deg,#bd6c31,#e2a34b)}.travel-discovery{margin-top:16px}.travel-discovery .label{margin-bottom:6px}.route-status a{color:#1d5145;font-weight:800}@media(max-width:720px){.xhs-photo{height:180px}}`;
  document.head.appendChild(style);

  Object.assign(geo, {
    'Munich Marriott Hotel, Munich, Germany': [48.171, 11.593],
    'Marienplatz, Munich, Germany': [48.137, 11.576],
    'English Garden, Munich, Germany': [48.160, 11.603]
  });

  const pointsFor = d => (d.route?.mapPts || []).map(name => ({ name, ll: geo[name] })).filter(x => x.ll);
  const status = (el, message, withNav) => {
    const nav = withNav && el.dataset.day ? '' : '';
    el.insertAdjacentHTML('beforeend', `<p class="route-status">${E(message)}${withNav ? ` · <a href="${E(url(withNav))}" target="_blank" rel="noopener">打开导航</a>` : nav}</p>`);
  };
  const cleanMap = el => {
    const next = el.cloneNode(false);
    el.replaceWith(next);
    return next;
  };
  const drawDrivingMap = (mount, day) => {
    mount = cleanMap(mount);
    const points = pointsFor(day);
    if (!day.route || points.length < 2) {
      mount.textContent = '本日没有需要自驾的路段。';
      return mount;
    }
    if (!window.L) {
      mount.classList.add('map-fallback');
      mount.textContent = '路线地图未能加载；请使用上方“打开导航”获取驾车路线。';
      return mount;
    }
    const map = L.map(mount, { scrollWheelZoom: false, attributionControl: true });
    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', { attribution: '© OpenStreetMap contributors' }).addTo(map);
    const direct = L.polyline(points.map(x => x.ll), { color: '#78978d', weight: 3, dashArray: '7 8', opacity: .8 }).addTo(map);
    L.marker(points[0].ll).addTo(map).bindTooltip('出发');
    L.marker(points[points.length - 1].ll).addTo(map).bindTooltip('抵达');
    map.fitBounds(direct.getBounds(), { padding: [26, 26] });
    status(mount, '正在加载实际驾车线路…');
    const coordinates = points.map(x => `${x.ll[1]},${x.ll[0]}`).join(';');
    fetch(`https://router.project-osrm.org/route/v1/driving/${coordinates}?overview=full&geometries=geojson`)
      .then(r => r.ok ? r.json() : Promise.reject(new Error('route unavailable')))
      .then(data => {
        const line = data.routes?.[0]?.geometry?.coordinates;
        if (!line?.length) throw new Error('route unavailable');
        const driving = line.map(([lng, lat]) => [lat, lng]);
        direct.setLatLngs(driving).setStyle({ color: '#1d5145', weight: 4, dashArray: null, opacity: 1 });
        map.fitBounds(direct.getBounds(), { padding: [26, 26] });
        mount.querySelector('.route-status')?.remove();
      })
      .catch(() => {
        const notice = mount.querySelector('.route-status');
        if (notice) notice.innerHTML = `实际驾车线路暂不可用；虚线仅示意站点顺序 · <a href="${E(url(day))}" target="_blank" rel="noopener">打开导航</a>`;
      });
    setTimeout(() => map.invalidateSize(), 80);
    return mount;
  };

  const postCard = post => `<a class="xhs-card" href="${E(post.url)}" target="_blank" rel="noopener" aria-label="打开小红书笔记：${E(post.title)}">${post.cover ? `<img class="xhs-photo" src="${E(post.cover)}" alt="${E(post.title)} 的小红书封面" loading="lazy" referrerpolicy="no-referrer">` : '<div class="xhs-cover">小红书精选</div>'}<div class="xhs-body"><div class="xhs-meta"><span>小红书精选</span><span>${E(post.likes || '推荐')} 赞</span></div><b>${E(post.title)}</b><span>${E(post.takeaway)}</span></div></a>`;
  const foodCard = activity => `<div class="xhs-card food-card"><div class="xhs-cover">今日吃什么 · ¥${E(activity.meal.perPerson)}/人</div><div class="xhs-body"><b>${E(activity.meal.name)}</b><span>${E(activity.meal.cuisine)} · ${E(activity.meal.recommended || activity.meal.location || '')}</span></div></div>`;
  const discovery = day => {
    const posts = (day.xhs || []).slice(0, 2).map(postCard).join('');
    const foods = day.activities.filter(x => x.meal).slice(0, 2).map(foodCard).join('');
    return posts || foods ? `<div class="xhs-grid">${posts}${foods}</div>` : '';
  };

  const enhancePlanning = () => {
    [...document.querySelectorAll('#planDays > details')].forEach((detail, index) => {
      const day = tripData.days[index];
      let map = detail.querySelector('[data-day-map]');
      if (!map) {
        detail.insertAdjacentHTML('beforeend', `<div class="day-map" data-day-map="${index}"></div>`);
        map = detail.querySelector('[data-day-map]');
      }
      let next = map.nextElementSibling;
      if (next?.matches('.xhs-grid')) next.remove();
      const cards = discovery(day);
      if (cards) map.insertAdjacentHTML('afterend', cards);
      detail.addEventListener('toggle', () => {
        if (detail.open) setTimeout(() => drawDrivingMap(detail.querySelector('[data-day-map]'), day), 0);
      });
    });
  };

  const renderTravelExtras = () => {
    const day = tripData.days[selected];
    document.getElementById('activeDayMap')?.remove();
    document.getElementById('travelDiscovery')?.remove();
    const routeBox = document.querySelector('#today .route-box');
    const cols = document.querySelector('#today .cols');
    if (routeBox) routeBox.insertAdjacentHTML('afterend', '<div class="day-map" id="activeDayMap" aria-label="本日驾车路线图"></div>');
    if (cols) cols.insertAdjacentHTML('afterend', `<section class="travel-discovery" id="travelDiscovery"><div class="label">今日灵感 · 小红书与餐厅</div>${discovery(day)}</section>`);
    const section = document.getElementById('travel');
    if (routeBox && section.classList.contains('active')) setTimeout(() => drawDrivingMap(document.getElementById('activeDayMap'), day), 0);
  };

  const init = () => {
    const carBooking = document.querySelector('[data-b="car"]');
    if (carBooking) {
      carBooking.checked = true;
      const badge = carBooking.closest('.booking')?.querySelector('.status');
      if (badge) { badge.classList.add('done'); badge.textContent = '已确认'; }
    }
    enhancePlanning();
    const baseTravel = travel;
    travel = function () { baseTravel(); renderTravelExtras(); };
    document.querySelectorAll('[data-view="travel"]').forEach(button => button.addEventListener('click', () => setTimeout(renderTravelExtras, 0)));
    document.addEventListener('click', event => { if (event.target.closest('.day-card')) setTimeout(renderTravelExtras, 0); });
    if (document.getElementById('travel').classList.contains('active')) travel();
  };
  if (document.readyState !== 'complete') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
