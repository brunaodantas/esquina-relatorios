#!/usr/bin/env python3
"""
PDF do relatorio mensal, cortado nas fronteiras reais das secoes do template.
Screenshot da pagina inteira (Playwright, 2x) e corte por secao, nunca impressao
do navegador.
"""
import asyncio
from pathlib import Path
from PIL import Image
from playwright.async_api import async_playwright

BASE = Path(__file__).parent
SRC = BASE / "index.html"
PDF_OUT = BASE / "relatorio-campinas-06ago-07set2026.pdf"
SLIDES = BASE / "slides_png"
W, SCALE, RES = 1000, 2, 192
PAGE_RATIO = 1.414          # A4 retrato

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={"width": W, "height": 1400}, device_scale_factor=SCALE)
        await pg.goto(SRC.as_uri(), wait_until="networkidle")
        await pg.evaluate("document.documentElement.classList.remove('js');"
                          "document.querySelectorAll('.fade-in').forEach(e=>e.classList.add('visible'))")
        await pg.wait_for_timeout(1200)
        bounds = await pg.evaluate(
            "[...document.querySelectorAll('section,.meta-wrap,.diag,footer')]"
            ".map(e=>Math.round(e.getBoundingClientRect().bottom+scrollY))")
        await pg.screenshot(path=str(BASE / "_full.png"), full_page=True)
        await b.close()

    im = Image.open(BASE / "_full.png").convert("RGB")
    Wp, Hp = im.size
    page_h = int(Wp * PAGE_RATIO)
    cuts = sorted({int(x * SCALE) for x in bounds if 0 < x * SCALE <= Hp})

    pages, y = [], 0
    while y < Hp:
        limit = y + page_h
        if limit >= Hp:
            pages.append((y, Hp)); break
        cand = [c for c in cuts if y + page_h * 0.35 < c <= limit]
        end = max(cand) if cand else limit
        pages.append((y, end)); y = end

    SLIDES.mkdir(exist_ok=True)
    imgs = []
    for i, (a, z) in enumerate(pages, 1):
        canvas = Image.new("RGB", (Wp, page_h), (255, 255, 255))
        canvas.paste(im.crop((0, a, Wp, z)), (0, 0))
        canvas.save(SLIDES / f"slide_{i:02d}.png")
        imgs.append(canvas)
        print(f"  [{i}/{len(pages)}] slide_{i:02d}.png  ({z-a}px)")
    imgs[0].save(str(PDF_OUT), save_all=True, append_images=imgs[1:], resolution=RES)
    (BASE / "_full.png").unlink()
    print(f"PDF: {PDF_OUT} ({len(imgs)} paginas, {PDF_OUT.stat().st_size/1_048_576:.1f} MB)")

asyncio.run(main())
