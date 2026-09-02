#!/usr/bin/env python3
"""
Gera o PDF vertical (540x960 pt) do boletim a partir do proprio index.html.
Corta nas fronteiras de bloco (header/section), nunca no meio de texto.
Rodar na mesma pasta:  python3 make_pdf.py
"""
import asyncio
from pathlib import Path
from PIL import Image
from playwright.async_api import async_playwright

BASE = Path(__file__).parent
SRC = BASE / "index.html"
OUTDIR = BASE / "slides_png"
PDF_OUT = BASE / "boletim-campinas-semanal-26ago-01set2026.pdf"
W, H, SCALE, RES = 720, 1280, 2, 192

async def main():
    OUTDIR.mkdir(exist_ok=True)
    async with async_playwright() as p:
        b = await p.chromium.launch()
        page = await b.new_page(viewport={"width": W, "height": H}, device_scale_factor=SCALE)
        await page.goto(SRC.as_uri(), wait_until="networkidle")
        await page.evaluate("document.querySelectorAll('details').forEach(d=>d.open=true)")
        await page.evaluate("document.querySelectorAll('.dtoggle,.cr-toggle').forEach(e=>e.style.display='none')")
        await page.wait_for_timeout(1200)
        blocks = await page.evaluate("""
          (() => {
            const SEL = 'nav, .hero-intro, header .eb, header .hc, section .sn, section h2, section .sl, section .card, section .ins, section h3, .cr, .common';
            const out = [];
            document.querySelectorAll(SEL).forEach(e => {
              if (e.closest('.cr') && !e.matches('.cr')) return;
              if (e.closest('.common') && !e.matches('.common')) return;
              const r = e.getBoundingClientRect();
              if (r.height < 2) return;
              out.push({top: Math.round(r.top + scrollY), h: Math.round(r.height)});
            });
            const f = document.querySelector('footer');
            if (f) { const r = f.getBoundingClientRect(); out.push({top: Math.round(r.top+scrollY), h: Math.round(r.height)}); }
            out.sort((a,b) => a.top - b.top);
            return out;
          })()
        """)
        total = await page.evaluate("document.documentElement.scrollHeight")
        # agrupa blocos em paginas de ate H px
        pages, cur_start, cur_end = [], None, None
        for blk in blocks:
            b_top, b_bot = blk["top"], blk["top"] + blk["h"]
            if cur_start is None:
                cur_start, cur_end = b_top, b_bot; continue
            if b_bot - cur_start > H:
                pages.append((cur_start, cur_end - cur_start))
                cur_start, cur_end = b_top, b_bot
            else:
                cur_end = max(cur_end, b_bot)
        if cur_start is not None: pages.append((cur_start, cur_end - cur_start))
        # bloco isolado maior que a pagina: fatia
        final = []
        for top, h in pages:
            if h <= H: final.append((top, h)); continue
            k = 0
            while k < h:
                final.append((top + k, min(H, h - k))); k += H
        pages = final
        print(f"{len(blocks)} blocos, altura total {total}px, {len(pages)} paginas")
        full = OUTDIR / "_full.png"
        await page.screenshot(path=str(full), full_page=True)
        await b.close()
    src = Image.open(full).convert("RGB")
    bg = src.getpixel((5,5))
    paths = []
    for i,(top,h) in enumerate(pages):
        box = (0, top*SCALE, W*SCALE, min((top+h)*SCALE, src.height))
        crop = src.crop(box)
        canvas = Image.new("RGB", (W*SCALE, H*SCALE), bg)
        canvas.paste(crop, (0,0))
        out = OUTDIR / f"slide_{i+1:02d}.png"
        canvas.save(out); paths.append(out)
        print(f"  [{i+1}/{len(pages)}] {out.name}")
    imgs = [Image.open(p).convert("RGB") for p in paths]
    imgs[0].save(str(PDF_OUT), save_all=True, append_images=imgs[1:], resolution=RES)
    full.unlink(missing_ok=True)
    print(f"PDF: {PDF_OUT} ({PDF_OUT.stat().st_size/1_048_576:.1f} MB)")

asyncio.run(main())
