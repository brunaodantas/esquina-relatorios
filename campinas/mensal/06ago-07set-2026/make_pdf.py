#!/usr/bin/env python3
"""PDF em slides 16:9 (1280x720), screenshot por slide via Playwright + Pillow."""
import asyncio
from pathlib import Path
from PIL import Image
from playwright.async_api import async_playwright

BASE        = Path(__file__).parent
SLIDES_FILE = BASE / "slides.html"
SLIDES_DIR  = BASE / "slides_png"
PDF_OUT     = BASE / "relatorio-campinas-06ago-07set2026.pdf"
W, H        = 1280, 720
SCALE, RES  = 2, 192

async def main():
    SLIDES_DIR.mkdir(exist_ok=True)
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": W, "height": H}, device_scale_factor=SCALE)
        await page.goto(SLIDES_FILE.as_uri(), wait_until="networkidle")
        await page.wait_for_timeout(1800)
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
    print(f"PDF: {PDF_OUT} ({len(imgs)} slides, {PDF_OUT.stat().st_size/1_048_576:.1f} MB)")

asyncio.run(main())
