// The data page: a two-way comparison and a filterable table over the Spliced dataset.
// Only measured rows are shown; a row without the chosen measurement point is disabled,
// never filled in.

fetch(ROOT + "assets/data.json").then(r => r.json()).then(D => {
  const rows = D.dataset.map((r, i) => ({ ...r, i }));
  explorer(rows);
  table(rows);
});

const label = r => `${r.model} ${r.format}${r.batch !== 1 && r.batch !== "1" ? ", batch " + r.batch : ""} | ${r.machine.split(",")[0]}`;
const fmt = n => n >= 1e9 ? (n / 1e9).toFixed(1) + " billion" : n >= 1e6 ? (n / 1e6).toFixed(1) + " million" : Math.round(n).toLocaleString("en");

function explorer(rows) {
  const a = document.getElementById("cmp-a"), b = document.getElementById("cmp-b");
  const svg = document.getElementById("cmp-svg");
  let key = "board_mj";
  for (const sel of [a, b]) {
    for (const r of rows) {
      const o = document.createElement("option");
      o.value = r.i;
      o.textContent = label(r);
      sel.appendChild(o);
    }
  }
  // A laptop token against a datacenter token is the comparison most people want first.
  a.value = rows.find(r => r.model === "Qwen2.5 7B" && r.format === "Q4_0" && r.machine.startsWith("Apple")).i;
  b.value = rows.find(r => r.model === "Llama 2 70B" && r.machine.includes("B200")).i;

  const W = 1000, L = 20, R = 160;
  const bars = [0, 1].map(k => {
    const y = 18 + k * 64;
    const t = el("text", { x: L, y: y, class: "lbl" }, svg);
    const bar = el("rect", { x: L, y: y + 10, width: 0, height: 26, class: k ? "hatch" : "ink-fill" }, svg);
    const v = el("text", { x: L, y: y + 29 }, svg);
    return { t, bar, v };
  });
  bars[0].bar.style.transition = bars[1].bar.style.transition = "width .9s cubic-bezier(.2,.7,.1,1)";

  function enable() {
    for (const sel of [a, b]) {
      for (const o of sel.options) o.disabled = rows[o.value][key] === "" || rows[o.value][key] == null;
      if (sel.selectedOptions[0].disabled) sel.value = [...sel.options].find(o => !o.disabled).value;
    }
  }
  function update() {
    enable();
    const ra = rows[a.value], rb = rows[b.value];
    const va = +ra[key], vb = +rb[key], max = Math.max(va, vb);
    [[ra, va], [rb, vb]].forEach(([r, v], k) => {
      const w = Math.max(2, v / max * (W - L - R));
      bars[k].t.textContent = (k ? "B  " : "A  ") + label(r);
      bars[k].bar.setAttribute("width", w);
      bars[k].v.setAttribute("x", L + w + 10);
      bars[k].v.textContent = v.toLocaleString("en") + " mJ/token";
    });
    const ratio = va > vb ? va / vb : vb / va;
    document.getElementById("cmp-ratio").textContent = `${(va > vb ? "A" : "B")} costs ${ratio.toFixed(ratio < 10 ? 2 : 0)}x`;
    document.getElementById("cmp-kwh-a").textContent = fmt(3.6e9 / va);
    document.getElementById("cmp-kwh-b").textContent = fmt(3.6e9 / vb);
    document.getElementById("cmp-phone").textContent = `${fmt(5.4e7 / va)} / ${fmt(5.4e7 / vb)}`;
    const point = r => key === "board_mj" ? r.board_point : r.chip_point;
    document.getElementById("cmp-note").innerHTML =
      `A: ${point(ra)}, ${ra.power_state}, ${ra.runtime}, <a href="${ROOT}research/">note ${ra.note}</a>. ` +
      `B: ${point(rb)}, ${rb.power_state}, ${rb.runtime}, <a href="${ROOT}research/">note ${rb.note}</a>. ` +
      (point(ra) !== point(rb) ? "The two were measured at different points, so read the ratio as an order of magnitude, not a precise figure." : "Same measurement point.");
  }
  a.onchange = b.onchange = update;
  document.querySelectorAll(".cmp .toggle button").forEach(x => x.onclick = () => {
    key = x.dataset.v;
    document.querySelectorAll(".cmp .toggle button").forEach(y => y.setAttribute("aria-pressed", y === x));
    update();
  });
  update();
}

function table(rows) {
  const t = document.getElementById("dtable"), f = document.getElementById("filters");
  const machines = [...new Set(rows.map(r => r.machine))];
  let on = "all";
  const cols = [["model", "model"], ["format", "format"], ["batch", "batch"], ["tok_s", "tok/s"],
                ["chip_mj", "chip mJ"], ["board_mj", "whole mJ"], ["note", "note"]];
  for (const m of ["all", ...machines]) {
    const btn = document.createElement("button");
    btn.textContent = m === "all" ? "all machines" : m.split(",")[0];
    btn.setAttribute("aria-pressed", m === on);
    btn.onclick = () => { on = m; f.querySelectorAll("button").forEach(x => x.setAttribute("aria-pressed", x === btn)); draw(); };
    f.appendChild(btn);
  }
  function draw() {
    const shown = rows.filter(r => on === "all" || r.machine === on);
    t.innerHTML = "<thead><tr><th>machine</th>" + cols.map(([, h]) => `<th>${h}</th>`).join("") + "</tr></thead><tbody>" +
      shown.map(r => `<tr><td>${r.machine.split(",")[0]}</td>` + cols.map(([k]) =>
        `<td${["tok_s", "chip_mj", "board_mj", "batch"].includes(k) ? ' class="num"' : ""}>${r[k] === "" ? "&ndash;" : r[k]}</td>`).join("") + "</tr>").join("") +
      "</tbody>";
  }
  draw();
}
