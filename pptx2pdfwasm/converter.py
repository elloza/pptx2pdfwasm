import asyncio
import base64
import threading
import socket
import sys
import zipfile
from pathlib import Path
from http.server import SimpleHTTPRequestHandler
from socketserver import TCPServer

class CustomHTTPRequestHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cross-Origin-Opener-Policy", "same-origin")
        self.send_header("Cross-Origin-Embedder-Policy", "require-corp")
        super().end_headers()

class StoppableTCPServer(TCPServer):
    allow_reuse_address = True  

    def shutdown_server(self):
        self.shutdown()
        self.server_close()
        print("🛑 Servidor HTTP detenido correctamente.")

class PPTXtoPDFConverter:
    def __init__(self, headless=True):
        self.headless = headless
        self.root_path = Path(__file__).parent / "static"
        self.static_zip = self.root_path / "static.zip"

        self._ensure_static_files()

        if self._is_port_in_use(8000):
            raise OSError("❌ ERROR: El puerto 8000 ya está en uso. Cierra el proceso que lo está usando e inténtalo de nuevo.")

        handler = lambda *args, **kwargs: CustomHTTPRequestHandler(*args, directory=str(self.root_path), **kwargs)
        self.server = StoppableTCPServer(("localhost", 8000), handler)
        self.server_thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.server_thread.start()
        print("🚀 Servidor HTTP iniciado en http://localhost:8000/")

    def _ensure_static_files(self):
        """Descomprime `static/static.zip` si existe y elimina el ZIP después."""
        if self.static_zip.exists():
            print(f"📦 Se encontró `{self.static_zip.name}`, descomprimiendo archivos en `{self.root_path}`...")
            with zipfile.ZipFile(self.static_zip, "r") as zip_ref:
                zip_ref.extractall(self.root_path)
            self.static_zip.unlink()
            print("✅ Archivos descomprimidos y `static.zip` eliminado.")

        if not self.root_path.exists() or not any(self.root_path.iterdir()):
            raise FileNotFoundError(f"❌ ERROR: No se encontraron archivos estáticos en `{self.root_path}`.")

    def _is_port_in_use(self, port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(("localhost", port)) == 0

    def stop_server(self):
        if hasattr(self, "server"):
            self.server.shutdown_server()

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
                    print(f"LOG: {text}")

                page.on("console", log_message)

                with open(pptx_path, "rb") as f:
                    pptx_b64 = base64.b64encode(f.read()).decode()

                print("⏳ Cargando página de conversión...")
                await page.goto("http://localhost:8000/index.html")

                print("⏳ Esperando que soffice.js se cargue...")
                await page.wait_for_function("window.sofficeLoaded === true", timeout=120000)

                print("🚀 Enviando archivo para conversión...")
                pdf_b64 = await page.evaluate(f'convertPPTX("{pptx_b64}")')

                if pdf_b64 is None:
                    print("❌ ERROR: `convertPPTX` retornó `null`. Guardando logs y HTML de depuración.")

                    with open("browser_logs.txt", "w", encoding="utf-8") as f:
                        f.write("\n".join(logs))

                    page_content = await page.content()
                    with open("debug_page.html", "w", encoding="utf-8") as f:
                        f.write(page_content)

                    raise ValueError("❌ ERROR: JavaScript no generó un PDF válido. Revisa 'browser_logs.txt' y 'debug_page.html'.")

                pdf_bytes = base64.b64decode(pdf_b64)

                if len(pdf_bytes) < 100:
                    print("⚠️ ADVERTENCIA: PDF generado es demasiado pequeño, la conversión pudo haber fallado.")
                    raise ValueError("❌ ERROR: El archivo PDF generado es sospechosamente pequeño.")

                print("✅ Conversión finalizada con éxito. Cerrando navegador...")
                await browser.close()
                return pdf_bytes

        except Exception as e:
            print(f"❌ ERROR: Ocurrió un problema durante la conversión: {e}")
            return None

    def convert(self, pptx_path, output_pdf):
        try:
            pdf_data = asyncio.run(self._convert(pptx_path))
            if pdf_data:
                with open(output_pdf, "wb") as f:
                    f.write(pdf_data)
                print(f"✅ PDF guardado en {output_pdf}")
            else:
                print("❌ ERROR: La conversión falló. No se generó el PDF.")
        except Exception as e:
            print(f"❌ ERROR GENERAL: {e}")
        finally:
            self.stop_server()  

def main():
    import sys
    if len(sys.argv) < 3:
        print("Uso: pptx2pdf input.pptx output.pdf")
        sys.exit(1)

    converter = PPTXtoPDFConverter(headless=True)
    converter.convert(sys.argv[1], sys.argv[2])

if __name__ == "__main__":
    main()
