// Home page: the token-by-token headline and the live power-path schematic.

// Hero: the headline is written one real Qwen2.5 token at a time, as an example of what we measure. At the measured 198 tokens
// per second it would be over in a fifth of a second, so it is replayed 30 times slower.
const HEAD = ["Me", "asuring", " frontier", " inference", "."];
const LEDE = ["What", " AI", " costs", " to", " run", ",", " and", " how", " to", " cut", " it", "."];
(function typeTokens() {
  const h1 = document.getElementById("h1"), lede = document.getElementById("lede");
  const all = [...HEAD.map(t => [h1, t]), ...LEDE.map(t => [lede, t])];
  const step = 1000 / 198 * 30;
  let i = 0;
  function put() {
    const [el, t] = all[i];
    const span = document.createElement("span");
    span.className = "tok fresh"; span.textContent = t;
    el.appendChild(span);
    setTimeout(() => span.classList.remove("fresh"), 380);
    i++;
    if (i < all.length) reduced ? put() : setTimeout(put, step + (i === HEAD.length ? 500 : 0));
  }
  setTimeout(put, reduced ? 0 : 500);
})();

// Run an animation only while its element is on screen.
function whileVisible(node, start, stop) {
  if (!("IntersectionObserver" in window)) return start();
  new IntersectionObserver(([e]) => (e.isIntersecting ? start() : stop())).observe(node);
}
function fitCanvas(c) {
  const r = devicePixelRatio || 1, w = c.clientWidth, h = c.clientHeight;
  if (c.width !== w * r) { c.width = w * r; c.height = h * r; }
  const x = c.getContext("2d"); x.setTransform(r, 0, 0, r, 0, 0); return [x, w, h];
}
const C = name => getComputedStyle(document.documentElement).getPropertyValue(name).trim();

// Replay: the real chip and board trace, drawn up to a moving playhead. Counters come from the
// measured rates of that run (6,454 prompt tokens/s, 197.8 answer tokens/s), not from the trace.
fetch(ROOT + "assets/trace.json").then(r => r.json()).then(trace => {
  const c = document.getElementById("scope2");
  if (!c) return;
  const S = trace.samples, T = S[S.length - 1][0], marks = trace.marks;
  const phaseAt = t => { let n = "idle", a0 = 0; for (const [m, a] of marks) if (t >= a) { n = m; a0 = a; } return [n, a0]; };
  const nextMark = a0 => { for (const [, a] of marks) if (a > a0) return a; return T; };
  const out = id => document.getElementById(id);
  let t0 = null, raf = 0;
  function draw(now) {
    if (t0 === null) t0 = now;
    const t = reduced ? T : ((now - t0) / 1000) % (T + 1.5);
    const [x, w, h] = fitCanvas(c), pad = 8, top = 14, bot = h - 22;
    const PMAX = Math.ceil(Math.max(...S.map(s => s[2])) / 10) * 10 + 10;
    const X = s => pad + s / T * (w - 2 * pad), Y = p => bot - p / PMAX * (bot - top);
    x.clearRect(0, 0, w, h);
    for (const [m, a] of marks) if (m !== "idle") {
      x.fillStyle = m === "decode" ? C("--cv-band-a") : C("--cv-band-b");
      x.fillRect(X(a), top, X(nextMark(a)) - X(a), bot - top);
      x.fillStyle = C("--cv-text"); x.font = "11px JetBrains Mono, monospace";
      x.fillText(m === "decode" ? "writing the answer" : "reading the prompt", X(a) + 6, top + 12);
    }
    x.strokeStyle = C("--cv-grid"); x.lineWidth = 1;
    for (let p = 0; p <= PMAX; p += 20) { x.beginPath(); x.moveTo(pad, Y(p)); x.lineTo(w - pad, Y(p)); x.stroke(); }
    const line = (k, color, width) => {
      x.beginPath(); x.strokeStyle = color; x.lineWidth = width; x.lineJoin = "round";
      S.forEach((s, i) => { if (s[0] <= t) (i ? x.lineTo : x.moveTo).call(x, X(s[0]), Y(s[k])); });
      x.stroke();
    };
    line(2, C("--cv-board"), 1.5);
    line(1, C("--cv-ink"), 2.4);
    const cur = S.findLast ? S.findLast(s => s[0] <= t) || S[0] : S.filter(s => s[0] <= t).pop() || S[0];
    x.fillStyle = C("--cv-ink"); x.shadowColor = C("--cv-ink"); x.shadowBlur = 10; x.beginPath(); x.arc(X(Math.min(t, T)), Y(cur[1]), 4.5, 0, 7); x.fill(); x.shadowBlur = 0;
    x.fillStyle = C("--cv-text"); x.fillText(PMAX + " W", pad + 2, top + 10);
    const [ph, a0] = phaseAt(t);
    out("sc-chip").textContent = cur[1].toFixed(1);
    out("sc-board").textContent = cur[2].toFixed(1);
    out("sc-t").textContent = Math.min(t, T).toFixed(1);
    const pill = out("sc-phase"); pill.textContent = ph === "decode" ? "writing" : ph === "prefill" ? "reading" : "idle"; pill.dataset.p = ph;
    const pre = marks.find(m => m[0] === "prefill"), dec = marks.find(m => m[0] === "decode");
    const read = pre ? Math.round(Math.max(0, Math.min(t, nextMark(pre[1])) - pre[1]) * 6454) : 0;
    const wrote = dec ? Math.round(Math.max(0, Math.min(t, nextMark(dec[1])) - dec[1]) * 197.8) : 0;
    out("sc-text").textContent = `prompt tokens read ${read.toLocaleString()}   ·   answer tokens written ${wrote.toLocaleString()}`;
    if (!reduced) raf = requestAnimationFrame(draw);
  }
  whileVisible(c, () => { cancelAnimationFrame(raf); raf = requestAnimationFrame(draw); }, () => cancelAnimationFrame(raf));
});

// Batching: note 1's measured energy per token at each batch size. The columns are the series;
// the readout eases to the selected column; the slider plays itself until someone drags it.
fetch(ROOT + "assets/data.json").then(r => r.json()).then(data => {
  const cols = document.getElementById("cols"), slider = document.getElementById("bt");
  if (!cols) return;
  const series = data.batch.q4_0, top = series[0].mj;
  series.forEach(p => cols.insertAdjacentHTML("beforeend", `<i style="--h:${(p.mj / top * 100).toFixed(1)}%"><span>${Math.round(p.mj)}</span></i>`));
  const out = document.getElementById("bt-mj"), cut = document.getElementById("bt-cut"), watts = document.getElementById("bt-w");
  let shown = top, target = top, raf = 0;
  const ease = () => { shown += (target - shown) * 0.16; out.textContent = shown.toFixed(1); if (Math.abs(target - shown) > 0.05) raf = requestAnimationFrame(ease); else out.textContent = target.toFixed(1); };
  const set = n => {
    const p = series[n - 1];
    target = p.mj; cancelAnimationFrame(raf); raf = requestAnimationFrame(ease);
    cut.textContent = n === 1 ? "one request" : `${Math.round((1 - p.mj / top) * 100)}% less`;
    watts.textContent = `${Math.round(p.gpu_w)} W`;
    [...cols.children].forEach((c, i) => c.classList.toggle("on", i === n - 1));
    slider.style.setProperty("--p", `${(n - 1) / 7 * 100}%`);
  };
  let auto = null, n = 1;
  const play = () => { if (!reduced && !auto) auto = setInterval(() => { n = n % 8 + 1; slider.value = n; set(n); }, 1300); };
  const pause = () => { clearInterval(auto); auto = null; };
  slider.addEventListener("input", () => { pause(); n = +slider.value; set(n); slider.dataset.touched = 1; });
  [...cols.children].forEach((c, i) => c.addEventListener("click", () => { pause(); slider.dataset.touched = 1; n = i + 1; slider.value = n; set(n); }));
  whileVisible(cols, () => { if (!slider.dataset.touched) play(); }, pause);
  set(1);
});

// Note 19: joules per correct answer, each machine's 1.5B at one request set to 1.
(function jpc() {
  const svg = document.getElementById("jpc");
  if (!svg) return;
  const groups = [["M5 Pro", 40.2, 35.1], ["Strix Halo", 230.9, 156.6]];
  groups.forEach(([name, small, big], g) => {
    const x0 = 40 + g * 170, base = 180, H = 130;
    el("text", { x: x0 + 55, y: 208, "text-anchor": "middle", class: "lbl" }, svg).textContent = name;
    [[small, "1.5B, 1 at a time", "66%"], [big, "7B, 8 at once", "88%"]].forEach(([v, label, acc], i) => {
      const r = v / small, x = x0 + i * 60, hgt = H * r;
      const bar = el("rect", { x, y: base, width: 48, height: 0, rx: 6, class: i ? "b-big" : "b-small" }, svg);
      bar.dataset.h = hgt;
      el("text", { x: x + 24, y: base - hgt - 8, "text-anchor": "middle", class: "val" }, svg).textContent = r.toFixed(2);
      el("text", { x: x + 24, y: base + 14, "text-anchor": "middle", class: "acc" }, svg).textContent = acc;
    });
  });
  whileVisible(svg, () => svg.querySelectorAll("rect").forEach(b => { b.setAttribute("y", 180 - b.dataset.h); b.setAttribute("height", b.dataset.h); }), () => {});
})();

// Terminal: Phase measuring three models; the rows are the published Mac baseline.
fetch(ROOT + "assets/data.json").then(r => r.json()).then(data => {
  const term = document.getElementById("term");
  if (!term) return;
  const rows = data.results.map(r => `${r.model.replace("Qwen2.5 ", "").padEnd(5)} ${r.phase.padEnd(8)} ${String(Math.round(r.tps)).padStart(6)} tok/s ${r.chip.toFixed(1).padStart(7)} mJ`);
  const script = [["$ ", "uv run phase qwen2.5-{0.5b,1.5b,7b}.gguf"], ["", "idle baseline 1.6 W chip, 12.7 W board"], ["", "sizing runs to 20 s each ..."], ["", ""], ...rows.map(r => ["", r]), ["", ""], ["", "saved results/run.json"]];
  let timer = 0;
  function run() {
    let line = 0, ch = 0, text = "";
    const step = () => {
      if (line >= script.length) { timer = setTimeout(() => { term.textContent = ""; run(); }, 3500); return; }
      const [prompt, body] = script[line];
      if (prompt) {
        if (ch === 0) text += prompt;
        if (ch < body.length) { text += body[ch++]; term.textContent = text + "▍"; timer = setTimeout(step, 28); return; }
      } else text += body;
      text += "\n"; line++; ch = 0; term.textContent = text + "▍";
      timer = setTimeout(step, prompt ? 400 : 160);
    };
    step();
  }
  if (reduced) term.textContent = script.map(s => s.join("")).join("\n");
  else whileVisible(term, () => { if (!timer) run(); }, () => { clearTimeout(timer); timer = 0; term.textContent = ""; });
});

// Model visuals: Trace follows a target, Lattice snaps to a grid, Kinetic streams.
document.querySelectorAll(".mviz").forEach(c => {
  const kind = c.dataset.viz;
  const dots = Array.from({ length: 70 }, () => [Math.random(), Math.random(), 0.2 + Math.random() * 0.8]);
  let raf = 0;
  const frame = now => {
    const [x, w, h] = fitCanvas(c), t = reduced ? 2 : now / 1000;
    x.clearRect(0, 0, w, h);
    if (kind === "trace") {
      for (const [k, color, lag] of [[0, C("--cv-board"), 0], [1, C("--cv-ink"), 0.35]]) {
        x.beginPath(); x.strokeStyle = color; x.lineWidth = k ? 2.4 : 1.6;
        for (let i = 0; i <= w; i += 4) {
          const u = i / w * 6 + t - lag;
          const y = h / 2 + Math.sin(u) * h * 0.22 + Math.sin(u * 2.3) * h * 0.08;
          i ? x.lineTo(i, y) : x.moveTo(i, y);
        }
        x.stroke();
      }
    } else if (kind === "lattice") {
      const g = 22, snap = (Math.sin(t * 0.9) + 1) / 2;
      x.fillStyle = C("--cv-grid-dot");
      for (let i = g / 2; i < w; i += g) for (let j = g / 2; j < h; j += g) { x.beginPath(); x.arc(i, j, 1.4, 0, 7); x.fill(); }
      x.fillStyle = C("--cv-ink");
      dots.forEach(([a, b]) => {
        const px = a * w, py = b * h, qx = Math.round((px - g / 2) / g) * g + g / 2, qy = Math.round((py - g / 2) / g) * g + g / 2;
        x.beginPath(); x.arc(px + (qx - px) * snap, py + (qy - py) * snap, 3, 0, 7); x.fill();
      });
    } else {
      dots.forEach(([a, b, v]) => {
        const px = ((a + t * 0.25 * v) % 1) * (w + 60) - 30, py = b * h;
        const grad = x.createLinearGradient(px - 40 * v, py, px, py);
        grad.addColorStop(0, C("--cv-ink-0")); grad.addColorStop(1, C("--cv-ink"));
        x.strokeStyle = grad; x.lineWidth = 2; x.beginPath(); x.moveTo(px - 40 * v, py); x.lineTo(px, py); x.stroke();
      });
    }
    if (!reduced) raf = requestAnimationFrame(frame);
  };
  whileVisible(c, () => { cancelAnimationFrame(raf); raf = requestAnimationFrame(frame); }, () => cancelAnimationFrame(raf));
});
