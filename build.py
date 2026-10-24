"""Build the site from src/ and the research notes in the sibling joule checkout.

    uv run --with markdown python build.py

Notes are written once, as markdown in joule/notes, and rendered here. A line
`<!-- chart:NAME -->` in a note becomes the interactive figure of that name. Chart data is
generated from joule/results, so the site cannot drift from the measurements.
"""

import json
import re
import shutil
import time
from pathlib import Path

import markdown

HERE = Path(__file__).parent
SRC = HERE / "src"
JOULE = HERE.parent / "joule"
VERSION = time.strftime("%Y%m%d%H%M")
CONFIG = json.loads((HERE / "site.json").read_text())
SITE = ("https://" + CONFIG["domain"]) if CONFIG.get("domain") else CONFIG["url"].rstrip("/")
PAGES = []

NOTES = [
    {"slug": "formats-and-batching", "file": "2026-10-formats-and-batching.md", "n": 1,
     "summary": "Eight quantization formats and batch sizes 1 to 8, energy at the chip and at the board. "
                "Chip-only measurement misranks F16 by 2x; batch 2 saves 1% per token and batch 8 saves 72%."},
    {"slug": "roofline-and-energy-model", "file": "2026-10-roofline-and-energy-model.md", "n": 2,
     "summary": "A decode roofline from measured bandwidth, and a validated energy model whose residuals "
                "isolate the cost of unpacking each format. Two wrong first attempts, kept in."},
    {"slug": "scale-and-runtime", "file": "2026-10-scale-and-runtime.md", "n": 3,
     "summary": "The format study at 7B, where every finding replicates and the hardware is used better, and in MLX, "
                "where repeat runs do not yet agree, so only claims that survive both passes are made."},
    {"slug": "two-machines", "file": "2026-10-two-machines.md", "n": 4,
     "summary": "The study on a Windows laptop with an RTX 5070 Ti, on battery. Q4_0 wins on both machines and a 4-bit token "
                "costs the same whole-machine energy on both; one Mac finding does not transfer."},
    {"slug": "kernel-energy", "file": "2026-10-kernel-energy.md", "n": 5,
     "summary": "Each format's matrix-vector kernel measured alone. Q4_0 and Q4_K read identical bytes at identical speed; "
                "Q4_K's unpacking costs 40% more chip energy. Explains note 2's largest residual and corrects its roof."},
    {"slug": "model-width", "file": "2026-10-model-width.md", "n": 6,
     "summary": "Five formats across four model sizes. A weight in a 0.5B model costs up to 1.6 times one in a 7B; "
                "Q4_0 is cheapest at every width; the Q5_K_M against Q6_K order flips with width."},
    {"slug": "speculative-decoding", "file": "2026-10-speculative-decoding.md", "n": 7,
     "summary": "Speculative decoding with a draft model and with n-gram copying, on code, prose and edits. It can be "
                "faster and more expensive at once; copy-based drafting on an edit costs 32% of plain decoding."},
    {"slug": "tokens-per-megawatt-hour", "file": "2026-10-tokens-per-megawatt-hour.md", "n": 8,
     "summary": "Every MLPerf LLM result with measured wall power. A B200 server buys 2.7 times the tokens per joule "
                "of an H100 NVL one, and the roofline says it must batch 58 or more sequences per weight pass."},
]

FIGURES = {
    "fmt": """<figure class="chart" id="fmt">
  <div class="chart-bar mono"><span>Decode energy against perplexity, eight formats</span>
    <span class="toggle" role="group" aria-label="Measurement point"><button data-v="board" aria-pressed="true">TP1 board</button><button data-v="soc" aria-pressed="false">TP2 chip only</button></span></div>
  <svg viewBox="0 0 1000 440" role="img" aria-label="Decode energy per token against perplexity for eight quantization formats"></svg>
  <figcaption class="mono">x: millijoules per decoded token. y: WikiText-2 perplexity, lower is better, so better is higher. The dashed line joins the formats nothing else beats on both. Toggle the test point to see how chip-only measurement moves every format.</figcaption>
</figure>""",
    "fmt7": """<figure class="chart" id="fmt7">
  <div class="chart-bar mono"><span>Qwen2.5 7B: decode energy against perplexity</span>
    <span class="toggle" role="group" aria-label="Measurement point"><button data-v="board" aria-pressed="true">TP1 board</button><button data-v="soc" aria-pressed="false">TP2 chip only</button></span></div>
  <svg viewBox="0 0 1000 440" role="img" aria-label="Decode energy per token against perplexity for eight quantization formats of the 7B model"></svg>
  <figcaption class="mono">Mean of two passes. F16 is plotted but did not repeat (memory pressure), so it is left out of the conclusions. Same layout as note 1: better is higher, cheaper is further left.</figcaption>
</figure>""",
    "two": """<figure class="chart" id="two">
  <div class="chart-bar mono"><span>Whole-machine decode energy, Qwen2.5 1.5B, two laptops</span><span>solid: Windows, RTX 5070 Ti, battery &middot; outline: Mac, M5 Pro, board</span></div>
  <svg viewBox="0 0 1000 400" role="img" aria-label="Whole-machine energy per token for eight formats on a Windows laptop and a Mac"></svg>
  <figcaption class="mono">Mean of two passes per machine. The labels read Windows / Mac in millijoules per token. At 4 bits the two machines land within 5% of each other; at full precision they part.</figcaption>
</figure>""",
    "kern": """<figure class="chart" id="kern">
  <div class="chart-bar mono"><span>Chip energy per weight, one 4096 x 14336 matrix-vector kernel per format</span><span>outline: streaming the bytes &middot; solid: unpacking them</span></div>
  <svg viewBox="0 0 1000 380" role="img" aria-label="Chip energy per weight for each format, split into streaming and unpacking"></svg>
  <figcaption class="mono">Streaming is the format's bytes at F16's energy per byte, since F16 needs no unpacking; unpacking is the rest. Q4_0 and Q4_K stream the same bytes, so the difference between them is all unpacking. Mean of two passes.</figcaption>
</figure>""",
    "width": """<figure class="chart" id="width">
  <div class="chart-bar mono"><span>Board energy per weight against model size, five formats</span><span id="width-read">0.5B</span></div>
  <svg viewBox="0 0 1000 400" role="img" aria-label="Energy per weight falls as models widen, for every format"></svg>
  <figcaption class="mono">Qwen2.5 0.5B to 7B, hidden size 896 to 3584. Board picojoules per weight read per decoded token, mean of two passes. Q4_0 is the heavy line. Hover or tap a size to read every format.</figcaption>
</figure>""",
    "spec": """<figure class="chart" id="spec">
  <div class="chart-bar mono"><span>Speculative decoding: speed against chip energy, both relative to plain decoding</span><span id="spec-read">square: code &middot; triangle: prose &middot; circle: edit</span></div>
  <svg viewBox="0 0 1000 440" role="img" aria-label="Speed-up against energy ratio for each speculative strategy and task"></svg>
  <figcaption class="mono">Log scales. Each point starts at plain decoding (1x, 1x) and moves to where it measured. d2 to d16: a draft model guessing that many tokens; ngram: copying from the context. Hover a point to read it.</figcaption>
</figure>""",
    "mwh": """<figure class="chart" id="mwh">
  <div class="chart-bar mono"><span>Billion tokens per megawatt-hour, audited MLPerf systems, Offline</span>
    <span class="toggle" role="group" aria-label="Where energy is counted"><button data-v="1" aria-pressed="true">wall</button><button data-v="1.09" aria-pressed="false">PUE 1.09</button><button data-v="1.56" aria-pressed="false">PUE 1.56</button></span></div>
  <svg viewBox="0 0 1000 260" role="img" aria-label="Tokens per megawatt-hour for each audited system"></svg>
  <figcaption class="mono">Output tokens per MWh from measured wall power. PUE 1.09 is Google's fleet; 1.56 is the 2024 industry average. The 405B row counts only output tokens of long-context prompts and is not comparable as a model cost.</figcaption>
</figure>""",
    "bat": """<figure class="chart" id="bat">
  <div class="chart-bar mono"><span>Decode energy per token and GPU power, by batch size</span><span id="bat-read">batch 1</span></div>
  <svg viewBox="0 0 1000 380" role="img" aria-label="Energy per token falls with batch size while GPU power plateaus from batch 2"></svg>
  <figcaption class="mono">Lines: chip millijoules per token, Q4_0 solid and Q4_K_M dashed. Columns: GPU watts for Q4_0. Mean of three runs. Hover or tap a column.</figcaption>
</figure>""",
    "roof": """<figure class="chart" id="roof">
  <div class="chart-bar mono"><span>Share of the memory-bandwidth roof each format's decode reaches</span><span>Qwen2.5 1.5B, llama.cpp</span></div>
  <svg viewBox="0 0 1000 380" role="img" aria-label="Fraction of measured memory bandwidth reached by decode, per format"></svg>
  <figcaption class="mono">The roof is the 266 GB/s an MLX matrix-vector kernel reaches on this machine. Bytes per token count every tensor except the token embedding table.</figcaption>
</figure>""",
}


def mean(xs):
    return sum(xs) / len(xs)


def chart_data():
    R = JOULE / "results"
    ppl = {l.split()[0]: float(l.split("PPL = ")[1].split()[0]) for l in open(R / "quant-ppl-1.5b.txt")}
    runs = [{r["model"].split("-")[1].split(".")[0]: r for r in json.load(open(R / f))["results"] if r["phase"] == "decode"}
            for f in ("quant-energy-1.5b.json", "quant-energy-1.5b-run2.json")]
    formats = [{"name": k, "ppl": round(ppl[k], 2),
                "soc": round(mean([r[k]["soc_j_per_tok"] for r in runs]) * 1e3, 1),
                "board": round(mean([r[k]["sys_j_per_tok"] for r in runs]) * 1e3, 1)} for k in runs[0]]

    def batch(q):
        d = json.load(open(R / f"batching-gpu-1.5b-{q}.json"))["runs"]
        return [{"batch": d[0][i]["batch"], "mj": round(mean([r[i]["soc_mj_per_tok"] for r in d]), 1),
                 "gpu_w": round(mean([r[i]["gpu_w"] for r in d]), 1)} for i in range(len(d[0]))]

    def baseline(f, model):
        rows = json.load(open(R / f))["results"]
        return [{"model": model, "phase": r["phase"], "tps": round(r["tokens_per_s"], 1),
                 "chip": round(r["soc_j_per_tok"] * 1e3, 1), "board": round(r["sys_j_per_tok"] * 1e3, 1)} for r in rows]

    first = json.load(open(R / "repeat-1.json"))["results"]
    results = []
    for r in first:
        name = "Qwen2.5 0.5B" if "0.5b" in r["model"] else "Qwen2.5 1.5B"
        results.append({"model": name, "phase": r["phase"], "tps": round(r["tokens_per_s"], 1),
                        "chip": round(r["soc_j_per_tok"] * 1e3, 1), "board": round(r["sys_j_per_tok"] * 1e3, 1)})
    results += baseline("7b-1.json", "Qwen2.5 7B")
    roofline = json.load(open(R / "roofline-1.5b.json"))
    s7 = json.load(open(R / "summary-7b.json"))["rows"]
    formats7 = [{"name": r["format"], "ppl": round(r["ppl"], 2), "soc": round(r["soc_mj"], 1), "board": round(r["board_mj"], 1),
                 **({"note": "(did not repeat)"} if r["spread_board"] > .05 else {})} for r in s7]
    two = [{k: (round(v, 1) if isinstance(v, float) else v) for k, v in r.items()}
           for r in json.load(open(R / "summary-two-machines.json"))]
    kernels = json.load(open(R / "summary-kernels.json"))
    spec = [{k: (round(v, 4) if isinstance(v, float) else v) for k, v in r.items() if k != "soc_range"}
            for r in json.load(open(R / "summary-speculative.json"))]
    import csv
    names = {"NVIDIA H100-NVL-94GB": "8x H100 NVL", "NVIDIA B200-SXM-180GB": "8x B200"}
    models = {"llama2-70b-99": "Llama 2 70B", "llama3.1-8b": "Llama 3.1 8B", "llama3.1-405b": "Llama 3.1 405B"}
    mwh = [{"system": names[r["accelerator"]], "model": models[r["model"]], "dtype": r["dtype"].upper(),
            "j_per_tok": float(r["j_per_tok"])}
           for r in csv.DictReader(open(R / "mlperf-llm-power.csv"))
           if r["scenario"] == "Offline" and r["model"] in models]
    width = [{k: (round(v, 2) if isinstance(v, float) else v) for k, v in r.items()}
             for r in json.load(open(R / "summary-width.json"))]
    return {"formats": formats, "formats7": formats7, "two": two, "kernels": kernels, "width": width, "spec": spec, "mwh": mwh, "batch": {"q4_0": batch("q4_0"), "q4_k_m": batch("q4_k_m")},
            "results": results, "roofline": roofline}


def notes_list(root):
    items = []
    for n in reversed(NOTES):
        title, date = note_meta(n)
        items.append(f'<a class="note-card" href="{root}research/{n["slug"]}/">'
                     f'<span class="mono">N{n["n"]} &middot; {date}</span><h3>{title}</h3><p>{n["summary"]}</p>'
                     f'<span class="mono go">Read note &rarr;</span></a>')
    return '<div class="notes">' + "".join(items) + "</div>"


def note_meta(n):
    text = (JOULE / "notes" / n["file"]).read_text()
    title = re.search(r"^# (.+)$", text, re.M).group(1)
    date = re.search(r"(\d{1,2} \w+ 20\d\d)", text).group(1)
    return title, date


def note_body(n):
    text = (JOULE / "notes" / n["file"]).read_text()
    text = re.sub(r"^# .+\n", "", text, count=1, flags=re.M)
    lede, _, rest = text.strip().partition("\n\n")
    html = markdown.markdown(rest, extensions=["tables", "fenced_code"])
    html = re.sub(r"<p><!-- chart:(\w+) --></p>|<!-- chart:(\w+) -->", lambda m: FIGURES[m.group(1) or m.group(2)], html)
    html = re.sub(r"<h2>(.+?)</h2>", lambda m: f'<h2 data-via>{m.group(1)}</h2>', html)
    html = html.replace('href="../', 'href="https://github.com/splicedso/joule/blob/main/')
    return lede, html


def page(path, content, *, title, description, page, sheet, sheetno, scripts="", root=None, ogtype="website"):
    depth = len(Path(path).parts) - 1
    root = "../" * depth if root is None else root
    url_path = "" if path == "index.html" else path.removesuffix("index.html")
    if not path.startswith("404"):
        PAGES.append(url_path)
    html = (SRC / "base.html").read_text()
    for k, v in {"content": content, "title": title, "description": description, "page": page,
                 "sheet": sheet, "sheetno": sheetno, "date": time.strftime("%Y-%m"),
                 "scripts": scripts.replace("{{root}}", root), "root": root, "version": VERSION,
                 "site": SITE, "path": url_path, "ogtype": ogtype}.items():
        html = html.replace("{{" + k + "}}", v)
    out = HERE / path
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html)
    return out


def main():
    assets = HERE / "assets"
    for f in ("style.css", "site.js", "charts.js", "home.js"):
        shutil.copy(SRC / f, assets / f)
    (assets / "data.json").write_text(json.dumps(chart_data(), separators=(",", ":")))
    total = len(NOTES) + 4
    charts = '<script src="{{root}}assets/charts.js?v=' + VERSION + '"></script>'

    page("index.html", (SRC / "pages/home.html").read_text().replace("{{notes}}", notes_list("")),
         title="Spliced", description="A research lab for efficient inference. We measure what a token costs, at the chip and at the board.",
         page="home", sheet="Spliced &middot; Efficient inference", sheetno=f"1 of {total}",
         scripts='<script src="{{root}}assets/home.js?v=' + VERSION + '"></script>')
    page("research/index.html", (SRC / "pages/research.html").read_text().replace("{{notes}}", notes_list("../")),
         title="Research &middot; Spliced", description="Spliced research notes on inference energy, with method, code and raw data.",
         page="research", sheet="Research", sheetno=f"2 of {total}")
    page("tools/joule/index.html", (SRC / "pages/joule.html").read_text(),
         title="joule &middot; Spliced", description="Energy per token for local LLM inference, at the chip and the board.",
         page="tools", sheet="Tools / joule", sheetno=f"3 of {total}", scripts=charts)
    page("lab/index.html", (SRC / "pages/lab.html").read_text(),
         title="Lab &middot; Spliced", description="Spliced is a small research lab for efficient inference.",
         page="lab", sheet="Lab", sheetno=f"4 of {total}")
    for i, n in enumerate(NOTES):
        title, date = note_meta(n)
        lede, body = note_body(n)
        content = f"""<header class="page-head">
  <div class="wrap">
    <span class="refdes mono" data-via><b>N{n['n']}</b> Research note &middot; {date}</span>
    <h1>{title}</h1>
    <p class="lede">{markdown.markdown(lede)[3:-4]}</p>
  </div>
</header>
<main><article class="wrap note-body">{body}
<p class="source mono">Source, scripts and raw data: <a href="https://github.com/splicedso/joule/blob/main/notes/{n['file']}">joule/notes/{n['file']}</a></p>
</article></main>"""
        page(f"research/{n['slug']}/index.html", content, title=f"{title} &middot; Spliced", description=n["summary"],
             page="research", sheet=f"N{n['n']} &middot; {title}", sheetno=f"{5 + i} of {total}", scripts=charts,
             ogtype="article")
    page("404.html", (SRC / "pages/404.html").read_text(), title="Not found &middot; Spliced",
         description="This page does not exist.", page="404", sheet="Not found", sheetno="&mdash;", root="/")
    (HERE / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "".join(f"  <url><loc>{SITE}/{p}</loc><lastmod>{time.strftime('%Y-%m-%d')}</lastmod></url>\n" for p in PAGES)
        + "</urlset>\n")
    (HERE / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n")
    cname = HERE / "CNAME"
    if CONFIG.get("domain"):
        cname.write_text(CONFIG["domain"] + "\n")
    elif cname.exists():
        cname.unlink()
    print("built", total, "pages for", SITE)


if __name__ == "__main__":
    main()
