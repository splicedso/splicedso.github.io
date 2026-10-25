// Shared by every page: theme, the gutter bus, and helpers the other scripts use.

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

// Theme: follows the system until the reader picks one, then remembers it.
(function theme() {
  const btn = document.getElementById("theme");
  const stored = (() => { try { return localStorage.getItem("theme"); } catch { return null; } })();
  if (stored) document.documentElement.dataset.theme = stored;
  const current = () => document.documentElement.dataset.theme ||
    (matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
  const label = () => {
    const dark = current() === "dark";
    btn.setAttribute("aria-pressed", dark);
    btn.title = dark ? "Switch to light" : "Switch to dark";
  };
  btn.addEventListener("click", () => {
    const next = current() === "dark" ? "light" : "dark";
    document.documentElement.dataset.theme = next;
    try { localStorage.setItem("theme", next); } catch {}
    label();
    dispatchEvent(new Event("themechange"));
  });
  label();
})();

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
