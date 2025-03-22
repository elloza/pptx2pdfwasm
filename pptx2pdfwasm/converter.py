import asyncio
import base64
import threading
import socket
import zipfile
from pathlib import Path
from http.server import SimpleHTTPRequestHandler
from socketserver import TCPServer

class CustomHTTPRequestHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cross-Origin-Opener-Policy", "same-origin")
        self.send_header("Cross-Origin-Embedder-Policy", "require-corp")
        super().end_headers()
    
    def log_message(self, format, *args):
        if self.server.log_enabled:
            super().log_message(format, *args)
        # else: suprime el log

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
            raise OSError(f"❌ ERROR: El puerto {self.port} ya está en uso. Cierra el proceso que lo está usando e inténtalo de nuevo.")

        handler = lambda *args, **kwargs: CustomHTTPRequestHandler(*args, directory=str(self.root_path), **kwargs)
        self.server = StoppableTCPServer(("localhost", self.port), handler)
        self.server.log_enabled = self.log_enabled  # Propagar configuración de logs al servidor
        self.server_thread = None

    def start_server(self):
        if self.server_thread is None:
            self.server_thread = threading.Thread(target=self.server.serve_forever, daemon=True)
            self.server_thread.start()
            self._log(f"🚀 Servidor HTTP iniciado en http://localhost:{self.port}/")
        else:
            self._log("⚠️ ADVERTENCIA: El servidor ya está en ejecución.")

    def stop_server(self):
        if self.server_thread is not None:
            self.server.shutdown_server()
            self.server_thread = None
            self._log("🛑 Servidor HTTP detenido correctamente.")
        else:
            self._log("⚠️ ADVERTENCIA: El servidor no está en ejecución.")

    def _log(self, message):
        if self.log_enabled:
            print(message)

    def _ensure_static_files(self):
        """Descomprime `static/static.zip` si existe y elimina el ZIP después."""
        if self.static_zip.exists():
            self._log(f"📦 Se encontró `{self.static_zip.name}`, descomprimiendo archivos en `{self.root_path}`...")
            with zipfile.ZipFile(self.static_zip, "r") as zip_ref:
                zip_ref.extractall(self.root_path)
            #self.static_zip.unlink()
            self._log("✅ Archivos descomprimidos correctamente.")

        if not self.root_path.exists() or not any(self.root_path.iterdir()):
            raise FileNotFoundError(f"❌ ERROR: No se encontraron archivos estáticos en `{self.root_path}`.")

    def _is_port_in_use(self, port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(("localhost", port)) == 0

    async def _convert(self, pptx_path):
        try:
            from playwright.async_api import async_playwright
            
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=self.headless)
                page = await browser.new_page()
                logs = []

                def log_message(msg):
                    text = msg.text
                    logs.append(text)
                    self._log(f"LOG: {text}")

                if self.log_enabled:
                    page.on("console", log_message)

                with open(pptx_path, "rb") as f:
                    pptx_b64 = base64.b64encode(f.read()).decode()

                self._log("⏳ Cargando página de conversión...")
                await page.goto(f"http://localhost:{self.port}/index.html")

                self._log("⏳ Esperando que soffice.js se cargue...")
                await page.wait_for_function("window.sofficeLoaded === true", timeout=120000)

                self._log("🚀 Enviando archivo para conversión...")
                pdf_b64 = await page.evaluate(f'convertPPTX("{pptx_b64}")')

                if pdf_b64 is None:
                    self._log("❌ ERROR: `convertPPTX` retornó `null`. Guardando logs y HTML de depuración.")

                    with open("browser_logs.txt", "w", encoding="utf-8") as f:
                        f.write("\n".join(logs))

                    page_content = await page.content()
                    with open("debug_page.html", "w", encoding="utf-8") as f:
                        f.write(page_content)

                    raise ValueError("❌ ERROR: JavaScript no generó un PDF válido. Revisa 'browser_logs.txt' y 'debug_page.html'.")

                pdf_bytes = base64.b64decode(pdf_b64)

                if len(pdf_bytes) < 100:
                    self._log("⚠️ ADVERTENCIA: PDF generado es demasiado pequeño, la conversión pudo haber fallado.")
                    raise ValueError("❌ ERROR: El archivo PDF generado es sospechosamente pequeño.")

                self._log("✅ Conversión finalizada con éxito. Cerrando navegador...")
                await browser.close()
                return pdf_bytes

        except Exception as e:
            self._log(f"❌ ERROR: Ocurrió un problema durante la conversión: {e}")
            self.stop_server()
            return None

    def convert(self, pptx_path, output_pdf):
        try:
            pdf_data = asyncio.run(self._convert(pptx_path))
            if pdf_data:
                with open(output_pdf, "wb") as f:
                    f.write(pdf_data)
                self._log(f"✅ PDF guardado en {output_pdf}")
            else:
                self._log("❌ ERROR: La conversión falló. No se generó el PDF.")
        except Exception as e:
            self._log(f"❌ ERROR GENERAL: {e}")
            self.stop_server()

def main():
    import argparse
    parser = argparse.ArgumentParser(
        description="Convert PPTX to PDF using a headless browser. Use --verbose to enable logging."
    )
    parser.add_argument("input", help="Input PPTX file")
    parser.add_argument("output", help="Output PDF file")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging", default=True)
    parser.add_argument("--port", type=int, default=8000, help="Port for the HTTP server (default: 8000)")
    parser.add_argument("--headless", action="store_true", help="Run the browser in headless mode", default=True)
    # TODO: add multiple input files in a folder and output to a folder
    
    args = parser.parse_args()

    converter = PPTXtoPDFConverter(headless=args.headless, log_enabled=args.verbose, port=args.port)
    converter.start_server()
    converter.convert(args.input, args.output)
    converter.stop_server()

if __name__ == "__main__":
    main()
