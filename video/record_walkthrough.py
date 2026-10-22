"""Record an actual 60-second notebook walkthrough in headless Google Chrome.

Start a local HTTP server for app/site on port 8765, then run this script.
Uses Playwright's 25 fps capture; trims startup and converts to H.264 with ffmpeg.
"""
import asyncio
import json
import subprocess
import time
from pathlib import Path
from playwright.async_api import async_playwright

ROOT = Path(__file__).resolve().parents[1]


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            executable_path="/usr/bin/google-chrome", headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage", "--enable-webgl",
                  "--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"])
        # Load the WASM runtime in one page before creating the recorded page.
        context = await browser.new_context(viewport={"width": 1920, "height": 1080},
                                            device_scale_factor=1, locale="en-US",
                                            record_video_dir="/tmp/oracle-audit-recordings",
                                            record_video_size={"width": 1920, "height": 1080})
        page = await context.new_page()
        created = time.monotonic()
        errors = []
        page.on("pageerror", lambda e: errors.append(str(e)))
        await page.goto("http://127.0.0.1:8765/", wait_until="domcontentloaded")
        await page.get_by_role("button", name="load a random real AMP", exact=True).wait_for(timeout=180000)
        await page.locator("svg.marks,canvas").first.wait_for(timeout=180000)
        await page.wait_for_timeout(6000)
        # Headless captures omit the OS cursor. Render a small ordinary pointer
        # at real mouse coordinates, without modifying any app output or controls.
        await page.evaluate("""() => {
          const c=document.createElement('div'); c.id='recording-cursor';
          c.style.cssText='position:fixed;left:0;top:0;width:23px;height:28px;z-index:2147483647;pointer-events:none;filter:drop-shadow(0 1px 1px #777)';
          c.innerHTML='<svg viewBox="0 0 24 28"><path d="M2 2 L2 23 L8 17 L12 26 L16 24 L12 15 L21 15 Z" fill="white" stroke="#111" stroke-width="1.5"/></svg>';
          document.body.append(c);
          document.addEventListener('mousemove',e=>{c.style.left=e.clientX+'px';c.style.top=e.clientY+'px'});
        }""")
        await page.mouse.move(1640, 170)
        await page.evaluate("window.scrollTo(0,0)")
        await page.wait_for_timeout(500)
        trim_start = time.monotonic() - created
        start = time.monotonic()
        shots = []

        async def hold_until(second):
            await page.wait_for_timeout(max(0, second-(time.monotonic()-start))*1000)

        async def scroll_to(locator, top=70):
            await locator.evaluate("(el,top)=>{el.style.scrollMarginTop=top+'px';el.scrollIntoView({block:'start',behavior:'smooth'})}", top)
            await page.wait_for_timeout(1200)

        async def shot(name):
            shots.append({"name": name, "time": round(time.monotonic()-start, 3)})
            print(name, flush=True)

        async def click(locator):
            box = await locator.bounding_box()
            await page.mouse.move(box['x']+box['width']/2, box['y']+box['height']/2, steps=8)
            await locator.click()

        async def evidence(name):
            await page.screenshot(path=str(ROOT / "video" / f"capture_{name}.png"))

        await shot("title")
        await evidence("title")
        await hold_until(5)

        await shot("load_peptide")
        explorer = page.get_by_role("heading", name="1. Audit any peptide", exact=True)
        await scroll_to(explorer)
        await click(page.get_by_role("button", name="load a random real AMP", exact=True))
        await page.wait_for_timeout(1200)
        # Display the wheels beneath the sequence and feature cards.
        # Matplotlib's two-wheel figure is the first image in this notebook.
        await scroll_to(page.locator('img').first, top=130)
        await evidence("wheels")
        await hold_until(12)

        await shot("helix")
        helix_heading = page.get_by_role("heading", name="1.1 The same peptide as a 3D helix", exact=True)
        await scroll_to(helix_heading)
        iframe = page.locator('iframe').first
        frame = await (await iframe.element_handle()).content_frame()
        canvases = frame.locator('canvas')
        has_3d = await canvases.count() > 0
        if has_3d:
            box = await canvases.first.bounding_box()
            await page.mouse.move(box['x']+box['width']*.3, box['y']+box['height']*.5, steps=6)
            await page.mouse.down()
            await page.mouse.move(box['x']+box['width']*.8, box['y']+box['height']*.55, steps=8)
            await page.mouse.up()
        await evidence("helix")
        await hold_until(17)

        await shot("compare_wheels")
        await scroll_to(page.locator('img').first, top=100)
        await hold_until(22)

        await shot("surrogate_scores")
        await scroll_to(page.get_by_role("heading", name="composition surrogate — as given", exact=True), top=130)
        await evidence("surrogate")
        await hold_until(26)

        await shot("change_oracle")
        await scroll_to(page.get_by_role("heading", name="0. The audit — pick an oracle, move the threshold", exact=True))
        oracle = page.locator('marimo-dropdown').first.get_by_role('button')
        await click(oracle)
        await page.wait_for_timeout(400)
        await page.get_by_role('option', name='B - amPEPpy', exact=True).click()
        await page.get_by_text('Oracle: ampeppy', exact=False).wait_for()
        await page.wait_for_timeout(800)
        await evidence("ampeppy")
        await hold_until(31)
        await click(oracle)
        await page.get_by_role('option', name='A - broad', exact=True).click()
        await page.get_by_text('Oracle: broad-classifier', exact=False).wait_for()
        await page.wait_for_timeout(800)
        await evidence("broad")
        await hold_until(35)

        await shot("threshold")
        slider = page.get_by_role('slider').nth(0)
        box = await slider.bounding_box()
        await page.mouse.move(box['x']+8, box['y']+8, steps=6)
        await page.mouse.down()
        await page.mouse.move(box['x']-40, box['y']+8, steps=8)
        await page.mouse.up()
        await page.wait_for_timeout(1000)
        await slider.hover()
        await page.mouse.down()
        await page.mouse.move(box['x']+8, box['y']+8, steps=8)
        await page.mouse.up()
        value = float(await slider.get_attribute('aria-valuenow'))
        # Correct only a possible one-step pixel-rounding difference.
        for _ in range(round(abs(value-.5)/.01)):
            await slider.press('ArrowRight' if value < .5 else 'ArrowLeft')
        await page.wait_for_timeout(800)
        await evidence("threshold")
        await hold_until(41)

        await shot("generate")
        await scroll_to(page.get_by_role("heading", name="2. Generate control sequences", exact=True))
        # Slider order: threshold, MIC, shuffle seed, n, length, seed, sampler threshold.
        count = page.get_by_role('slider').nth(3)
        count_box = await count.bounding_box()
        await page.mouse.move(count_box['x']+8,count_box['y']+8,steps=6)
        await page.mouse.down()
        await page.mouse.move(count_box['x']+36,count_box['y']+8,steps=8)
        await page.mouse.up()
        await page.wait_for_timeout(1200)
        await evidence("generated")
        await hold_until(49)

        await shot("depth")
        await scroll_to(page.get_by_role("heading", name="0.2 How many candidates would you select?", exact=True))
        await evidence("depth")
        await hold_until(55)

        await shot("provenance")
        await scroll_to(page.get_by_role("heading", name="Data provenance", exact=True))
        await evidence("footer")
        await hold_until(60)
        video = page.video
        await context.close()
        webm = await video.path()
        await browser.close()
        manifest = {"browser": "Google Chrome headless", "viewport": [1920,1080],
                    "source": "local corrected WASM export", "trim_start": trim_start,
                    "duration": 60, "fps": 25, "3d_canvas_rendered": has_3d,
                    "page_errors": errors, "shots": shots, "webm": str(webm)}
        (ROOT/'video'/'capture_manifest.json').write_text(json.dumps(manifest, indent=2))
        subprocess.run(['ffmpeg', '-y', '-v', 'error', '-ss', str(trim_start), '-i', str(webm),
                        '-t', '60', '-vf', 'fps=25,tpad=stop_mode=clone:stop_duration=1',
                        '-c:v', 'libx264', '-crf', '18',
                        '-pix_fmt', 'yuv420p', '-an', '-movflags', '+faststart',
                        str(ROOT/'oracle_audit_app_capture.mp4')], check=True)
        print(json.dumps(manifest), flush=True)


if __name__ == '__main__':
    asyncio.run(main())
