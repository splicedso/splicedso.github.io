// Home page: the token-by-token headline and the live power-path schematic.

// Hero: the headline is written one real Qwen2.5 token at a time, as an example of what we measure. At the measured 198 tokens
// per second it would be over in a fifth of a second, so it is replayed 30 times slower.
const HEAD = ["The", " engineering", " of", " efficient", " inference", "."];
const LEDE = ["We", " measure", " what", " it", " costs", " to", " run", " AI", ",", " and", " publish", " everything", "."];
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
