import os
from wasmtime import Store, Module, Instance, WasiConfig

def convert_pptx_to_pdf(pptx_path: str, pdf_output: str):
    # Verificar que el archivo PPTX existe
    if not os.path.exists(pptx_path):
        raise FileNotFoundError(f"No se encontró el archivo: {pptx_path}")

    # Configurar WASI
    store = Store()
    wasi_config = WasiConfig()
    wasi_config.argv = [
        'soffice', '--headless', '--convert-to', 'pdf', '/work/input.pptx'
    ]
    wasi_config.preopen_dir('.', '/work')
    store.set_wasi(wasi_config)

    # Cargar y compilar el módulo WASM de LibreOffice
    with open("libreoffice.wasm", "rb") as wasm_file:
        module = Module(store.engine, wasm_file.read())

    # Instanciar el módulo WASM
    instance = Instance(store, module, [])

    # Copiar el archivo de entrada al directorio de trabajo
    os.makedirs('./work', exist_ok=True)
    os.system(f'cp {pptx_path} ./work/input.pptx')

    # Ejecutar la conversión dentro del entorno WASM
    start = instance.exports(store)["_start"]
    start(store)

    # Mover el PDF generado al destino especificado
    os.system(f'mv ./work/input.pdf {pdf_output}')

    print(f"Conversión completada: {pdf_output}")

# Ejemplo de uso
if __name__ == "__main__":
    convert_pptx_to_pdf("presentacion.pptx", "salida.pdf")
