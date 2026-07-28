#!/usr/bin/env python3
"""
Gera o PDF de slides 16:9 (960x540 pt) a partir de um slides.html.
Copie este arquivo para a MESMA pasta do slides.html e rode:  python make_pdf.py

Método: screenshot de cada .slide (Playwright, 2x) montado em PDF (Pillow).
NÃO usa impressão do navegador (que corta e vira A4).

Dependências (uma vez): pip install playwright pillow && python -m playwright install chromium
"""
import asyncio
from pathlib import Path
from PIL import Image
from playwright.async_api import async_playwright

BASE = Path(__file__).parent
SLIDES_FILE = BASE / "slides.html"
SLIDES_DIR = BASE / "slides_png"
PDF_OUT = BASE / "relatorio-americana-temasdiversos-jul2026.pdf"
W, H, SCALE, RES = 1280, 720, 2, 192  # 2560/192*72 = 960pt · 1440/192*72 = 540pt

async def main():
    if not SLIDES_FILE.exists():
        raise SystemExit(f"Nao encontrei {SLIDES_FILE}. Coloque este make_pdf.py na mesma pasta do slides.html.")
    SLIDES_DIR.mkdir(exist_ok=True)
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": W, "height": H}, device_scale_factor=SCALE)
        await page.goto(SLIDES_FILE.as_uri(), wait_until="networkidle")
        await page.wait_for_timeout(1500)  # deixa os charts renderizarem
        n = await page.locator(".slide").count()
        if n == 0:
            raise SystemExit("Nenhum elemento .slide encontrado no slides.html.")
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
    print(f"\nPDF gerado: {PDF_OUT}  ({PDF_OUT.stat().st_size/1_048_576:.1f} MB)")

asyncio.run(main())
