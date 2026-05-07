import asyncio
import base64
from pathlib import Path

from playwright.async_api import async_playwright


async def _capture(
    html_path: str,
    output_dir: Path,
    count: int,
    wait_ms: int,
    interaction_wait_ms: int,
    viewport: dict,
) -> tuple[list[str], list[str]]:
    output_dir.mkdir(parents=True, exist_ok=True)
    file_url = f"file://{Path(html_path).resolve()}"
    screenshots = []
    errors = []

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        ctx = await browser.new_context(viewport=viewport)
        page = await ctx.new_page()

        page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
        page.on("pageerror", lambda e: errors.append(str(e)))

        await page.goto(file_url)
        await page.wait_for_timeout(wait_ms)

        for i in range(count):
            path = output_dir / f"screenshot_{i:02d}.png"
            await page.screenshot(path=str(path))
            screenshots.append(base64.b64encode(path.read_bytes()).decode())
            if i < count - 1:
                await page.wait_for_timeout(interaction_wait_ms)

        await browser.close()

    return screenshots, errors


def capture(
    html_path: str,
    output_dir: Path,
    count: int = 3,
    wait_ms: int = 2000,
    interaction_wait_ms: int = 1000,
    viewport: dict | None = None,
) -> tuple[list[str], list[str]]:
    vp = viewport or {"width": 800, "height": 600}
    return asyncio.run(_capture(html_path, output_dir, count, wait_ms, interaction_wait_ms, vp))
