import asyncio
import base64
from pathlib import Path
from http.server import SimpleHTTPRequestHandler
from socketserver import TCPServer
from playwright.async_api import async_playwright

class CustomHTTPRequestHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cross-Origin-Opener-Policy", "same-origin")
        self.send_header("Cross-Origin-Embedder-Policy", "require-corp")
        super().end_headers()

class PPTXtoPDFConverter:
    def __init__(self, headless=True):
        self.headless = headless
        self.root_path = Path(__file__).parent.resolve()
        handler = lambda *args, **kwargs: CustomHTTPRequestHandler(*args, directory=str(self.root_path), **kwargs)
        self.server = TCPServer(("localhost", 8000), handler)
        asyncio.get_event_loop().run_in_executor(None, self.server.serve_forever)

    async def _convert(self, pptx_path):
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=self.headless)
            page = await browser.new_page()
            page.on("console", lambda msg: print(f"LOG: {msg.text}"))

            with open(pptx_path, "rb") as f:
                pptx_b64 = base64.b64encode(f.read()).decode()

            await page.goto("http://localhost:8000/index.html")

            await page.wait_for_function("window.sofficeLoaded === true", timeout=120000)
            pdf_b64 = await page.evaluate(f'convertPPTX("{pptx_b64}")')

            await browser.close()
            return base64.b64decode(pdf_b64)

    def convert(self, pptx_path, output_pdf):
        pdf_data = asyncio.run(self._convert(pptx_path))
        with open(output_pdf, "wb") as f:
            f.write(pdf_data)
        print(f"✅ PDF guardado en {output_pdf}")

if __name__ == "__main__":
    converter = PPTXtoPDFConverter(headless=True)
    converter.convert("./presentacion.pptx", "resultado.pdf")
