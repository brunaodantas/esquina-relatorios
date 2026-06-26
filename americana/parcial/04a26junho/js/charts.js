// ===== ROCK DAY 2026 — AMERICANA · CHARTS =====

const C = {
  blue:   '#1A3CFF',
  navy:   '#0D1B6E',
  teal:   '#17A697',
  purple: '#7B2FBE',
  warn:   '#CC8800',
  red:    '#CC0000',
  green:  '#1DB954',
  bg:     '#F4F6FF',
  border: 'rgba(0,0,0,0.06)'
};

const fontBase = { family: "'Inter', sans-serif", color: '#555' };

const pluginCenterText = {
  id: 'centerText',
  beforeDraw(chart) {
    if (chart.config.type !== 'doughnut') return;
    const { ctx, data, chartArea: { left, top, right, bottom } } = chart;
    const cx = (left + right) / 2;
    const cy = (top + bottom) / 2;
    const opts = chart.config.options.plugins.centerText;
    if (!opts) return;
    ctx.save();
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillStyle = opts.color || '#111';
    ctx.font = `800 ${opts.fontSize1 || 22}px Inter, sans-serif`;
    ctx.fillText(opts.line1, cx, cy - 12);
    ctx.fillStyle = opts.color2 || '#888';
    ctx.font = `500 ${opts.fontSize2 || 11}px Inter, sans-serif`;
    ctx.fillText(opts.line2, cx, cy + 12);
    ctx.restore();
  }
};
Chart.register(pluginCenterText);

// ===== CHART 1 — Rock Day Meta Doughnut =====
(function() {
  const el = document.getElementById('chartRockDayMeta');
  if (!el) return;
  new Chart(el, {
    type: 'doughnut',
    data: {
      labels: ['Americana', 'Outras Cidades'],
      datasets: [{
        data: [278020, 180628],
        backgroundColor: [C.blue, C.purple],
        borderColor: '#fff',
        borderWidth: 3,
        hoverOffset: 8
      }]
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      cutout: '68%',
      plugins: {
        legend: {
          position: 'right',
          labels: { color: '#555', font: { size: 12, family: 'Inter' }, padding: 16, usePointStyle: true }
        },
        tooltip: {
          backgroundColor: '#fff', titleColor: '#111', bodyColor: '#555',
          borderColor: 'rgba(0,0,0,0.1)', borderWidth: 1,
          callbacks: {
            label: function(ctx) {
              const val = ctx.parsed;
              const total = ctx.dataset.data.reduce((a, b) => a + b, 0);
              const pct = ((val / total) * 100).toFixed(1);
              return ` ${val.toLocaleString('pt-BR')} imp (${pct}%)`;
            }
          }
        },
        centerText: {
          line1: '527.2K',
          line2: 'impressões',
          fontSize1: 20, fontSize2: 11,
          color: '#111', color2: '#888'
        }
      }
    }
  });
})();

// ===== CHART 2 — Criativos Meta (barras horizontais) =====
(function() {
  const el = document.getElementById('chartAnuncios');
  if (!el) return;
  new Chart(el, {
    type: 'bar',
    data: {
      labels: [
        'Novo Endereço — Americana',
        'Novo Endereço — Outras Cidades',
        'Carrossel Rock Day — Americana',
        'Vacina Gripe Liberada',
        'Carrossel Rock Day — Outras Cid.',
        'Dark Post — Mais Segurança',
        'Dark Post — EJA',
        'Progresso Social'
      ],
      datasets: [{
        label: 'Impressões',
        data: [207971, 129572, 70049, 68766, 51056, 33115, 28055, 7127],
        backgroundColor: [
          C.blue, C.purple, C.teal, C.warn,
          'rgba(123,47,190,0.6)', 'rgba(23,166,151,0.5)', 'rgba(204,136,0,0.5)', 'rgba(26,60,255,0.4)'
        ],
        borderRadius: 4,
        borderSkipped: false
      }]
    },
    options: {
      indexAxis: 'y',
      responsive: true, maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: '#fff', titleColor: '#111', bodyColor: '#555',
          borderColor: 'rgba(0,0,0,0.1)', borderWidth: 1,
          callbacks: {
            label: ctx => ` ${ctx.parsed.x.toLocaleString('pt-BR')} impressões`
          }
        }
      },
      scales: {
        x: {
          grid: { color: C.border },
          ticks: {
            color: '#888', font: { size: 11, family: 'Inter' },
            callback: v => v >= 1000 ? (v / 1000).toFixed(0) + 'K' : v
          }
        },
        y: {
          grid: { display: false },
          ticks: { color: '#555', font: { size: 11, family: 'Inter' } }
        }
      }
    }
  });
})();

// ===== CHART 3 — Cobertura Geográfica Google (barras verticais por cidade) =====
(function() {
  const el = document.getElementById('chartGeo');
  if (!el) return;
  new Chart(el, {
    type: 'bar',
    data: {
      labels: ['Americana', 'Campinas', 'Piracicaba', 'Limeira', 'Sta. Bárbara'],
      datasets: [
        {
          label: 'Display',
          data: [4861, 29250, 2526, 2601, 871],
          backgroundColor: C.teal,
          borderRadius: 4, borderSkipped: false
        },
        {
          label: 'Bumper 6s',
          data: [23662, 0, 0, 0, 0],
          backgroundColor: C.red,
          borderRadius: 4, borderSkipped: false
        },
        {
          label: 'TrueView (imp)',
          data: [5500, 1924, 660, 487, 270],
          backgroundColor: C.blue,
          borderRadius: 4, borderSkipped: false
        }
      ]
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'top',
          labels: { color: '#555', font: { size: 12, family: 'Inter' }, padding: 16, usePointStyle: true }
        },
        tooltip: {
          backgroundColor: '#fff', titleColor: '#111', bodyColor: '#555',
          borderColor: 'rgba(0,0,0,0.1)', borderWidth: 1,
          callbacks: {
            label: ctx => ` ${ctx.dataset.label}: ${ctx.parsed.y.toLocaleString('pt-BR')} imp`
          }
        }
      },
      scales: {
        x: {
          stacked: true,
          grid: { display: false },
          ticks: { color: '#555', font: { size: 11, family: 'Inter' } }
        },
        y: {
          stacked: true,
          grid: { color: C.border },
          ticks: {
            color: '#888', font: { size: 11, family: 'Inter' },
            callback: v => v >= 1000 ? (v / 1000).toFixed(0) + 'K' : v
          }
        }
      }
    }
  });
})();
