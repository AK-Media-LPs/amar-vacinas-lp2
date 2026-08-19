/* Amar Vacinas — animações da LP (reveals no scroll, trilha da Solução, parallax).
   Porte vanilla da lógica do protótipo; sem React, sem dependências. */
(function () {
  'use strict';

  var R = {};
  document.querySelectorAll('[data-ref]').forEach(function (el) {
    R[el.getAttribute('data-ref')] = el;
  });
  var reveals = Array.prototype.slice.call(document.querySelectorAll('[data-rv]'));
  var floaters = Array.prototype.slice.call(document.querySelectorAll('[data-mas]'));

  var motionOff = matchMedia('(prefers-reduced-motion: reduce)').matches;
  var vh = innerHeight;
  var stepReady = false, stepW = 0, stepL = 0;

  floaters.forEach(function (el) {
    el.style.animationPlayState = motionOff ? 'paused' : 'running';
  });

  /* ---------------------------------------------------------------- reveals */
  function hideEl(el) {
    var t = el.dataset.rv || 'up';
    el.style.transition = 'none';
    if (t === 'mask') el.style.transform = 'translateY(110%)';
    else if (t === 'clip') {
      el.style.clipPath = 'inset(0 0 100% 0)';
      el.style.transform = 'translateY(16px)';
    } else if (t === 'mark') {
      el.style.background = '#FFFFFF';
      el.style.borderColor = '#E4E9FF';
      el.style.color = '#22317E';
    } else {
      el.style.opacity = '0';
      el.style.transform = 'translateY(26px)';
    }
  }

  function showEl(el) {
    var t = el.dataset.rv || 'up';
    var d = (el.dataset.rd || '0') + 'ms';
    el.style.transition =
      'transform 0.95s cubic-bezier(.22,.61,.21,1) ' + d +
      ', opacity 0.8s ease ' + d +
      ', clip-path 0.95s cubic-bezier(.22,.61,.21,1) ' + d +
      ', background 0.5s ease ' + d +
      ', border-color 0.5s ease ' + d +
      ', color 0.5s ease ' + d;
    if (t === 'mask') el.style.transform = 'translateY(0%)';
    else if (t === 'clip') {
      el.style.clipPath = 'inset(-12% -6% -14% -6%)';
      el.style.transform = 'translateY(0)';
    } else if (t === 'mark') {
      el.style.background = '#3C5DFA';
      el.style.borderColor = '#3C5DFA';
      el.style.color = '#FFFFFF';
    } else {
      el.style.opacity = '1';
      el.style.transform = 'translateY(0)';
    }
  }

  var io = null;
  function setupReveals() {
    if (motionOff) return;
    var proxy = new Map();
    io = new IntersectionObserver(function (ents) {
      ents.forEach(function (e) {
        if (!e.isIntersecting) return;
        showEl(proxy.get(e.target) || e.target);
        io.unobserve(e.target);
      });
    }, { threshold: 0.15, rootMargin: '0px 0px -8% 0px' });

    reveals.forEach(function (el) {
      var r = el.getBoundingClientRect();
      hideEl(el);
      if (r.top < vh * 0.95 && r.bottom > 0) {
        requestAnimationFrame(function () {
          requestAnimationFrame(function () { showEl(el); });
        });
      } else {
        var t = el.dataset.rv || 'up';
        var obs = (t === 'mask' || t === 'clip') && el.parentElement ? el.parentElement : el;
        proxy.set(obs, el);
        io.observe(obs);
      }
    });
  }

  /* ------------------------------------------------- trilha da Solução (SVG) */
  function setupSteps() {
    var svg = R.stepSvg;
    if (!svg || !R.stepBase) return;
    if (!matchMedia('(min-width: 901px)').matches) { stepReady = false; return; }
    var box = svg.getBoundingClientRect();
    var w = Math.max(300, Math.round(box.width));
    var h = Math.max(48, Math.round(box.height));
    svg.setAttribute('width', w);
    svg.setAttribute('height', h);
    svg.setAttribute('viewBox', '0 0 ' + w + ' ' + h);
    var d = 'M 0 ' + h * 0.5 +
      ' C ' + w * 0.17 + ' ' + h * 0.15 + ', ' + w * 0.33 + ' ' + h * 0.92 +
      ', ' + w * 0.5 + ' ' + h * 0.52 +
      ' C ' + w * 0.66 + ' ' + h * 0.14 + ', ' + w * 0.82 + ' ' + h * 0.88 +
      ', ' + w * 0.97 + ' ' + h * 0.45;
    R.stepBase.setAttribute('d', d);
    R.stepLit.setAttribute('d', d);
    R.stepClip.setAttribute('height', h);
    stepW = w;
    stepL = R.stepLit.getTotalLength();
    stepReady = true;
    if (motionOff) {
      R.stepClip.setAttribute('width', w);
      var pt = R.stepLit.getPointAtLength(stepL);
      R.stepMas.style.transform =
        'translate(' + (pt.x - 40).toFixed(1) + 'px, ' + (pt.y - 94).toFixed(1) + 'px)';
    }
  }

  /* -------------------------------------------------------------- parallaxes */
  function update() {
    if (motionOff) return;

    if (R.painWrap && R.prob) {
      var r = R.prob.getBoundingClientRect();
      if (r.bottom > 0 && r.top < vh) {
        var k = (vh - r.top) / (vh + r.height);
        R.painWrap.style.transform = 'translateY(' + ((0.5 - k) * 26).toFixed(1) + 'px)';
      }
    }

    if (stepReady && R.stepsSec) {
      var rs = R.stepsSec.getBoundingClientRect();
      if (rs.bottom > 0 && rs.top < vh) {
        var p = Math.min(1, Math.max(0, (vh * 0.9 - rs.top) / (rs.height + vh * 0.35)));
        R.stepClip.setAttribute('width', (stepW * p).toFixed(1));
        var pt = R.stepLit.getPointAtLength(stepL * p);
        var rot = Math.sin(p * Math.PI * 4) * 5;
        R.stepMas.style.transform =
          'translate(' + (pt.x - 40).toFixed(1) + 'px, ' + (pt.y - 94).toFixed(1) + 'px) rotate(' +
          rot.toFixed(1) + 'deg)';
      }
    }

    if (R.mLit && R.mMas && R.stepsSec && !matchMedia('(min-width: 901px)').matches) {
      var rm = R.stepsSec.getBoundingClientRect();
      if (rm.bottom > 0 && rm.top < vh) {
        var pm = Math.min(1, Math.max(0, (vh * 0.85 - rm.top) / (rm.height + vh * 0.3)));
        R.mLit.style.height = (pm * 100).toFixed(1) + '%';
        var railH = R.mLit.parentElement.getBoundingClientRect().height;
        var rotm = Math.sin(pm * Math.PI * 5) * 7;
        R.mMas.style.transform =
          'translateY(' + (pm * Math.max(0, railH - 56)).toFixed(1) + 'px) rotate(' +
          rotm.toFixed(1) + 'deg)';
      }
    }

    if (R.psSec && R.psMas) {
      var rp = R.psSec.getBoundingClientRect();
      if (rp.bottom > 0 && rp.top < vh) {
        var kp = (vh - rp.top) / (vh + rp.height);
        R.psMas.style.transform =
          'translateY(' + ((0.5 - kp) * 90).toFixed(1) + 'px) rotate(' +
          ((kp - 0.5) * 10).toFixed(1) + 'deg)';
      }
    }

    if (R.ctaSec && R.ctaMas) {
      var rc = R.ctaSec.getBoundingClientRect();
      if (rc.top < vh && rc.bottom > 0) {
        var pc = Math.min(1, Math.max(0, (vh - rc.top) / (vh * 0.85)));
        var e = 1 - Math.pow(1 - pc, 3);
        R.ctaMas.style.transform =
          'translateY(calc(-50% + ' + ((1 - e) * 160).toFixed(1) + 'px)) scale(' +
          (0.75 + 0.25 * e).toFixed(3) + ')';
      }
    }
  }

  /* ------------------------------------- carrossel "Conheça o nosso espaço" */
  /* Arraste e snap sao do CSS (.amv-car); aqui ficam so as setas: um passo =
     largura de uma foto + o gap de 18px do grid. */
  (function () {
    var car = R.car;
    if (!car) return;
    document.querySelectorAll('[data-car]').forEach(function (btn) {
      btn.addEventListener('click', function () {
        var first = car.firstElementChild;
        var step = first ? first.getBoundingClientRect().width + 18 : car.clientWidth;
        car.scrollBy({
          left: (btn.getAttribute('data-car') === 'prev' ? -1 : 1) * step,
          behavior: motionOff ? 'auto' : 'smooth'
        });
      });
    });
  })();

  /* -------------------------------------------------------------------- init */
  setupReveals();
  setupSteps();

  var ticking = false;
  addEventListener('scroll', function () {
    if (ticking) return;
    ticking = true;
    requestAnimationFrame(function () { ticking = false; update(); });
  }, { passive: true });

  addEventListener('resize', function () {
    vh = innerHeight;
    setupSteps();
    update();
  });

  if (document.fonts) {
    document.fonts.ready.then(function () { setupSteps(); update(); });
  }
  update();

  /* Eventos de conversão para o GTM: cada CTA carrega data-cta (hero/meio/final/sticky). */
  document.querySelectorAll('a[data-cta]').forEach(function (a) {
    a.addEventListener('click', function () {
      window.dataLayer = window.dataLayer || [];
      window.dataLayer.push({
        event: 'clique_whatsapp',
        cta_local: a.getAttribute('data-cta')
      });
    });
  });
})();
