#!/usr/bin/env python3
"""PDF em slides 16:9 do relatório mensal E3 (960×540 pt), a partir de um slides.html próprio.
Uso: python3 make_pdf.py  (na pasta do relatório; lê index.html, gera slides.html, slides_png/ e o PDF)."""
import asyncio, re, sys
from pathlib import Path
from PIL import Image
from playwright.async_api import async_playwright
BASE = Path(__file__).parent
PDF_OUT = BASE / "relatorio-campinas-concilia-setembro2026.pdf"
W, H, SCALE, RES = 1280, 720, 2, 192
CSS = """<style id="pdf-mode">.anim,.anim *{opacity:1!important;transform:none!important;transition:none!important;animation:none!important}
html{scroll-snap-type:none!important;scroll-behavior:auto!important}
.slide{height:720px!important;min-height:720px!important;max-height:720px!important;overflow:hidden!important}
[class*="dots"],[class*="progress"],.chapter-label,#nav,#dots,#progress,#chapter{display:none!important}</style>"""
def make_slides():
    s = (BASE / "index.html").read_text(encoding="utf-8")
    s = s.replace("</head>", CSS + "\n</head>", 1)
    (BASE / "slides.html").write_text(s, encoding="utf-8")
async def main():
    make_slides()
    out_dir = BASE / "slides_png"; out_dir.mkdir(exist_ok=True)
    for f in out_dir.glob("*.png"): f.unlink()
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={"width": W, "height": H}, device_scale_factor=SCALE)
        await pg.goto((BASE / "slides.html").as_uri(), wait_until="networkidle"); await pg.wait_for_timeout(1500)
        await pg.evaluate("document.querySelectorAll('*').forEach(e=>{if(getComputedStyle(e).position==='fixed'&&!e.closest('.slide'))e.style.display='none'})")
        n = await pg.locator(".slide").count(); paths = []
        for i in range(n):
            el = pg.locator(".slide").nth(i); await el.scroll_into_view_if_needed(); await pg.wait_for_timeout(200)
            bb = await el.bounding_box(); assert abs(bb["height"] - H) < 2, (i + 1, bb)
            o = out_dir / f"slide_{i+1:02d}.png"; await el.screenshot(path=str(o), scale="device"); paths.append(o)
        await b.close()
    imgs = [Image.open(x).convert("RGB") for x in paths]
    imgs[0].save(str(PDF_OUT), save_all=True, append_images=imgs[1:], resolution=RES)
    print(PDF_OUT.name, n, "slides")
asyncio.run(main())
