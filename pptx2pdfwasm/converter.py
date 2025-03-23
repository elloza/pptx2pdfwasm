import asyncio
import threading
import socket
import zipfile
import shutil
import os
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

    def log_message(self, format, *args):
        if self.server.log_enabled:
            super().log_message(format, *args)

class StoppableTCPServer(TCPServer):
    allow_reuse_address = True  
    def __init__(self, server_address, RequestHandlerClass):
        super().__init__(server_address, RequestHandlerClass)
        self.log_enabled = True
    def shutdown_server(self):
        self.shutdown()
        self.server_close()

class PPTXtoPDFConverter:
    def __init__(self, headless=True, log_enabled=True, port=8000):
        self.headless = headless
        self.log_enabled = log_enabled
        self.port = port
        self.root_path = Path(__file__).parent / "static"
        self.static_zip = self.root_path / "static.zip"

        self._ensure_static_files()

        if self._is_port_in_use(self.port):
            raise OSError(f"❌ ERROR: El puerto {self.port} ya está en uso.")

        handler = lambda *args, **kwargs: CustomHTTPRequestHandler(*args, directory=str(self.root_path), **kwargs)
        self.server = StoppableTCPServer(("localhost", self.port), handler)
        self.server.log_enabled = self.log_enabled
        self.server_thread = None

    def start_server(self):
        if self.server_thread is None:
            self.server_thread = threading.Thread(target=self.server.serve_forever, daemon=True)
            self.server_thread.start()
            self._log(f"🚀 Servidor HTTP iniciado en http://localhost:{self.port}/")
        else:
            self._log("⚠️ El servidor ya está en ejecución.")

    def stop_server(self):
        if self.server_thread is not None:
            self.server.shutdown_server()
            self.server_thread = None
            self._log("🛑 Servidor HTTP detenido.")
        else:
            self._log("⚠️ El servidor no está en ejecución.")

    def _log(self, message):
        if self.log_enabled:
            print(message)

    def _ensure_static_files(self):
        if self.static_zip.exists():
            with zipfile.ZipFile(self.static_zip, "r") as zip_ref:
                zip_ref.extractall(self.root_path)
            self.static_zip.unlink()

        if not self.root_path.exists() or not any(self.root_path.iterdir()):
            raise FileNotFoundError(f"❌ ERROR: No hay archivos estáticos en `{self.root_path}`.")

    def _is_port_in_use(self, port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(("localhost", port)) == 0

    async def _convert(self, pptx_path):
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=self.headless,
                args=["--js-flags=--max_old_space_size=8192"]
            )
            page = await browser.new_page()

            if self.log_enabled:
                page.on("console", lambda msg: print("📢 [HTML]:", msg))

            await page.goto(f"http://localhost:{self.port}/index.html")
            await page.wait_for_function("window.sofficeLoaded === true", timeout=120000)

            served_pptx = self.root_path / "input.pptx"
            shutil.copy(pptx_path, served_pptx)

            pptx_url = f"http://localhost:{self.port}/input.pptx"
            self._log("🚀 Iniciando conversión desde URL local...")
            success = await page.evaluate(f'convertPPTXFromServer("{pptx_url}")')
            if not success:
                raise Exception("❌ La conversión falló en el navegador.")

            self._log("📥 Leyendo PDF generado desde el navegador...")
            pdf_b64 = await page.evaluate('''() => {
                function uint8ToBase64(uint8) {
                    let CHUNK_SIZE = 0x8000; // 32KB
                    let index = 0;
                    let length = uint8.length;
                    let result = '';
                    while (index < length) {
                        let slice = uint8.subarray(index, Math.min(index + CHUNK_SIZE, length));
                        result += String.fromCharCode.apply(null, slice);
                        index += CHUNK_SIZE;
                    }
                    return btoa(result);
                }

                const data = FS.readFile('/tmp/output.pdf');
                return uint8ToBase64(data);
            }''')

            pdf_bytes = base64.b64decode(pdf_b64)

            self._log("🧹 Eliminando PDF del navegador...")
            await page.evaluate('FS.unlink("/tmp/output.pdf")')

            await browser.close()
            served_pptx.unlink()

            return bytes(pdf_bytes)

    def convert(self, pptx_path, output_pdf):
        try:
            pdf_data = asyncio.run(self._convert(pptx_path))
            if pdf_data:
                with open(output_pdf, "wb") as f:
                    f.write(pdf_data)
                self._log(f"✅ PDF guardado en {output_pdf}")
            else:
                self._log("❌ No se generó el PDF.")
        except Exception as e:
            self._log(f"❌ ERROR GENERAL: {e}")
            self.stop_server()

def main():
    import argparse
    parser = argparse.ArgumentParser(description="PPTX a PDF")
    parser.add_argument("input", help="Archivo PPTX")
    parser.add_argument("output", help="Archivo PDF resultante")
    parser.add_argument("--verbose", action="store_true", default=True)
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--headless", action="store_true", default=True)

    args = parser.parse_args()

    converter = PPTXtoPDFConverter(headless=args.headless, log_enabled=args.verbose, port=args.port)
    converter.start_server()
    converter.convert(args.input, args.output)
    converter.stop_server()

if __name__ == "__main__":
    main()
