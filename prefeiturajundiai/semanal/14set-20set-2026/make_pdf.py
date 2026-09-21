#!/usr/bin/env python3
"""
Gera o PDF vertical (540x960 pt) do boletim a partir do index.html.
Metodo: screenshot da pagina inteira (Playwright, 2x, details abertos) e corte
em paginas nas fronteiras dos blocos. Nunca impressao do navegador.

Dependencias: pip install playwright pillow && python -m playwright install chromium
"""
import asyncio
import re
from pathlib import Path
from PIL import Image
from playwright.async_api import async_playwright

BASE = Path(__file__).parent
SRC = BASE / "index.html"
PDF_OUT = BASE / "boletim-prefeitura-jundiai-14a20set2026.pdf"
W, SCALE, RES = 720, 2, 192          # 1440/192*72 = 540pt de largura
PAGE_RATIO = 960 / 540               # pagina vertical 9:16

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={"width": W, "height": 1280}, device_scale_factor=SCALE)
        await pg.goto(SRC.as_uri(), wait_until="networkidle")
        await pg.evaluate("document.querySelectorAll('details').forEach(d=>d.open=true)")
        await pg.wait_for_timeout(900)
        # blocos atomicos: nunca podem ser cortados ao meio
        blocks = await pg.evaluate("""() => {
          const sel = 'header.hero, .hc, .card, .ins, .prose > p, .perf-card, .perf-ins, .perf-metrics, .perf-top, .perf-title, .cx-item, .cxh, ul.cl > li, table, .dsec-top, footer.wrap p, h2, h3';
          return [...document.querySelectorAll(sel)].map(e => {
            const r = e.getBoundingClientRect();
            return [r.top + window.scrollY, r.bottom + window.scrollY];
          }).filter(b => b[1] > b[0]);
        }""")
        bg = await pg.evaluate("getComputedStyle(document.body).backgroundColor")
        total = await pg.evaluate("document.body.scrollHeight")
        await pg.screenshot(path=str(BASE / "_full.png"), full_page=True)
        await b.close()

    m = re.findall(r'\d+', bg or '')
    fill = tuple(int(x) for x in m[:3]) if len(m) >= 3 else (255, 255, 255)
    im = Image.open(BASE / "_full.png").convert("RGB")
    Wp, Hp = im.size
    page_h = int(Wp * PAGE_RATIO)
    blocks = [(int(t * SCALE), int(bt * SCALE)) for t, bt in blocks]
    tops = sorted({t for t, _ in blocks})
    pages, y = [], 0
    while y < Hp:
        limit = y + page_h
        if limit >= Hp:
            pages.append((y, Hp)); break
        # corta no topo do primeiro bloco que ultrapassa o limite
        cand = [t for t in tops if y + page_h * 0.3 < t <= limit]
        end = max(cand) if cand else limit
        # se ainda assim algum bloco cruza o corte, recua para o topo dele
        for t, bt in blocks:
            if t < end < bt and t > y + page_h * 0.25:
                end = min(end, t)
        pages.append((y, end)); y = end

    imgs = []
    for a, bnd in pages:
        canvas = Image.new("RGB", (Wp, page_h), fill)
        canvas.paste(im.crop((0, a, Wp, bnd)), (0, 0))
        imgs.append(canvas)

    imgs[0].save(str(PDF_OUT), save_all=True, append_images=imgs[1:], resolution=RES)
    (BASE / "_full.png").unlink()
    print(f"PDF gerado: {PDF_OUT} · {len(imgs)} paginas · {PDF_OUT.stat().st_size/1048576:.1f} MB")

asyncio.run(main())
