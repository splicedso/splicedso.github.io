// Research charts. Each draws only if its figure is on the page. Data comes from
// assets/data.json, which build.py generates from phase's results files.

fetch(ROOT + "assets/data.json").then(r => r.json()).then(D => {
  resultsBars(D.results);
  formatChart(D.formats, "#fmt", 9.5, 11.0, [9.5, 10, 10.5, 11]);
  formatChart(D.formats7, "#fmt7", 7.2, 7.9, [7.3, 7.5, 7.7, 7.9]);
  batchChart(D.batch);
  rooflineChart(D.roofline);
  twoChart(D.two);
  kernChart(D.kernels);
  widthChart(D.width);
  specChart(D.spec);
  mwhChart(D.mwh);
  pminChart(D.pmin);
});

function resultsBars(rows) {
  const table = document.getElementById("bars");
  if (!table) return;
  const max = Math.max(...rows.map(r => r.board));
  for (const r of rows) {
    const row = document.createElement("div");
    row.className = "row";
    row.innerHTML = `<span class="m">${r.model}</span><span class="mono">${r.phase}</span>
      <span class="bar" title="chip ${r.chip} mJ, board ${r.board} mJ"><i class="board" data-w="${r.board / max * 100}"></i><i class="chip" data-w="${r.chip / max * 100}"></i></span>
      <span class="v mono">${r.tps.toLocaleString("en")} <span class="dim">&middot; ${r.chip} / ${r.board}</span></span>`;
    table.appendChild(row);
  }
  // Bars charge like a capacitor when the table comes into view.
  new IntersectionObserver((es, o) => {
    if (!es[0].isIntersecting) return;
    table.querySelectorAll(".bar i").forEach((b, i) =>
      setTimeout(() => b.style.width = b.dataset.w + "%", reduced ? 0 : 60 * Math.floor(i / 2)));
    o.disconnect();
  }, { threshold: .2 }).observe(table);
}

function axes(svg, xs, ys) {
  for (const [x1, y1, x2, y2] of [...xs, ...ys]) el("line", { x1, y1, x2, y2, class: "gridline" }, svg);
}

function formatChart(FORMATS, sel, ymin, ymax, ticks) {
  const svg = document.querySelector(sel + " svg");
  if (!svg) return;
  const W = 1000, H = 440, L = 56, R = 24, T = 20, B = 40;
  const xmax = Math.ceil(Math.max(...FORMATS.flatMap(f => [f.soc, f.board])) / 100) * 100;
  const step = xmax > 1000 ? 500 : 100;
  const LBL = { F16: [10, -10], Q8_0: [10, 16], Q6_K: [-10, -10, "end"], Q5_K_M: [10, 18], Q4_0: [10, 18] };
  const X = v => L + v / xmax * (W - L - R);
  const Y = p => T + (Math.min(p, ymax) - ymin) / (ymax - ymin) * (H - T - B);
  for (let v = 0; v <= xmax; v += step) {
    el("line", { x1: X(v), x2: X(v), y1: T, y2: H - B, class: "gridline" }, svg);
    el("text", { x: X(v), y: H - B + 22, "text-anchor": "middle" }, svg).textContent = v;
  }
  for (const p of ticks) {
    el("line", { x1: L, x2: W - R, y1: Y(p), y2: Y(p), class: "gridline" }, svg);
    el("text", { x: L - 10, y: Y(p) + 4, "text-anchor": "end" }, svg).textContent = p.toFixed(1);
  }
  el("text", { x: W - R, y: H - 6, "text-anchor": "end" }, svg).textContent = "mJ per decoded token";
  const front = el("path", { class: "ink-line", "stroke-width": 1.2, "stroke-dasharray": "3 4" }, svg);
  const dots = FORMATS.map(f => {
    const g = el("g", { class: "dot" }, svg);
    el("line", { x1: 0, x2: 0, y1: 0, y2: 0, class: "ink-line ghost", opacity: .35 }, g);
    el("circle", { r: f.name === "Q4_0" ? 6 : 4.5, class: "ink-fill" }, g);
    const [dx, dy, anchor] = LBL[f.name] || [10, -10];
    const off = f.ppl > ymax ? `  ${f.ppl.toFixed(1)}, off scale` : "";
    el("text", { x: dx, y: dy, class: "lbl", "text-anchor": anchor || "start" }, g).textContent = f.name + off + (f.note ? "  " + f.note : "");
    return { f, g };
  });
  function frontier(key) {
    const pts = FORMATS.map(f => ({ x: f[key], y: f.ppl })).sort((a, b) => a.x - b.x);
    const out = [];
    let best = Infinity;
    for (const p of pts) if (p.y < best) { out.push(p); best = p.y; }
    return out;
  }
  function show(key) {
    for (const { f, g } of dots) {
      g.style.transform = `translate(${X(f[key])}px, ${Y(f.ppl)}px)`;
      g.querySelector(".ghost").setAttribute("x2", X(key === "board" ? f.soc : f.board) - X(f[key]));
    }
    front.setAttribute("d", frontier(key).map((p, i) => (i ? "L" : "M") + X(p.x) + " " + Y(p.y)).join(" "));
    document.querySelectorAll(sel + " .toggle button").forEach(b => b.setAttribute("aria-pressed", b.dataset.v === key));
  }
  document.querySelectorAll(sel + " .toggle button").forEach(b => b.onclick = () => show(b.dataset.v));
  show("soc");
  new IntersectionObserver((es, o) => {
    if (es[0].isIntersecting) { setTimeout(() => show("board"), 400); o.disconnect(); }
  }, { threshold: .25 }).observe(svg);
}

function batchChart(BATCH) {
  const svg = document.querySelector("#bat svg");
  if (!svg) return;
  const read = document.getElementById("bat-read");
  const W = 1000, H = 380, L = 56, R = 56, T = 20, B = 40;
  const n = BATCH.q4_0.length, ymax = 140, wmax = 40;
  const X = i => L + (i + .5) * (W - L - R) / n, bw = (W - L - R) / n * .56;
  const Y = v => H - B - v / ymax * (H - T - B), YW = w => H - B - w / wmax * (H - T - B);
  for (const v of [0, 40, 80, 120]) {
    el("line", { x1: L, x2: W - R, y1: Y(v), y2: Y(v), class: "gridline" }, svg);
    el("text", { x: L - 10, y: Y(v) + 4, "text-anchor": "end" }, svg).textContent = v;
  }
  for (const w of [0, 20, 40]) el("text", { x: W - R + 10, y: YW(w) + 4 }, svg).textContent = w + " W";
  el("text", { x: L - 10, y: T - 6, "text-anchor": "end" }, svg).textContent = "mJ/tok";
  const cols = BATCH.q4_0.map((r, i) => {
    const g = el("g", { class: "col" }, svg);
    el("rect", { x: X(i) - bw / 2, y: YW(r.gpu_w), width: bw, height: H - B - YW(r.gpu_w), class: "ink-fill", opacity: .1 }, g);
    el("text", { x: X(i), y: H - B + 22, "text-anchor": "middle" }, g).textContent = r.batch;
    el("rect", { x: X(i) - (W - L - R) / n / 2, y: T, width: (W - L - R) / n, height: H - T - B, fill: "transparent" }, g);
    g.addEventListener("pointerenter", () => focus(i));
    return g;
  });
  const line = (rows, dash) => el("path", {
    d: rows.map((r, i) => (i ? "L" : "M") + X(i) + " " + Y(r.mj)).join(" "),
    class: "ink-line", "stroke-width": 1.8, "stroke-dasharray": dash,
  }, svg);
  line(BATCH.q4_0, "");
  line(BATCH.q4_k_m, "5 4");
  const cur = el("circle", { r: 5, class: "ink-fill" }, svg);
  function focus(i) {
    cols.forEach((g, k) => g.querySelector("rect").setAttribute("opacity", k === i ? .25 : .1));
    const a = BATCH.q4_0[i], b = BATCH.q4_k_m[i];
    cur.setAttribute("cx", X(i));
    cur.setAttribute("cy", Y(a.mj));
    read.textContent = `batch ${a.batch}  Q4_0 ${a.mj.toFixed(0)} mJ/tok  Q4_K_M ${b.mj.toFixed(0)} mJ/tok  GPU ${a.gpu_w.toFixed(1)} W`;
  }
  focus(0);
}

// Each format as a bar: how much of the measured bandwidth roof its decode reaches.
// The bar grows from zero to its measured share, and a marker sits at 100%.
function rooflineChart(RF) {
  const svg = document.querySelector("#roof svg");
  if (!svg) return;
  const rows = RF.rows, W = 1000, rowH = 40, L = 96, R = 150, T = 26;
  const H = T + rows.length * rowH + 30;
  svg.setAttribute("viewBox", `0 0 ${W} ${H}`);
  const X = f => L + f * (W - L - R) / 1.1;
  for (const f of [0, .25, .5, .75, 1]) {
    el("line", { x1: X(f), x2: X(f), y1: T - 8, y2: H - 30, class: f === 1 ? "ink-line" : "gridline", "stroke-dasharray": f === 1 ? "4 3" : "" }, svg);
    el("text", { x: X(f), y: H - 10, "text-anchor": "middle" }, svg).textContent = Math.round(f * 100) + "%";
  }
  el("text", { x: X(1) + 6, y: T - 12 }, svg).textContent = `roof ${RF.bandwidth_gb_s.toFixed(0)} GB/s`;
  const bars = rows.map((r, i) => {
    const y = T + i * rowH;
    el("text", { x: L - 12, y: y + 22, "text-anchor": "end", class: "lbl" }, svg).textContent = r.format;
    const b = el("rect", { x: L, y: y + 8, width: 0, height: 20, class: "ink-fill" }, svg);
    el("text", { x: W - R + 16, y: y + 22 }, svg).textContent =
      `${Math.round(r.efficiency * 100)}%  ${r.tok_s.toFixed(0)} tok/s  ${r.gb_per_token.toFixed(2)} GB`;
    return { b, w: X(r.efficiency) - L };
  });
  new IntersectionObserver((es, o) => {
    if (!es[0].isIntersecting) return;
    bars.forEach((x, i) => setTimeout(() => x.b.setAttribute("width", x.w), reduced ? 0 : 70 * i));
    o.disconnect();
  }, { threshold: .3 }).observe(svg);
}

// Whole-machine energy per format on both laptops, as paired bars that grow in.
function twoChart(rows) {
  const svg = document.querySelector("#two svg");
  if (!svg) return;
  const W = 1000, rowH = 44, L = 96, R = 70, T = 24;
  const H = T + rows.length * rowH + 30;
  svg.setAttribute("viewBox", `0 0 ${W} ${H}`);
  const max = Math.ceil(Math.max(...rows.flatMap(r => [r.win_sys_mj, r.mac_board_mj])) / 100) * 100;
  const X = v => L + v / max * (W - L - R);
  for (let v = 0; v <= max; v += 200) {
    el("line", { x1: X(v), x2: X(v), y1: T - 6, y2: H - 30, class: "gridline" }, svg);
    el("text", { x: X(v), y: H - 10, "text-anchor": "middle" }, svg).textContent = v;
  }
  el("text", { x: W - R + 60, y: H - 10, "text-anchor": "end" }, svg).textContent = "mJ/tok";
  const bars = [];
  rows.forEach((r, i) => {
    const y = T + i * rowH;
    el("text", { x: L - 12, y: y + 22, "text-anchor": "end", class: "lbl" }, svg).textContent = r.format;
    const a = el("rect", { x: L, y: y + 6, width: 0, height: 13, class: "ink-fill" }, svg);
    const b = el("rect", { x: L, y: y + 21, width: 0, height: 13, class: "hatch" }, svg);
    el("text", { x: X(Math.max(r.win_sys_mj, r.mac_board_mj)) + 8, y: y + 25 }, svg).textContent =
      `${Math.round(r.win_sys_mj)} / ${Math.round(r.mac_board_mj)}`;
    bars.push([a, X(r.win_sys_mj) - L], [b, X(r.mac_board_mj) - L]);
  });
  new IntersectionObserver((es, o) => {
    if (!es[0].isIntersecting) return;
    bars.forEach(([b, w], i) => setTimeout(() => b.setAttribute("width", w), reduced ? 0 : 45 * i));
    o.disconnect();
  }, { threshold: .3 }).observe(svg);
}

// Chip energy per weight for each format's matvec kernel, split into streaming the bytes
// (F16's energy per byte, which needs no unpacking) and unpacking them (the rest).
function kernChart(rows) {
  const svg = document.querySelector("#kern svg");
  if (!svg) return;
  const W = 1000, rowH = 40, L = 96, R = 90, T = 24;
  const H = T + rows.length * rowH + 30;
  svg.setAttribute("viewBox", `0 0 ${W} ${H}`);
  const stream = rows.find(r => r.format === "f16").soc_nj_b;
  const max = 120;
  const X = v => L + v / max * (W - L - R);
  for (let v = 0; v <= max; v += 20) {
    el("line", { x1: X(v), x2: X(v), y1: T - 6, y2: H - 30, class: "gridline" }, svg);
    el("text", { x: X(v), y: H - 10, "text-anchor": "middle" }, svg).textContent = v;
  }
  el("text", { x: W - R + 80, y: H - 10, "text-anchor": "end" }, svg).textContent = "pJ/weight";
  const bars = [];
  rows.forEach((r, i) => {
    const y = T + i * rowH;
    const s = stream * r.bytes_per_weight * 1e3;
    el("text", { x: L - 12, y: y + 22, "text-anchor": "end", class: "lbl" }, svg).textContent = r.format.toUpperCase();
    const a = el("rect", { x: L, y: y + 8, width: 0, height: 20, class: "hatch" }, svg);
    const b = el("rect", { x: X(s), y: y + 8, width: 0, height: 20, class: "ink-fill" }, svg);
    el("text", { x: X(r.soc_pj_w) + 8, y: y + 23 }, svg).textContent = r.soc_pj_w.toFixed(0);
    bars.push([a, X(s) - L], [b, X(r.soc_pj_w) - X(s)]);
  });
  new IntersectionObserver((es, o) => {
    if (!es[0].isIntersecting) return;
    bars.forEach(([b, w], i) => setTimeout(() => b.setAttribute("width", Math.max(0, w)), reduced ? 0 : 40 * i));
    o.disconnect();
  }, { threshold: .3 }).observe(svg);
}

// Board energy per weight against model width, one line per format. Lines draw in from the
// left as the chart scrolls into view; hover a width to read every format at it.
function widthChart(rows) {
  const svg = document.querySelector("#width svg");
  if (!svg) return;
  const read = document.getElementById("width-read");
  const W = 1000, H = 400, L = 56, R = 110, T = 20, B = 40;
  const sizes = ["0.5b", "1.5b", "3b", "7b"], fmts = ["Q4_0", "Q4_K_M", "Q5_K_M", "Q6_K", "Q8_0"];
  const dash = { Q4_0: "", Q4_K_M: "6 4", Q5_K_M: "2 4", Q6_K: "10 3 2 3", Q8_0: "1 3" };
  const X = i => L + i * (W - L - R) / (sizes.length - 1);
  const Y = v => H - B - (v - 100) / 250 * (H - T - B);
  for (const v of [100, 150, 200, 250, 300, 350]) {
    el("line", { x1: L, x2: W - R, y1: Y(v), y2: Y(v), class: "gridline" }, svg);
    el("text", { x: L - 10, y: Y(v) + 4, "text-anchor": "end" }, svg).textContent = v;
  }
  el("text", { x: L - 10, y: T - 6, "text-anchor": "end" }, svg).textContent = "pJ/weight";
  sizes.forEach((s, i) => el("text", { x: X(i), y: H - B + 22, "text-anchor": "middle" }, svg).textContent = s.toUpperCase());
  const paths = fmts.map(f => {
    const pts = sizes.map((s, i) => [X(i), Y(rows.find(r => r.size === s && r.format === f).board_pj_per_weight)]);
    const p = el("path", { d: pts.map((p, i) => (i ? "L" : "M") + p.join(" ")).join(" "), class: "ink-line",
                           "stroke-width": f === "Q4_0" ? 2.4 : 1.5, "stroke-dasharray": dash[f] }, svg);
    const last = pts[pts.length - 1];
    el("text", { x: last[0] + 10, y: last[1] + 4, class: "lbl" }, svg).textContent = f;
    return p;
  });
  const cur = el("line", { y1: T, y2: H - B, class: "ink-line", opacity: .35 }, svg);
  function focus(i) {
    cur.setAttribute("x1", X(i)); cur.setAttribute("x2", X(i));
    read.textContent = sizes[i].toUpperCase() + "  " + fmts.map(f =>
      `${f} ${rows.find(r => r.size === sizes[i] && r.format === f).board_pj_per_weight.toFixed(0)}`).join("  ");
  }
  sizes.forEach((s, i) => {
    const hit = el("rect", { x: X(i) - 40, y: T, width: 80, height: H - T - B, fill: "transparent" }, svg);
    hit.addEventListener("pointerenter", () => focus(i));
  });
  focus(0);
  // Draw each line in, as a pen would.
  for (const p of paths) {
    const len = p.getTotalLength();
    p.style.strokeDashoffset = 0;
    if (reduced || p.getAttribute("stroke-dasharray")) continue;
    p.style.strokeDasharray = len;
    p.style.strokeDashoffset = len;
  }
  new IntersectionObserver((es, o) => {
    if (!es[0].isIntersecting) return;
    paths.forEach((p, i) => setTimeout(() => {
      p.style.transition = "stroke-dashoffset 1.4s cubic-bezier(.2,.7,.1,1)";
      p.style.strokeDashoffset = 0;
    }, 120 * i));
    o.disconnect();
  }, { threshold: .3 }).observe(svg);
}

// Speed-up against energy ratio, both relative to plain decoding. Points right of the
// vertical line are faster; points above the horizontal line cost more energy. The
// upper-right quadrant is the trap: faster and more expensive.
function specChart(rows) {
  const svg = document.querySelector("#spec svg");
  if (!svg) return;
  const read = document.getElementById("spec-read");
  const W = 1000, H = 440, L = 60, R = 30, T = 24, B = 44;
  const X = v => L + Math.log2(v / .3) / Math.log2(5 / .3) * (W - L - R);
  const Y = v => T + (1 - Math.log2(v / .25) / Math.log2(4.5 / .25)) * (H - T - B);
  for (const v of [.5, 1, 2, 4]) {
    el("line", { x1: X(v), x2: X(v), y1: T, y2: H - B, class: v === 1 ? "ink-line" : "gridline", "stroke-dasharray": v === 1 ? "4 3" : "" }, svg);
    el("text", { x: X(v), y: H - B + 22, "text-anchor": "middle" }, svg).textContent = v + "x";
  }
  for (const v of [.25, .5, 1, 2, 4]) {
    el("line", { x1: L, x2: W - R, y1: Y(v), y2: Y(v), class: v === 1 ? "ink-line" : "gridline", "stroke-dasharray": v === 1 ? "4 3" : "" }, svg);
    el("text", { x: L - 10, y: Y(v) + 4, "text-anchor": "end" }, svg).textContent = v + "x";
  }
  el("text", { x: W - R, y: H - 6, "text-anchor": "end" }, svg).textContent = "speed vs plain decoding";
  el("text", { x: L + 6, y: H - B - 10 }, svg).textContent = "energy vs plain (up is costlier)";
  el("text", { x: W - R - 8, y: T + 14, "text-anchor": "end", class: "lbl" }, svg).textContent = "faster and costlier";
  el("text", { x: W - R - 8, y: H - B - 10, "text-anchor": "end", class: "lbl" }, svg).textContent = "faster and cheaper";
  const plain = {};
  rows.filter(r => r.cond === "plain").forEach(r => plain[r.prompt] = r);
  const shape = { code: "M-5 -5 h10 v10 h-10 Z", prose: "M0 -6 L6 5 L-6 5 Z", edit: "M0 -6 A6 6 0 1 0 0.01 -6 Z" };
  rows.filter(r => r.cond !== "plain").forEach((r, i) => {
    const sx = r.tok_s / plain[r.prompt].tok_s, ey = r.vs_plain;
    const g = el("g", { class: "dot", style: `transform: translate(${X(1)}px, ${Y(1)}px)` }, svg);
    el("path", { d: shape[r.prompt], class: "ink-fill" }, g);
    el("text", { x: 9, y: 4 }, g).textContent = r.cond.replace("draft-", "d");
    g.addEventListener("pointerenter", () => read.textContent =
      `${r.prompt} ${r.cond}  ${sx.toFixed(2)}x speed  ${ey.toFixed(2)}x energy  accepted ${r.accept == null ? "-" : Math.round(r.accept * 100) + "%"}`);
    setTimeout(() => g.style.transform = `translate(${X(sx)}px, ${Y(ey)}px)`, reduced ? 0 : 0);
    g.dataset.to = `translate(${X(sx)}px, ${Y(ey)}px)`;
  });
  // Every point starts at plain decoding (1x, 1x) and moves to where it measured.
  const pts = [...svg.querySelectorAll(".dot")];
  pts.forEach(g => g.style.transform = `translate(${X(1)}px, ${Y(1)}px)`);
  new IntersectionObserver((es, o) => {
    if (!es[0].isIntersecting) return;
    pts.forEach((g, i) => setTimeout(() => g.style.transform = g.dataset.to, reduced ? 0 : 300 + 40 * i));
    o.disconnect();
  }, { threshold: .3 }).observe(svg);
}

// Billion tokens per megawatt-hour per audited system, at the wall or at the building
// for a chosen PUE. The bars resize when the PUE changes.
function mwhChart(rows) {
  const svg = document.querySelector("#mwh svg");
  if (!svg) return;
  const W = 1000, rowH = 52, L = 250, R = 110, T = 20;
  const H = T + rows.length * rowH + 30;
  svg.setAttribute("viewBox", `0 0 ${W} ${H}`);
  const max = 60;
  const X = v => L + v / max * (W - L - R);
  for (let v = 0; v <= max; v += 10) {
    el("line", { x1: X(v), x2: X(v), y1: T - 6, y2: H - 30, class: "gridline" }, svg);
    el("text", { x: X(v), y: H - 10, "text-anchor": "middle" }, svg).textContent = v;
  }
  el("text", { x: W - 8, y: 12, "text-anchor": "end" }, svg).textContent = "billion tokens per MWh";
  const bars = rows.map((r, i) => {
    const y = T + i * rowH;
    el("text", { x: L - 14, y: y + 18, "text-anchor": "end", class: "lbl" }, svg).textContent = r.system;
    el("text", { x: L - 14, y: y + 34, "text-anchor": "end" }, svg).textContent = `${r.model}, ${r.dtype}`;
    const b = el("rect", { x: L, y: y + 10, width: 0, height: 24, class: "ink-fill" }, svg);
    const t = el("text", { x: L + 8, y: y + 27 }, svg);
    return { r, b, t };
  });
  function show(pue) {
    for (const { r, b, t } of bars) {
      const v = 3.6e9 / r.j_per_tok / 1e9 / pue;
      b.setAttribute("width", Math.max(1, X(v) - L));
      t.setAttribute("x", X(v) + 8);
      t.textContent = v < 1 ? v.toFixed(2) : v.toFixed(1);
    }
    document.querySelectorAll("#mwh .toggle button").forEach(x => x.setAttribute("aria-pressed", +x.dataset.v === pue));
  }
  document.querySelectorAll("#mwh .toggle button").forEach(x => x.onclick = () => show(+x.dataset.v));
  new IntersectionObserver((es, o) => {
    if (!es[0].isIntersecting) return;
    show(1);
    o.disconnect();
  }, { threshold: .3 }).observe(svg);
}

// Energy against plain decoding for each threshold, one group per prompt. Bars grow up from
// the 1x line (costlier) or down from it (cheaper), so the threshold's effect reads as
// bars collapsing toward or below the line.
function pminChart(rows) {
  const svg = document.querySelector("#pmin svg");
  if (!svg) return;
  const read = document.getElementById("pmin-read");
  const conds = ["draft-8", "draft-8-p0.5", "draft-8-p0.8", "draft-8-p0.95", "draft-16", "draft-16-p0.8"];
  const short = { "draft-8": "d8", "draft-8-p0.5": "d8 .5", "draft-8-p0.8": "d8 .8", "draft-8-p0.95": "d8 .95", "draft-16": "d16", "draft-16-p0.8": "d16 .8" };
  const prompts = ["code", "prose", "edit"];
  const W = 1000, H = 400, L = 56, R = 16, T = 20, B = 56;
  const Y = v => T + (1 - Math.log2(v / .5) / Math.log2(4 / .5)) * (H - T - B);
  for (const v of [.5, 1, 2, 4]) {
    el("line", { x1: L, x2: W - R, y1: Y(v), y2: Y(v), class: v === 1 ? "ink-line" : "gridline", "stroke-dasharray": v === 1 ? "4 3" : "" }, svg);
    el("text", { x: L - 10, y: Y(v) + 4, "text-anchor": "end" }, svg).textContent = v + "x";
  }
  const gw = (W - L - R) / prompts.length, bw = gw / (conds.length + 1.5);
  const bars = [];
  prompts.forEach((p, gi) => {
    el("text", { x: L + gi * gw + gw / 2, y: H - 12, "text-anchor": "middle", class: "lbl" }, svg).textContent = p;
    conds.forEach((c, ci) => {
      const r = rows.find(x => x.prompt === p && x.cond === c);
      const x = L + gi * gw + (ci + .75) * bw;
      const top = Math.min(Y(r.vs_plain), Y(1)), h = Math.abs(Y(r.vs_plain) - Y(1));
      const thr = c.includes("-p");
      const b = el("rect", { x, y: Y(1), width: bw * .8, height: 0, class: thr ? "ink-fill" : "hatch" }, svg);
      el("text", { x: x + bw * .4, y: H - B + 16, "text-anchor": "middle", style: "font-size:10px" }, svg).textContent = short[c];
      b.addEventListener("pointerenter", () => read.textContent =
        `${p} ${c}: ${r.vs_plain.toFixed(2)}x energy, ${r.speed.toFixed(2)}x speed, ${Math.round(r.accept * 100)}% accepted`);
      bars.push({ b, top, h });
    });
  });
  new IntersectionObserver((es, o) => {
    if (!es[0].isIntersecting) return;
    bars.forEach(({ b, top, h }, i) => setTimeout(() => {
      b.style.transition = "y .8s cubic-bezier(.2,.7,.1,1), height .8s cubic-bezier(.2,.7,.1,1)";
      b.setAttribute("y", top); b.setAttribute("height", Math.max(1, h));
    }, reduced ? 0 : 40 * i));
    o.disconnect();
  }, { threshold: .3 }).observe(svg);
}
