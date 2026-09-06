(() => {
  const style = document.createElement('style');
  style.textContent = `.day-map{position:relative}.route-status{position:absolute;z-index:500;left:10px;bottom:10px;margin:0;padding:5px 8px;border-radius:6px;background:#fffdfae8;color:#52645e;font-size:12px;box-shadow:0 2px 8px #17352f22}.ticket-board{margin:0 0 24px;padding:18px 20px;background:#fff8e9;border:1px solid #e7c98f;border-radius:16px}.ticket-board h3{margin:4px 0 9px;font-size:21px}.ticket-item{display:grid;grid-template-columns:auto 1fr auto;gap:10px;align-items:start;padding:12px 0;border-top:1px solid #eadbb8}.ticket-item:first-of-type{border-top:0}.ticket-level{padding:3px 7px;border-radius:20px;background:#7b4020;color:#fff;font-size:11px;font-weight:800;white-space:nowrap}.ticket-item a{color:#1d5145;font-weight:800;white-space:nowrap}.ticket-item p{margin:3px 0 0;color:#62726d;font-size:13px}.xhs-carousel{position:relative;margin-top:14px}.xhs-rail{display:flex;gap:12px;overflow-x:auto;padding:2px 1px 10px;scroll-snap-type:x mandatory;scrollbar-width:thin}.xhs-post{display:block;position:relative;flex:0 0 clamp(220px,26vw,300px);scroll-snap-align:start;text-decoration:none;color:var(--ink);border:1px solid var(--line);border-radius:14px;overflow:hidden;background:#fff;box-shadow:var(--sh)}.xhs-media{position:relative;aspect-ratio:3/4;background:#e8e1d5;overflow:hidden}.xhs-track{display:flex;height:100%;overflow-x:auto;scroll-snap-type:x mandatory;scrollbar-width:none}.xhs-track::-webkit-scrollbar{display:none}.xhs-slide{flex:0 0 100%;width:100%;height:100%;scroll-snap-align:start}.xhs-photo{display:block;width:100%;height:100%;object-fit:cover;background:#e8e1d5}.xhs-media button{position:absolute;z-index:3;top:50%;transform:translateY(-50%);border:0;border-radius:50%;width:30px;height:30px;background:#17352fba;color:#fff;font-size:20px;cursor:pointer}.media-prev{left:8px}.media-next{right:8px}.media-count,.video-badge{position:absolute;z-index:2;right:9px;bottom:9px;padding:3px 7px;border-radius:20px;background:#17352fcc;color:#fff;font-size:11px;font-weight:800}.video-badge{left:9px;right:auto}.xhs-body{padding:11px;font-size:13px}.xhs-body b{display:block;line-height:1.35;margin:5px 0}.xhs-meta{display:flex;justify-content:space-between;gap:6px;color:#8a4a36;font-size:11px;font-weight:800}.food-card{flex-basis:220px;background:#fffaf4}.food-card .xhs-cover{min-height:0;padding:10px;background:linear-gradient(135deg,#bd6c31,#e2a34b)}.travel-discovery{margin-top:16px}.travel-discovery .label{margin-bottom:6px}.route-status a{color:#1d5145;font-weight:800}@media(max-width:720px){.ticket-item{grid-template-columns:1fr}.xhs-post{flex-basis:min(78vw,292px)}}`;
  document.head.appendChild(style);
  style.textContent += '.xhs-link{display:block;color:inherit;text-decoration:none}.xhs-link:focus-visible{outline:3px solid #d49a56;outline-offset:-3px}';

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

  const postCard = (post, index) => {
    const media = post.media?.length ? post.media : post.cover ? [post.cover] : [];
    const slides = media.map((src, i) => `<div class="xhs-slide"><img class="xhs-photo" src="${E(src)}" alt="${E(post.title)} · 第 ${i + 1} 张" loading="lazy" referrerpolicy="no-referrer"></div>`).join('') || '<div class="xhs-cover">小红书精选</div>';
    const controls = media.length > 1 ? `<button class="media-prev" type="button" data-media-shift="-1" aria-label="上一张图片">‹</button><button class="media-next" type="button" data-media-shift="1" aria-label="下一张图片">›</button><span class="media-count">1 / ${media.length}</span>` : '';
    const link = `href="${E(post.url)}" target="_blank" rel="noopener" aria-label="打开小红书笔记：${E(post.title)}"`;
    return `<article class="xhs-post"><div class="xhs-media"><a class="xhs-link" ${link}><div class="xhs-track" data-post="${index}">${slides}</div>${post.type === 'video' ? '<span class="video-badge">▶ 视频 · 在小红书播放</span>' : ''}</a>${controls}</div><a class="xhs-link" ${link}><div class="xhs-body"><div class="xhs-meta"><span>小红书精选</span><span>${E(post.likes || '推荐')} 赞</span></div><b>${E(post.title)}</b><span>${E(post.takeaway)}</span></div></a></article>`;
  };
  const foodCard = activity => `<article class="xhs-post food-card"><div class="xhs-cover">今日吃什么 · ¥${E(activity.meal.perPerson)}/人</div><div class="xhs-body"><div class="xhs-meta"><span>餐厅建议</span><span>${E(activity.meal.cuisine)}</span></div><b>${E(activity.meal.name)}</b><span>${E(activity.meal.recommended || activity.meal.location || '')}</span></div></article>`;
  const discovery = day => {
    const posts = (day.xhs || []).slice(0, 4).map(postCard).join('');
    const foods = day.activities.filter(x => x.meal).slice(0, 2).map(foodCard).join('');
    return posts || foods ? `<div class="xhs-carousel"><div class="xhs-rail">${posts}${foods}</div></div>` : '';
  };
  const renderAdvanceTickets = () => {
    if (!tripData.advanceTickets?.length || document.getElementById('advanceTickets')) return;
    const content = tripData.advanceTickets.map(ticket => `<div class="ticket-item"><span class="ticket-level">${E(ticket.level)}</span><div><b>${E(ticket.day)} · ${E(ticket.name)}</b><p>${E(ticket.action)}</p></div><a href="${E(ticket.url)}" target="_blank" rel="noopener">官方购票 ↗</a></div>`).join('');
    planDays.insertAdjacentHTML('beforebegin', `<section class="ticket-board" id="advanceTickets"><div class="label">Buy ahead</div><h3>这些票请提前处理</h3>${content}</section>`);
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
      if (next?.matches('.xhs-grid,.xhs-carousel')) next.remove();
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
    renderAdvanceTickets();
    enhancePlanning();
    const baseTravel = travel;
    travel = function () { baseTravel(); renderTravelExtras(); };
    document.querySelectorAll('[data-view="travel"]').forEach(button => button.addEventListener('click', () => setTimeout(renderTravelExtras, 0)));
    document.addEventListener('click', event => {
      const control = event.target.closest('[data-media-shift]');
      if (control) {
        event.preventDefault();
        event.stopPropagation();
        const media = control.closest('.xhs-media');
        const track = media?.querySelector('.xhs-track');
        if (!track) return;
        const next = Math.max(0, Math.min(track.children.length - 1, Math.round(track.scrollLeft / track.clientWidth) + Number(control.dataset.mediaShift)));
        track.scrollTo({ left: next * track.clientWidth, behavior: 'smooth' });
        const count = media.querySelector('.media-count');
        if (count) count.textContent = `${next + 1} / ${track.children.length}`;
        return;
      }
      if (event.target.closest('.day-card')) setTimeout(renderTravelExtras, 0);
    });
    if (document.getElementById('travel').classList.contains('active')) travel();
  };
  if (document.readyState !== 'complete') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
