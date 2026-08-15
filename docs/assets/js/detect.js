/* detect.js — shared helpers for "Wrong in a Particular Way"
 *
 * The interactive-lab engine for this site: seeded randomness, canvas
 * plumbing, a coordinate frame, control builders, and the classification
 * metrics this project is built on.
 *
 * The plotting half of this file is the SenSym mentored-research house
 * engine, shared with the other project sites, so a chapter authored for one
 * renders in another unchanged. The metrics half is specific to this project.
 *
 * Global namespace: G
 */
(function (global) {
  'use strict';

  var G = {};

  /* ================= seeded randomness ================= */
  /* Every figure in this course must be reproducible. Never use Math.random. */

  G.rng = function (seed) {
    var a = (seed >>> 0) || 1;
    return function () {
      a |= 0; a = (a + 0x6D2B79F5) | 0;
      var t = Math.imul(a ^ (a >>> 15), 1 | a);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  };
  /* ================= canvas plumbing ================= */

  /* Size a canvas for the device pixel ratio and return a 2-D context in CSS px.
   *
   * Careful: assigning to c.height writes back into the element's `height`
   * attribute. So the authored height can only be read ONCE -- after the first
   * call the attribute holds the device-pixel value, and re-reading it would
   * multiply by the pixel ratio again on every redraw (the canvas doubles in
   * height each time you touch a slider on a Retina display). Stash the
   * authored value on the element the first time and use that from then on. */
  G.canvas = function (id) {
    var c = typeof id === 'string' ? document.getElementById(id) : id;
    if (!c) return null;
    var dpr = global.devicePixelRatio || 1;
    var cssW = c.clientWidth || c.parentNode.clientWidth || 700;
    if (c.dataset.baseHeight === undefined) {
      c.dataset.baseHeight = String(parseInt(c.getAttribute('height'), 10) || 320);
    }
    var cssH = parseInt(c.dataset.baseHeight, 10);
    c.style.height = cssH + 'px';
    c.width = Math.round(cssW * dpr);
    c.height = Math.round(cssH * dpr);
    var ctx = c.getContext('2d');
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.clearRect(0, 0, cssW, cssH);
    return { c: c, ctx: ctx, w: cssW, h: cssH, dpr: dpr };
  };

  G.COL = {
    ink: '#10161d', muted: '#64748b', line: '#d7dce1', wash: '#f6f7f8',
    accent: '#0b6b5b', accent2: '#08483d', amber: '#b45309', green: '#15803d',
    rose: '#b02a37', violet: '#6d28d9', teal: '#0f766e'
  };

  /* A coordinate frame: maps data coordinates to pixels inside a margin box. */
  function Frame(ctx, w, h, opt) {
    opt = opt || {};
    var m = opt.margin || {};
    this.ctx = ctx;
    this.L = m.left === undefined ? 46 : m.left;
    this.R = m.right === undefined ? 14 : m.right;
    this.T = m.top === undefined ? 14 : m.top;
    this.B = m.bottom === undefined ? 34 : m.bottom;
    this.w = w; this.h = h;
    this.xmin = opt.xmin === undefined ? 0 : opt.xmin;
    this.xmax = opt.xmax === undefined ? 1 : opt.xmax;
    this.ymin = opt.ymin === undefined ? 0 : opt.ymin;
    this.ymax = opt.ymax === undefined ? 1 : opt.ymax;
    this.iw = w - this.L - this.R;
    this.ih = h - this.T - this.B;
  }
  Frame.prototype.px = function (x) {
    return this.L + (x - this.xmin) / (this.xmax - this.xmin) * this.iw;
  };
  Frame.prototype.py = function (y) {
    return this.T + this.ih - (y - this.ymin) / (this.ymax - this.ymin) * this.ih;
  };
  Frame.prototype.clipRect = function () {
    var c = this.ctx;
    c.save(); c.beginPath();
    c.rect(this.L, this.T, this.iw, this.ih); c.clip();
  };
  Frame.prototype.unclip = function () { this.ctx.restore(); };

  Frame.prototype.axes = function (o) {
    o = o || {};
    var c = this.ctx, i, v, s;
    var nt = function (v) { return (v === 0 || v === false) ? 0 : (v || 5); };
    var xt = nt(o.xticks), yt = nt(o.yticks);
    c.save();
    c.fillStyle = o.bg || '#fff';
    c.fillRect(this.L, this.T, this.iw, this.ih);

    /* grid */
    if (o.grid !== false) {
      c.strokeStyle = '#eef1f4'; c.lineWidth = 1;
      for (i = 0; xt && i <= xt; i++) {
        v = this.L + this.iw * i / xt;
        c.beginPath(); c.moveTo(v, this.T); c.lineTo(v, this.T + this.ih); c.stroke();
      }
      for (i = 0; yt && i <= yt; i++) {
        v = this.T + this.ih * i / yt;
        c.beginPath(); c.moveTo(this.L, v); c.lineTo(this.L + this.iw, v); c.stroke();
      }
    }

    /* box */
    c.strokeStyle = G.COL.line; c.lineWidth = 1;
    c.strokeRect(this.L + 0.5, this.T + 0.5, this.iw - 1, this.ih - 1);

    /* labels */
    c.fillStyle = G.COL.muted;
    c.font = '11px -apple-system, Segoe UI, Roboto, sans-serif';
    c.textAlign = 'center'; c.textBaseline = 'top';
    var fx = o.xfmt || function (t) { return G.fmt(t, 2); };
    var fy = o.yfmt || function (t) { return G.fmt(t, 2); };
    for (i = 0; xt && i <= xt; i++) {
      v = this.xmin + (this.xmax - this.xmin) * i / xt;
      c.fillText(fx(v), this.px(v), this.T + this.ih + 6);
    }
    c.textAlign = 'right'; c.textBaseline = 'middle';
    for (i = 0; yt && i <= yt; i++) {
      v = this.ymin + (this.ymax - this.ymin) * i / yt;
      c.fillText(fy(v), this.L - 7, this.py(v));
    }

    /* axis titles */
    c.fillStyle = G.COL.ink;
    c.font = '12px -apple-system, Segoe UI, Roboto, sans-serif';
    if (o.xlabel) {
      c.textAlign = 'center'; c.textBaseline = 'bottom';
      c.fillText(o.xlabel, this.L + this.iw / 2, this.h - 2);
    }
    if (o.ylabel) {
      c.save();
      c.translate(11, this.T + this.ih / 2);
      c.rotate(-Math.PI / 2);
      c.textAlign = 'center'; c.textBaseline = 'top';
      c.fillText(o.ylabel, 0, 0);
      c.restore();
    }
    c.restore();
    return this;
  };

  /* Draw y = fn(x) sampled across the frame. */
  Frame.prototype.fn = function (fn, o) {
    o = o || {};
    var c = this.ctx, n = o.samples || 400, i, x, y, started = false;
    this.clipRect();
    c.strokeStyle = o.color || G.COL.accent;
    c.lineWidth = o.width || 2;
    c.beginPath();
    for (i = 0; i <= n; i++) {
      x = this.xmin + (this.xmax - this.xmin) * i / n;
      y = fn(x);
      if (!isFinite(y)) { started = false; continue; }
      if (!started) { c.moveTo(this.px(x), this.py(y)); started = true; }
      else c.lineTo(this.px(x), this.py(y));
    }
    c.stroke();
    this.unclip();
    return this;
  };

  /* Polyline through [[x,y],...] */
  Frame.prototype.line = function (pts, o) {
    o = o || {};
    var c = this.ctx, i;
    if (!pts.length) return this;
    this.clipRect();
    if (o.alpha !== undefined) c.globalAlpha = o.alpha;
    c.strokeStyle = o.color || G.COL.ink;
    c.lineWidth = o.width || 1.5;
    if (o.dash) c.setLineDash(o.dash);
    c.beginPath();
    c.moveTo(this.px(pts[0][0]), this.py(pts[0][1]));
    for (i = 1; i < pts.length; i++) c.lineTo(this.px(pts[i][0]), this.py(pts[i][1]));
    c.stroke();
    c.setLineDash([]);
    c.globalAlpha = 1;
    this.unclip();
    return this;
  };

  /* A filled and/or stroked rectangle in DATA coordinates. Bars, highlighted
     bands, shaded confidence regions. Added for this project; the chaos site
     drew everything with lines and never needed it. */
  Frame.prototype.rect = function (x0, y0, x1, y1, o) {
    o = o || {};
    var c = this.ctx;
    var ax = this.px(x0), bx = this.px(x1), ay = this.py(y0), by = this.py(y1);
    var x = Math.min(ax, bx), y = Math.min(ay, by);
    var w = Math.abs(bx - ax), h = Math.abs(by - ay);
    this.clipRect();
    if (o.fill) {
      c.globalAlpha = o.alpha === undefined ? 1 : o.alpha;
      c.fillStyle = o.fill;
      c.fillRect(x, y, w, h);
      c.globalAlpha = 1;
    }
    if (o.stroke) {
      c.strokeStyle = o.stroke;
      c.lineWidth = o.width || 1.5;
      c.strokeRect(x + 0.5, y + 0.5, Math.max(0, w - 1), Math.max(0, h - 1));
    }
    this.unclip();
    return this;
  };

  /* Scatter of [[x,y],...] as small squares (fast for many points). */
  Frame.prototype.dots = function (pts, o) {
    o = o || {};
    var c = this.ctx, i, s = o.size || 1.4, half = s / 2;
    this.clipRect();
    c.fillStyle = o.color || G.COL.ink;
    if (o.alpha !== undefined) c.globalAlpha = o.alpha;
    for (i = 0; i < pts.length; i++) {
      c.fillRect(this.px(pts[i][0]) - half, this.py(pts[i][1]) - half, s, s);
    }
    c.globalAlpha = 1;
    this.unclip();
    return this;
  };

  Frame.prototype.dot = function (x, y, o) {
    o = o || {};
    var c = this.ctx;
    this.clipRect();
    c.fillStyle = o.color || G.COL.rose;
    c.beginPath();
    c.arc(this.px(x), this.py(y), o.r || 3.5, 0, 6.2832);
    c.fill();
    if (o.ring) {
      c.strokeStyle = '#fff'; c.lineWidth = 1.4; c.stroke();
    }
    this.unclip();
    return this;
  };

  /* Vertical / horizontal reference line in data coords. */
  Frame.prototype.vline = function (x, o) {
    o = o || {}; var c = this.ctx;
    this.clipRect();
    c.strokeStyle = o.color || G.COL.muted; c.lineWidth = o.width || 1;
    c.setLineDash(o.dash || [4, 3]);
    c.beginPath(); c.moveTo(this.px(x), this.T); c.lineTo(this.px(x), this.T + this.ih); c.stroke();
    c.setLineDash([]); this.unclip();
    return this;
  };
  Frame.prototype.hline = function (y, o) {
    o = o || {}; var c = this.ctx;
    this.clipRect();
    c.strokeStyle = o.color || G.COL.muted; c.lineWidth = o.width || 1;
    c.setLineDash(o.dash || [4, 3]);
    c.beginPath(); c.moveTo(this.L, this.py(y)); c.lineTo(this.L + this.iw, this.py(y)); c.stroke();
    c.setLineDash([]); this.unclip();
    return this;
  };

  /* Bars from a histogram: counts over [lo,hi]. */
  Frame.prototype.bars = function (counts, lo, hi, o) {
    o = o || {};
    var c = this.ctx, n = counts.length, i, x0, x1, y;
    this.clipRect();
    c.fillStyle = o.color || G.COL.accent;
    if (o.alpha !== undefined) c.globalAlpha = o.alpha;
    for (i = 0; i < n; i++) {
      x0 = this.px(lo + (hi - lo) * i / n);
      x1 = this.px(lo + (hi - lo) * (i + 1) / n);
      y = this.py(counts[i]);
      c.fillRect(x0, y, Math.max(1, x1 - x0 - (o.gap === undefined ? 0.5 : o.gap)),
                 this.py(this.ymin) - y);
    }
    c.globalAlpha = 1;
    this.unclip();
    return this;
  };

  /* Text annotation in data coordinates. */
  Frame.prototype.text = function (x, y, s, o) {
    o = o || {};
    var c = this.ctx;
    c.save();
    c.fillStyle = o.color || G.COL.ink;
    c.font = o.font || '12px -apple-system, Segoe UI, Roboto, sans-serif';
    c.textAlign = o.align || 'left';
    c.textBaseline = o.baseline || 'bottom';
    c.fillText(s, this.px(x) + (o.dx || 0), this.py(y) + (o.dy || 0));
    c.restore();
    return this;
  };

  /* Legend in the top-right of the plot box. */
  Frame.prototype.legend = function (items, o) {
    o = o || {};
    var c = this.ctx, i, y = this.T + 9, x = o.left ? this.L + 10 : this.L + this.iw - 10;
    c.save();
    c.font = '12px -apple-system, Segoe UI, Roboto, sans-serif';
    c.textBaseline = 'middle';
    c.textAlign = o.left ? 'left' : 'right';
    for (i = 0; i < items.length; i++) {
      c.fillStyle = items[i][1];
      if (o.left) { c.fillRect(x, y - 4, 16, 3); c.fillStyle = G.COL.ink; c.fillText(items[i][0], x + 22, y); }
      else {
        var tw = c.measureText(items[i][0]).width;
        c.fillRect(x - tw - 22, y - 4, 16, 3);
        c.fillStyle = G.COL.ink; c.fillText(items[i][0], x, y);
      }
      y += 17;
    }
    c.restore();
    return this;
  };

  G.frame = function (ctx, w, h, opt) { return new Frame(ctx, w, h, opt); };

  /* ================= number formatting ================= */

  G.fmt = function (v, d) {
    if (d === undefined) d = 3;
    if (v === undefined || v === null || !isFinite(v)) return '—';
    if (v === 0) return '0';
    var a = Math.abs(v);
    if (a >= 1e5 || a < 1e-4) return v.toExponential(Math.max(1, d - 1));
    return v.toFixed(d);
  };
  G.pad = function (s, n) { s = String(s); while (s.length < n) s = ' ' + s; return s; };

  /* ================= controls ================= */

  /* spec: [{k, type:'range'|'button'|'select'|'check', label, min,max,step,value,
   *         fmt, options:[[value,label]], text}]
   * Returns a state object; onchange(state, key) fires on every change. */
  G.controls = function (id, spec, onchange) {
    var host = typeof id === 'string' ? document.getElementById(id) : id;
    var state = {}, i;
    if (!host) return state;
    host.innerHTML = '';

    spec.forEach(function (s) {
      var wrap = document.createElement('div');
      wrap.className = 'ctl';

      if (s.type === 'button') {
        var b = document.createElement('button');
        b.type = 'button';
        b.textContent = s.text || s.label;
        b.addEventListener('click', function () { onchange(state, s.k); });
        wrap.appendChild(b);
      } else if (s.type === 'select') {
        var lab = document.createElement('label');
        lab.textContent = s.label; wrap.appendChild(lab);
        var sel = document.createElement('select');
        s.options.forEach(function (o) {
          var op = document.createElement('option');
          op.value = o[0]; op.textContent = o[1];
          sel.appendChild(op);
        });
        sel.value = s.value;
        state[s.k] = s.value;
        sel.addEventListener('change', function () {
          state[s.k] = sel.value; onchange(state, s.k);
        });
        wrap.appendChild(sel);
      } else if (s.type === 'check') {
        var cb = document.createElement('input');
        cb.type = 'checkbox'; cb.checked = !!s.value;
        state[s.k] = !!s.value;
        var cl = document.createElement('label');
        cl.textContent = s.label;
        cl.style.cursor = 'pointer';
        cl.addEventListener('click', function () { cb.checked = !cb.checked; cb.dispatchEvent(new Event('change')); });
        cb.addEventListener('change', function () { state[s.k] = cb.checked; onchange(state, s.k); });
        wrap.appendChild(cb); wrap.appendChild(cl);
      } else { /* range */
        var l2 = document.createElement('label');
        l2.textContent = s.label; wrap.appendChild(l2);
        var r = document.createElement('input');
        r.type = 'range';
        r.min = s.min; r.max = s.max; r.step = s.step;
        r.value = s.value;
        state[s.k] = parseFloat(s.value);
        var out = document.createElement('span');
        out.className = 'val';
        var f = s.fmt || function (v) { return G.fmt(v, 3); };
        out.textContent = f(state[s.k]);
        r.addEventListener('input', function () {
          state[s.k] = parseFloat(r.value);
          out.textContent = f(state[s.k]);
          onchange(state, s.k);
        });
        wrap.appendChild(r); wrap.appendChild(out);
      }
      host.appendChild(wrap);
    });
    return state;
  };

  G.say = function (id, text) {
    var el = typeof id === 'string' ? document.getElementById(id) : id;
    if (el) el.textContent = text;
  };

  /* ================= objectives checkboxes ================= */

  G.objectives = function () {
    var lists = document.querySelectorAll('.objectives ul');
    Array.prototype.forEach.call(lists, function (ul) {
      var key = 'wipw:' + (location.pathname.split('/').pop() || 'index');
      var saved = {};
      try { saved = JSON.parse(localStorage.getItem(key) || '{}'); } catch (e) { saved = {}; }
      Array.prototype.forEach.call(ul.querySelectorAll('li'), function (li, i) {
        var cb = document.createElement('input');
        cb.type = 'checkbox';
        cb.id = key + ':' + i;
        var label = document.createElement('label');
        label.setAttribute('for', cb.id);
        while (li.firstChild) label.appendChild(li.firstChild);
        li.appendChild(cb); li.appendChild(label);
        if (saved[i]) { cb.checked = true; li.classList.add('done'); }
        cb.addEventListener('change', function () {
          li.classList.toggle('done', cb.checked);
          saved[i] = cb.checked;
          try { localStorage.setItem(key, JSON.stringify(saved)); } catch (e) {}
        });
      });
    });
  };


  /* =====================================================================
     PROJECT-SPECIFIC: classification metrics
     =====================================================================
     Everything below is about one 2x2 table. The positive class is M,
     "this response contains a misconception" — see python/misconception/config.py.
     Keep these definitions and the Python in agreement; the tests in
     python/tests/test_pipeline.py cross-check the Python against scikit-learn,
     and this file is checked against the Python by eye in Phase 5. */

  /* m = {tp, fn, fp, tn}. Returns the four headline numbers plus specificity.
     A metric whose denominator is zero is returned as null, NOT as 0 — a
     precision of "no positive predictions were made" is undefined, and
     printing 0.00 there is a lie that has ended real papers. */
  G.metrics = function (m) {
    var tp = m.tp || 0, fn = m.fn || 0, fp = m.fp || 0, tn = m.tn || 0;
    var n = tp + fn + fp + tn;
    var prec = (tp + fp) ? tp / (tp + fp) : null;
    var rec  = (tp + fn) ? tp / (tp + fn) : null;
    var f1   = (prec !== null && rec !== null && (prec + rec) > 0)
                 ? 2 * prec * rec / (prec + rec) : null;
    return {
      n: n,
      acc:  n ? (tp + tn) / n : null,
      prec: prec,
      rec:  rec,
      f1:   f1,
      spec: (tn + fp) ? tn / (tn + fp) : null,
      /* the baseline worth beating: always guess the majority class */
      majority: n ? Math.max(tp + fn, fp + tn) / n : null
    };
  };

  /* Wilson score interval for a proportion k/n.
     Why Wilson and not k/n +/- 1.96*sqrt(p(1-p)/n): the normal approximation
     is badly wrong for small n and for p near 0 or 1, and this study has
     n = 40. At 38/40 the normal interval runs past 1.0, which is not a
     possible accuracy. Wilson does not. */
  G.wilson = function (k, n, z) {
    if (!n) return [null, null];
    z = z || 1.959964;
    var p = k / n, z2 = z * z;
    var d = 1 + z2 / n;
    var c = p + z2 / (2 * n);
    var s = z * Math.sqrt(p * (1 - p) / n + z2 / (4 * n * n));
    return [Math.max(0, (c - s) / d), Math.min(1, (c + s) / d)];
  };

  /* Format a metric that may be null. */
  G.pct = function (v, d) {
    if (v === null || v === undefined || isNaN(v)) return 'undefined';
    return (100 * v).toFixed(d === undefined ? 1 : d) + '%';
  };

  /* Render a 2x2 confusion matrix into a host element as a real table.
     A matrix is a table; drawing it on a canvas would be showing off. */
  G.matrix = function (id, m, opt) {
    var host = typeof id === 'string' ? document.getElementById(id) : id;
    if (!host) return;
    opt = opt || {};
    var cell = function (v, cls, name, sub) {
      return '<td class="cm ' + cls + '"><span class="cmv">' + v + '</span>' +
             '<span class="cmn">' + name + '</span>' +
             (sub ? '<span class="cms">' + sub + '</span>' : '') + '</td>';
    };
    host.innerHTML =
      '<table class="confusion"><thead><tr><th></th>' +
      '<th>model said M</th><th>model said C</th></tr></thead><tbody>' +
      '<tr><th>truly M</th>' +
        cell(m.tp, 'tp', 'true positive', 'caught it') +
        cell(m.fn, 'fn', 'false negative', opt.fnNote || 'MISSED a misconception') +
      '</tr><tr><th>truly C</th>' +
        cell(m.fp, 'fp', 'false positive', 'false alarm') +
        cell(m.tn, 'tn', 'true negative', 'correctly left alone') +
      '</tr></tbody></table>';
  };

  /* The twelve demo responses in python/data/sample/responses.csv, embedded so
     the labelling lab runs with no server. These are DEMO data: never report a
     number computed from them. */
  G.SAMPLE = [
    { id: 'S01', mis: 'M01', truth: 'M', text: "My password is 24 characters so it's basically uncrackable. Length is the only thing that really matters for password strength." },
    { id: 'S02', mis: 'M01', truth: 'M', text: "I use 'ilovepizzaandicecream' — it's really long, so even if it's just normal words a hacker would never get through it." },
    { id: 'S03', mis: 'M01', truth: 'C', text: "Length helps a lot, but a long password made of common words can still be guessed by a dictionary attack. It needs to be long and unpredictable." },
    { id: 'S04', mis: 'M01', truth: 'C', text: "I use a long passphrase, but I make sure it's random words that don't form a normal sentence, because attackers try common phrases first." },
    { id: 'S05', mis: 'M02', truth: 'M', text: "I change my password every single month, so even if someone got the old one my account is definitely safe now." },
    { id: 'S06', mis: 'M02', truth: 'M', text: "Our school makes us reset our password every 60 days, which is the main reason school accounts are more secure than personal ones." },
    { id: 'S07', mis: 'M02', truth: 'C', text: "I only change a password if there's a reason to — a breach notice or a login I don't recognize. Rotating on a schedule just makes people pick predictable patterns." },
    { id: 'S08', mis: 'M02', truth: 'C', text: "Changing a password doesn't help much on its own. What matters more is that it's unique to that site, so one breach doesn't spread." },
    { id: 'S09', mis: 'M03', truth: 'M', text: "Once I turned on two-factor authentication I stopped worrying about my password, because there's no way in without my phone." },
    { id: 'S10', mis: 'M03', truth: 'M', text: "MFA means my account literally cannot be hacked, so I reuse the same simple password on all my accounts that have it." },
    { id: 'S11', mis: 'M03', truth: 'C', text: "MFA blocks most automated attacks, but it isn't absolute — SIM swapping and push-notification spam can still get through, so the password still has to be strong." },
    { id: 'S12', mis: 'M03', truth: 'C', text: "Two-factor is the single best thing I've turned on, though I switched from SMS codes to an authenticator app because SMS can be intercepted." }
  ];

  G.MISCONCEPTIONS = [
    { id: 'M01', statement: 'Long passwords are always strong.',
      why: 'Length raises the cost of brute force, but a long password built from common words is still broken quickly by a dictionary attack. Strength comes from unpredictability, not length alone.' },
    { id: 'M02', statement: 'Changing passwords often makes accounts safer.',
      why: 'Forced rotation pushes people toward predictable increments (Summer2026!, Fall2026!) and does nothing if the credential has already leaked. NIST SP 800-63B recommends against scheduled rotation.' },
    { id: 'M03', statement: 'Multi-factor authentication makes an account impossible to hack.',
      why: 'MFA raises the cost of attack substantially but is bypassable via SIM swap, MFA-fatigue push spam, session-token theft, and real-time phishing proxies.' }
  ];

  /* Copy-to-clipboard buttons on every .cmd block. Progressive: if the
     clipboard API is unavailable the button falls back to a hidden textarea,
     and if that fails too it simply does nothing visible. */
  G.copyButtons = function () {
    Array.prototype.forEach.call(document.querySelectorAll('.cmd'), function (box) {
      if (box.querySelector('.copybtn')) return;
      var pre = box.querySelector('pre');
      if (!pre) return;
      var b = document.createElement('button');
      b.type = 'button'; b.className = 'copybtn'; b.textContent = 'copy';
      b.addEventListener('click', function () {
        var clone = pre.cloneNode(true);
        Array.prototype.forEach.call(clone.querySelectorAll('.p'), function (x) { x.remove(); });
        var text = clone.textContent.replace(/\n{3,}/g, '\n\n').trim();
        var ok = function () {
          b.textContent = 'copied'; b.classList.add('done');
          setTimeout(function () { b.textContent = 'copy'; b.classList.remove('done'); }, 1300);
        };
        if (navigator.clipboard && navigator.clipboard.writeText) {
          navigator.clipboard.writeText(text).then(ok, function () { fb(text, ok); });
        } else { fb(text, ok); }
      });
      box.appendChild(b);
    });
    function fb(text, ok) {
      var ta = document.createElement('textarea');
      ta.value = text; ta.style.position = 'fixed'; ta.style.opacity = '0';
      document.body.appendChild(ta); ta.select();
      try { document.execCommand('copy'); ok(); } catch (e) {}
      document.body.removeChild(ta);
    }
  };

  /* Operating-system switcher. Any element with class "os-only" and a
     data-os of "mac" or "win" shows only for the selected system. The choice
     is remembered across pages, because being asked twice is annoying. */
  G.osSwitch = function () {
    var bars = document.querySelectorAll('.os-bar');
    if (!bars.length) return;
    var pick = null;
    try { pick = localStorage.getItem('wipw:os'); } catch (e) {}
    if (pick !== 'mac' && pick !== 'win') {
      var ua = (navigator.platform || '') + ' ' + (navigator.userAgent || '');
      pick = (/Win/i.test(ua) && !/Mac/i.test(ua)) ? 'win' : 'mac';
    }
    function apply(os) {
      Array.prototype.forEach.call(document.querySelectorAll('.os-only'), function (n) {
        n.classList.toggle('on', n.getAttribute('data-os') === os);
      });
      Array.prototype.forEach.call(document.querySelectorAll('.os-bar button'), function (b) {
        b.setAttribute('aria-pressed', String(b.getAttribute('data-os') === os));
      });
      try { localStorage.setItem('wipw:os', os); } catch (e) {}
    }
    Array.prototype.forEach.call(bars, function (bar) {
      Array.prototype.forEach.call(bar.querySelectorAll('button'), function (b) {
        b.addEventListener('click', function () { apply(b.getAttribute('data-os')); });
      });
    });
    apply(pick);
  };

  /* ================= boot ================= */

  G.ready = function (fn) {
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', fn);
    else fn();
  };

  /* Register a lab: runs draw() on load and on resize (debounced). */
  G.lab = function (draw) {
    G.ready(function () {
      try { draw(); } catch (e) { console.error('lab error', e); }
      var t = null;
      global.addEventListener('resize', function () {
        clearTimeout(t);
        t = setTimeout(function () { try { draw(); } catch (e) { console.error('lab error', e); } }, 160);
      });
    });
  };

  G.ready(function () {
    G.objectives();
    G.copyButtons();
    G.osSwitch();
    if (global.renderMathInElement) {
      global.renderMathInElement(document.body, {
        delimiters: [
          { left: '$$', right: '$$', display: true },
          { left: '\\[', right: '\\]', display: true },
          { left: '$', right: '$', display: false },
          { left: '\\(', right: '\\)', display: false }
        ],
        throwOnError: false
      });
    }
  });

  global.G = G;
})(window);
