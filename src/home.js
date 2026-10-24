// Home page: the token-by-token headline and the live power-path schematic.

// Hero: the headline is written one real Qwen2.5 token at a time, as an example of what we measure. At the measured 198 tokens
// per second it would be over in a fifth of a second, so it is replayed 30 times slower, and
// the meter adds the measured 141.5 mJ per decoded token as it goes.
const HEAD = ["The", " engineering", " of", " efficient", " inference", "."];
const LEDE = ["Sp", "liced", " is", " a", " research", " lab", " for", " the", " engineering", " side", " of", " AI", ":", " what", " it", " takes", " to", " run", " models", " well", ",", " from", " the", " kernels", " on", " a", " laptop", " to", " the", " servers", " in", " a", " data", "center", ".", " We", " measure", ",", " publish", " the", " method", " and", " the", " data", ",", " and", " say", " what", " each", " result", " cannot", " show", "."];
(function typeTokens() {
  const h1 = document.getElementById("h1"), lede = document.getElementById("lede");
  const mt = document.getElementById("m-tok"), mj = document.getElementById("m-j");
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
    mt.textContent = i; mj.textContent = (i * 0.1415).toFixed(2);
    if (i < all.length) reduced ? put() : setTimeout(put, step + (i === HEAD.length ? 500 : 0));
  }
  setTimeout(put, reduced ? 0 : 500);
})();

// Hero schematic. Current on each wire moves at a speed set by the replayed power at that point:
// the DC input and memory follow TP1 (board), the GPU and CPU follow TP2 (chip).
fetch(ROOT + "assets/trace.json").then(r => r.json()).then(trace => {
  const svg = document.getElementById("schem");
  const S = trace.samples, T = S[S.length - 1][0];
  const at = t => { let k = 0; while (k < S.length - 1 && S[k + 1][0] <= t) k++; return S[k]; };
  const phaseAt = t => { let n = "idle"; for (const [m, a] of trace.marks) if (t >= a) n = m; return n; };

  const g = (tag, attrs, text) => { const e = el(tag, attrs, svg); if (text) e.textContent = text; return e; };
  // Power path, drawn as a schematic. J1 DC input through R1 (the sense point, TP1) into the
  // PMIC, which feeds two rails: VDD_SOC to the SoC (TP2) and VDD_MEM to the memory. Wires on
  // the board side carry current at the TP1 rate, wires into the SoC at the TP2 rate.
  const wires = [
    { d: "M54 64 H96", src: 2 }, { d: "M150 64 H218", src: 2 },
    { d: "M300 64 H352 V104", src: 1 },
    { d: "M260 112 V240 H352", src: 2 },
  ];
  const flows = wires.map(w => {
    g("path", { d: w.d, class: "wire" });
    return { el: g("path", { d: w.d, class: "flow" }), src: w.src, off: 0 };
  });
  // J1: barrel connector
  g("circle", { cx: 40, cy: 64, r: 13, class: "part" }); g("circle", { cx: 40, cy: 64, r: 4, class: "fillbar" });
  g("text", { x: 22, y: 40 }, "J1"); g("text", { x: 22, y: 98, class: "dim" }, "DC IN");
  // R1: the sense resistor, as a zigzag
  g("path", { d: "M96 64 l5 -9 l9 18 l9 -18 l9 18 l9 -18 l9 18 l4 -9", class: "wire" });
  g("text", { x: 104, y: 98 }, "R1"); g("text", { x: 96, y: 112, class: "dim" }, "sense");
  // PMIC
  g("rect", { x: 218, y: 40, width: 82, height: 72, class: "part" });
  g("text", { x: 228, y: 70 }, "U3"); g("text", { x: 228, y: 86, class: "dim" }, "PMIC");
  // Rail labels
  g("text", { x: 306, y: 56, class: "dim" }, "VDD_SOC"); g("text", { x: 268, y: 232, class: "dim" }, "VDD_MEM");
  // SoC
  g("rect", { x: 352, y: 104, width: 176, height: 98, class: "part" });
  g("text", { x: 362, y: 122 }, "U1  SoC");
  const cores = [["GPU", 362, 132, 100], ["CPU", 468, 132, 50], ["ANE", 362, 166, 156]];
  const meters = cores.map(([n, x, y, w]) => {
    g("rect", { x, y, width: w, height: 24, class: "part" });
    const f = g("rect", { x, y, width: 0, height: 24, class: "fillbar" });
    g("text", { x: x + 6, y: y + 16, class: "on-fill" }, n);
    return { f, w };
  });
  // Memory and the bus between it and the SoC
  g("rect", { x: 352, y: 226, width: 176, height: 30, class: "part" });
  g("text", { x: 362, y: 245 }, "U2  LPDDR5X");
  const bus = [400, 424, 448, 472].map(x => {
    g("path", { d: `M${x} 202 V226`, class: "wire" });
    return { el: g("path", { d: `M${x} 202 V226`, class: "flow", style: "stroke-width:2.4;stroke-dasharray:1.5 5" }), src: 2, off: 0 };
  });
  g("text", { x: 482, y: 218, class: "dim" }, "x64");
  // Decoupling capacitors to ground on both rails, and the ground symbol
  const cap = (x, y) => {
    g("path", { d: `M${x} ${y} V${y + 14} M${x - 9} ${y + 14} H${x + 9} M${x - 9} ${y + 19} H${x + 9} M${x} ${y + 19} V282`, class: "wire" });
  };
  cap(176, 64); cap(232, 240);
  g("text", { x: 186, y: 84, class: "dim" }, "C1"); g("text", { x: 196, y: 262, class: "dim" }, "C2");
  g("path", { d: "M40 282 H540", class: "wire" });
  g("path", { d: "M40 77 V282", class: "wire" });
  g("path", { d: "M290 282 v8 M280 290 h20 M284 295 h12 M288 300 h4", class: "wire" });
  g("text", { x: 304, y: 298, class: "dim" }, "GND");
  // Test points
  const tp = (x, y, name) => { g("path", { d: `M${x} ${y} V${y - 26}`, class: "wire" }); g("circle", { cx: x, cy: y - 31, r: 5.5, class: "tp" }); g("text", { x: x + 10, y: y - 27 }, name); };
  tp(160, 64, "TP1  board"); tp(352, 160, "");
  g("text", { x: 300, y: 133 }, "TP2"); g("text", { x: 300, y: 147, class: "dim" }, "chip");
  flows.push(...bus);

  // Scope: a light graticule, ten by four divisions, with both traces.
  const cv = document.getElementById("scope"), ctx = cv.getContext("2d");
  let w, h;
  function size() { const dpr = devicePixelRatio || 1; w = cv.clientWidth; h = cv.clientHeight; cv.width = w * dpr; cv.height = h * dpr; ctx.setTransform(dpr, 0, 0, dpr, 0, 0); }
  size(); addEventListener("resize", size);
  const X = t => t / T * w, Y = p => h - 10 - p / 85 * (h - 20);

  const rt = document.getElementById("rt"), rc = document.getElementById("rc"), rs = document.getElementById("rs"), rp = document.getElementById("rp");
  const SPEED = 2;
  let t0 = null, last = null;
  function frame(now) {
    if (t0 === null) t0 = last = now;
    const dt = (now - last) / 1000; last = now;
    const t = reduced ? T * .7 : ((now - t0) / 1000 * SPEED) % (T + 2);
    const s = at(Math.min(t, T));
    for (const f of flows) { f.off -= dt * s[f.src] * 3.2; f.el.style.strokeDashoffset = f.off; f.el.style.opacity = .25 + Math.min(1, s[f.src] / 60); }
    meters[0].f.setAttribute("width", Math.min(1, s[1] / 40) * meters[0].w);
    meters[1].f.setAttribute("width", Math.min(1, 3.2 / 12) * meters[1].w);
    meters[2].f.setAttribute("width", 0);
    rt.textContent = s[0].toFixed(1); rc.textContent = s[1].toFixed(1); rs.textContent = s[2].toFixed(1); rp.textContent = phaseAt(s[0]);

    ctx.clearRect(0, 0, w, h);
    const ink = cssVar("--ink"), mute = cssVar("--mute");
    ctx.strokeStyle = cssVar("--rule"); ctx.lineWidth = 1;
    for (let i = 1; i < 10; i++) { ctx.beginPath(); ctx.moveTo(i * w / 10 + .5, 0); ctx.lineTo(i * w / 10 + .5, h); ctx.stroke(); }
    for (let i = 1; i < 4; i++) { ctx.beginPath(); ctx.moveTo(0, i * h / 4 + .5); ctx.lineTo(w, i * h / 4 + .5); ctx.stroke(); }
    const shown = S.filter(x => x[0] <= t);
    const line = (i, dash, width) => { ctx.setLineDash(dash); ctx.lineWidth = width; ctx.strokeStyle = ink; ctx.beginPath(); shown.forEach((x, k) => k ? ctx.lineTo(X(x[0]), Y(x[i])) : ctx.moveTo(X(x[0]), Y(x[i]))); ctx.stroke(); ctx.setLineDash([]); };
    line(2, [4, 3], 1.2); line(1, [], 1.6);
    if (shown.length) { const p = shown[shown.length - 1]; ctx.fillStyle = ink; ctx.beginPath(); ctx.arc(X(p[0]), Y(p[1]), 3.2, 0, 7); ctx.fill(); }
    ctx.font = "11px JetBrains Mono, monospace"; ctx.fillStyle = mute; ctx.fillText("CH1 chip  CH2 board  21 W/div  2 s/div", 10, 16);
    requestAnimationFrame(frame);
  }
  requestAnimationFrame(frame);
});
