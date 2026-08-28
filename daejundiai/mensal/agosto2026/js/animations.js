/* Fade-in on scroll */
const fadeObs = new IntersectionObserver(entries => entries.forEach(x => {
  if (x.isIntersecting) { x.target.classList.add('visible'); fadeObs.unobserve(x.target); }
}), { threshold: .12 });
document.querySelectorAll('.fade-in').forEach(el => fadeObs.observe(el));

/* Progress bars on scroll */
const barObs = new IntersectionObserver(entries => entries.forEach(x => {
  if (!x.isIntersecting) return;
  const el = x.target;
  setTimeout(() => { el.style.width = el.dataset.w || '0%'; }, 200);
  barObs.unobserve(el);
}), { threshold: .4 });
document.querySelectorAll('.bar-fill').forEach(el => barObs.observe(el));

/* Count-up on hero pills */
function countUp(el) {
  const target = parseInt(el.dataset.count, 10);
  if (isNaN(target)) return;
  const duration = 1400;
  const start = performance.now();
  function tick(now) {
    const progress = Math.min((now - start) / duration, 1);
    const value = Math.floor(progress * target);
    el.textContent = value.toLocaleString('pt-BR');
    if (progress < 1) requestAnimationFrame(tick);
    else el.textContent = target.toLocaleString('pt-BR');
  }
  requestAnimationFrame(tick);
}
document.querySelectorAll('[data-count]').forEach(countUp);

/* Carrossel */
let acIdx = 0;
function acMove(dir) { acGoTo((acIdx + dir + 4) % 4); }
function acGoTo(i) {
  acIdx = i;
  document.getElementById('acTrack').style.transform = 'translateX(-' + (i * 100) + '%)';
  document.querySelectorAll('.ac-dot').forEach(function (d, j) { d.classList.toggle('active', j === i); });
}

/* Placeholder fallback for broken creative images */
document.querySelectorAll('.ad-img img').forEach(img => {
  img.addEventListener('error', function () {
    this.style.display = 'none';
  });
});
