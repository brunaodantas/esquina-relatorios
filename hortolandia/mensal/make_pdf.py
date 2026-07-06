#!/usr/bin/env python3
"""
Gera prints de alta qualidade dos slides (16:9) e monta o PDF final.
Modelo: PNAE 2026 (slides 960×540pt). Prints a 2560×1440 (scale 2) → PDF 960×540pt.
Uso: python3.9 make_pdf.py
Dependências: playwright pillow  ·  playwright install chromium
"""
import asyncio
from pathlib import Path
from PIL import Image
from playwright.async_api import async_playwright

BASE        = Path(__file__).parent
SLIDES_FILE = BASE / "slides.html"
SLIDES_DIR  = BASE / "slides_png"
PDF_OUT     = BASE / "relatorio-hortolandia-temasdiversos-jun2026.pdf"
W, H        = 1280, 720
SCALE       = 2       # 2560×1440 por slide
RES         = 192     # 2560/192*72 = 960pt · 1440/192*72 = 540pt (igual PNAE)

async def main():
    SLIDES_DIR.mkdir(exist_ok=True)
    url = SLIDES_FILE.as_uri()
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": W, "height": H}, device_scale_factor=SCALE)
        await page.goto(url, wait_until="networkidle")
        await page.wait_for_timeout(1500)  # garante render dos charts
        n = await page.locator(".slide").count()
        print(f"Encontrados {n} slides.")
        paths = []
        for i in range(n):
            out = SLIDES_DIR / f"slide_{i+1:02d}.png"
            await page.locator(".slide").nth(i).scroll_into_view_if_needed()
            await page.locator(".slide").nth(i).screenshot(path=str(out), scale="device")
            paths.append(out)
            print(f"  [{i+1}/{n}] {out.name}")
        await browser.close()
    imgs = [Image.open(p).convert("RGB") for p in paths]
    imgs[0].save(str(PDF_OUT), save_all=True, append_images=imgs[1:], resolution=RES)
    print(f"\nPDF gerado: {PDF_OUT}")
    print(f"Tamanho: {PDF_OUT.stat().st_size/1_048_576:.1f} MB")

asyncio.run(main())
