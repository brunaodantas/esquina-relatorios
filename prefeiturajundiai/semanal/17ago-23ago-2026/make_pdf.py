#!/usr/bin/env python3
"""
Gera o PDF vertical (540x960 pt) do boletim a partir do index.html.
Metodo: screenshot da pagina inteira (Playwright, 2x, details abertos) e corte
em paginas nas fronteiras dos blocos. Nunca impressao do navegador.

Dependencias: pip install playwright pillow && python -m playwright install chromium
"""
import asyncio
from pathlib import Path
from PIL import Image
from playwright.async_api import async_playwright

BASE = Path(__file__).parent
SRC = BASE / "index.html"
PDF_OUT = BASE / "boletim-prefeitura-jundiai-17a23ago2026.pdf"
W, SCALE, RES = 720, 2, 192          # 1440/192*72 = 540pt de largura
PAGE_RATIO = 960 / 540               # pagina vertical 9:16

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={"width": W, "height": 1280}, device_scale_factor=SCALE)
        await pg.goto(SRC.as_uri(), wait_until="networkidle")
        await pg.evaluate("document.querySelectorAll('details').forEach(d=>d.open=true)")
        await pg.wait_for_timeout(900)
        # fronteiras candidatas: fim de cada bloco de topo
        bounds = await pg.evaluate("""() => {
          const sel = 'header.hero, section.wrap, .creatives > details, footer.wrap, .card, .ins, ul.cl > li';
          return [...document.querySelectorAll(sel)].map(e => {
            const r = e.getBoundingClientRect();
            return r.bottom + window.scrollY;
          });
        }""")
        total = await pg.evaluate("document.body.scrollHeight")
        await pg.screenshot(path=str(BASE / "_full.png"), full_page=True)
        await b.close()

    im = Image.open(BASE / "_full.png").convert("RGB")
    Wp, Hp = im.size
    page_h = int(Wp * PAGE_RATIO)
    cuts = sorted({int(b * SCALE) for b in bounds if 0 < b * SCALE < Hp})
    pages, y = [], 0
    while y < Hp:
        limit = y + page_h
        if limit >= Hp:
            pages.append((y, Hp)); break
        cand = [c for c in cuts if y + page_h * 0.45 < c <= limit]
        end = max(cand) if cand else limit
        pages.append((y, end)); y = end

    imgs = []
    for a, bnd in pages:
        canvas = Image.new("RGB", (Wp, page_h), (255, 255, 255))
        canvas.paste(im.crop((0, a, Wp, bnd)), (0, 0))
        imgs.append(canvas)
    imgs[0].save(str(PDF_OUT), save_all=True, append_images=imgs[1:], resolution=RES)
    (BASE / "_full.png").unlink()
    print(f"PDF gerado: {PDF_OUT} · {len(imgs)} paginas · {PDF_OUT.stat().st_size/1048576:.1f} MB")

asyncio.run(main())
