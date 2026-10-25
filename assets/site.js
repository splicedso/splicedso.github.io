// Shared by every page: the gutter bus, and helpers the other scripts use.

const ROOT = document.body.dataset.root || "";
const reduced = matchMedia("(prefers-reduced-motion: reduce)").matches;
const NS = "http://www.w3.org/2000/svg";
const el = (tag, attrs, parent) => {
  const e = document.createElementNS(NS, tag);
  for (const k in attrs) e.setAttribute(k, attrs[k]);
  if (parent) parent.appendChild(e);
  return e;
};
const cssVar = name => getComputedStyle(document.documentElement).getPropertyValue(name).trim();

// The bus: one trace down the left gutter through a via at every marked heading. It fills
// with current up to the reader's position, and charges drift along the filled part.
(function bus() {
  const svg = document.getElementById("bus");
  if (!svg || getComputedStyle(svg).display === "none") return;
  if (document.querySelectorAll("[data-via]").length < 2) return;
  let live, q = [], vias = [], len = 0, ys = [], fill = 0;
  function build() {
    svg.innerHTML = "";
    const H = document.documentElement.scrollHeight;
    const wrap = document.querySelector("main .wrap, header .wrap").getBoundingClientRect();
    const x = Math.max(16, wrap.left + 28 + 18);
    svg.setAttribute("height", H);
    svg.setAttribute("viewBox", `0 0 ${innerWidth} ${H}`);
    const pts = [...document.querySelectorAll("[data-via]")].map(e => {
      const r = e.getBoundingClientRect();
      return { y: r.top + scrollY + r.height / 2, xe: r.left - 8 };
    });
    ys = pts.map(p => p.y);
    const d = `M${x} ${pts[0].y}` + pts.slice(1).map(p => ` V${p.y}`).join("");
    el("path", { d, class: "base" }, svg);
    live = el("path", { d, class: "live" }, svg);
    len = live.getTotalLength();
    live.style.strokeDasharray = len;
    vias = pts.map(p => {
      el("path", { d: `M${x} ${p.y} H${p.xe}`, class: "base" }, svg);
      return el("circle", { cx: x, cy: p.y, r: 4.5, class: "via" }, svg);
    });
    q = Array.from({ length: 14 }, (_, i) => ({ c: el("circle", { r: 1.8, class: "q" }, svg), s: i / 14 }));
    update();
  }
  function update() {
    const y = scrollY + innerHeight * .6;
    fill = Math.max(0, Math.min(1, (y - ys[0]) / (ys[ys.length - 1] - ys[0])));
    live.style.strokeDashoffset = len * (1 - fill);
    vias.forEach((v, i) => v.classList.toggle("lit", ys[i] <= y));
  }
  function drift() {
    for (const c of q) {
      c.s = (c.s + .0009) % 1;
      const p = live.getPointAtLength(c.s * len * fill);
      c.c.setAttribute("cx", p.x);
      c.c.setAttribute("cy", p.y);
    }
    if (!reduced) requestAnimationFrame(drift);
  }
  addEventListener("scroll", update, { passive: true });
  addEventListener("resize", build);
  document.fonts.ready.then(() => { build(); requestAnimationFrame(drift); });
  // Charts render after load and change the page height.
  addEventListener("load", () => setTimeout(build, 300));
})();

// Content rises into place as it scrolls into view; siblings follow one another.
(function reveal() {
  const items = document.querySelectorAll("section .wrap > *, .page-head .wrap > *, .area, .note-card, .fact, .chart, .limits > div");
  if (reduced || !("IntersectionObserver" in window)) return;
  const seen = new IntersectionObserver(entries => entries.forEach(e => {
    if (e.isIntersecting) { e.target.classList.add("in"); seen.unobserve(e.target); }
  }), { rootMargin: "0px 0px -8% 0px" });
  items.forEach(item => {
    if (item.closest(".reveal")) return;
    const i = [...item.parentElement.children].indexOf(item);
    item.style.setProperty("--d", `${Math.min(i, 6) * 70}ms`);
    item.classList.add("reveal");
    seen.observe(item);
  });
})();

// The nav gains a hairline once the page has moved under it.
(function navShadow() {
  const nav = document.querySelector("nav");
  const set = () => nav.classList.toggle("scrolled", scrollY > 8);
  addEventListener("scroll", set, { passive: true });
  set();
})();

// Numbers count up the first time they are seen.
(function countUp() {
  const nums = document.querySelectorAll("[data-count]");
  if (reduced || !nums.length || !("IntersectionObserver" in window)) return;
  const io = new IntersectionObserver(entries => entries.forEach(e => {
    if (!e.isIntersecting) return;
    io.unobserve(e.target);
    const node = e.target.firstChild, end = parseFloat(e.target.dataset.count);
    const dp = (e.target.dataset.count.split(".")[1] || "").length, t0 = performance.now(), dur = 1400;
    const tick = now => {
      const p = Math.min(1, (now - t0) / dur), eased = 1 - Math.pow(1 - p, 4);
      node.textContent = (end * eased).toFixed(dp);
      if (p < 1) requestAnimationFrame(tick);
    };
    requestAnimationFrame(tick);
  }), { threshold: .6 });
  nums.forEach(n => io.observe(n));
})();

// Large images drift a little as they pass through the viewport.
(function parallax() {
  const imgs = [...document.querySelectorAll(".stage-img img")], hero = document.querySelector(".hero-object img, .hero-object video");
  if (reduced || (!imgs.length && !hero)) return;
  const tick = () => {
    imgs.forEach(img => {
      const r = img.getBoundingClientRect(), p = (r.top + r.height / 2) / innerHeight - .5;
      img.style.setProperty("--sy", Math.max(-1, Math.min(1, p)).toFixed(3));
    });
    if (hero) hero.style.setProperty("--hy", Math.min(1, scrollY / innerHeight).toFixed(3));
  };
  addEventListener("scroll", () => requestAnimationFrame(tick), { passive: true });
  tick();
})();

// Looping videos play while on screen and pause off it (some browsers hold off-screen autoplay).
(function videos() {
  const vids = document.querySelectorAll("video[autoplay]");
  if (!vids.length || !("IntersectionObserver" in window)) return;
  const io = new IntersectionObserver(es => es.forEach(e => {
    if (reduced) { e.target.pause(); return; }
    e.isIntersecting ? e.target.play().catch(() => {}) : e.target.pause();
  }), { threshold: .15 });
  vids.forEach(v => io.observe(v));
})();

// The hero turntable plays at a third of its rendered speed: a slow plinth turn, not a spin.
(function fall() {
  const c = document.getElementById("fall");
  if (!c) return;
  const n = 36, ctx = c.getContext("2d"), frames = [];
  let shown = -1;
  const draw = () => {
    const r = c.getBoundingClientRect();
    const t = Math.min(1, Math.max(0, (innerHeight * 0.85 - r.top) / (r.height + innerHeight * 0.35)));
    const i = Math.round(t * (n - 1));
    const im = frames[i];
    if (i !== shown && im && im.complete && im.naturalWidth) { ctx.drawImage(im, 0, 0, c.width, c.height); shown = i; }
  };
  for (let i = 0; i < n; i++) {
    const im = new Image();
    im.src = "assets/fall/" + String(i + 1).padStart(4, "0") + ".jpg";
    im.onload = () => { shown = -1; draw(); };
    frames.push(im);
  }
  addEventListener("scroll", () => requestAnimationFrame(draw), { passive: true });
})();
