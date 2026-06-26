// ===== ALGORITMICA - ANIMATIONS & INTERACTIONS =====

// ===== INTERSECTION OBSERVER - Fade In on Scroll =====
const observerOptions = {
  threshold: 0.1,
  rootMargin: '0px 0px -50px 0px'
};

const fadeObserver = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add('visible');
      fadeObserver.unobserve(entry.target);
    }
  });
}, observerOptions);

document.querySelectorAll('.fade-in').forEach(el => {
  fadeObserver.observe(el);
});

// ===== COUNT-UP ANIMATION =====
function animateCountUp(element) {
  const target = parseFloat(element.dataset.target);
  const prefix = element.dataset.prefix || '';
  const suffix = element.dataset.suffix || '';
  const decimals = parseInt(element.dataset.decimals) || 0;
  const format = element.dataset.format || 'number';
  const duration = 2000;
  const startTime = performance.now();

  function formatNumber(num) {
    if (format === 'compact') {
      if (num >= 1000000) return (num / 1000000).toFixed(1) + 'MI';
      if (num >= 1000) return (num / 1000).toFixed(0) + 'K';
      return Math.round(num).toString();
    }
    if (decimals > 0) {
      return num.toLocaleString('pt-BR', {
        minimumFractionDigits: decimals,
        maximumFractionDigits: decimals
      });
    }
    return Math.round(num).toLocaleString('pt-BR');
  }

  function easeOutQuart(t) {
    return 1 - Math.pow(1 - t, 4);
  }

  function update(currentTime) {
    const elapsed = currentTime - startTime;
    const progress = Math.min(elapsed / duration, 1);
    const easedProgress = easeOutQuart(progress);
    const currentValue = target * easedProgress;

    element.textContent = prefix + formatNumber(currentValue) + suffix;

    if (progress < 1) {
      requestAnimationFrame(update);
    }
  }

  requestAnimationFrame(update);
}

// Observe count-up elements
const countObserver = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      animateCountUp(entry.target);
      countObserver.unobserve(entry.target);
    }
  });
}, { threshold: 0.5 });

document.querySelectorAll('.count-up').forEach(el => {
  countObserver.observe(el);
});

// ===== SMOOTH SCROLL FOR NAV LINKS =====
document.querySelectorAll('.nav-links a').forEach(link => {
  link.addEventListener('click', (e) => {
    e.preventDefault();
    const targetId = link.getAttribute('href');
    const targetEl = document.querySelector(targetId);
    if (targetEl) {
      targetEl.scrollIntoView({ behavior: 'smooth', block: 'start' });
      document.querySelector('.nav-links').classList.remove('active');
    }
  });
});

// ===== NAV BACKGROUND ON SCROLL =====
let lastScroll = 0;
window.addEventListener('scroll', () => {
  const nav = document.querySelector('.nav');
  const scrollTop = window.pageYOffset;

  if (scrollTop > 100) {
    nav.style.borderBottomColor = 'rgba(255,255,255,0.1)';
  } else {
    nav.style.borderBottomColor = 'rgba(255,255,255,0.06)';
  }

  lastScroll = scrollTop;
}, { passive: true });

// ===== KPI CARD HOVER PARALLAX =====
document.querySelectorAll('.kpi-card').forEach(card => {
  card.addEventListener('mousemove', (e) => {
    const rect = card.getBoundingClientRect();
    const x = (e.clientX - rect.left) / rect.width - 0.5;
    const y = (e.clientY - rect.top) / rect.height - 0.5;
    card.style.transform = `translateY(-2px) perspective(500px) rotateX(${-y * 3}deg) rotateY(${x * 3}deg)`;
  });

  card.addEventListener('mouseleave', () => {
    card.style.transform = 'translateY(0) perspective(500px) rotateX(0) rotateY(0)';
  });
});
