import os
from wasmer import engine as wasmer_engine, Store, Module, Instance, MemoryType, Memory
from wasmer_compiler_cranelift import Compiler
from wasmer import wasi

def convert_pptx_to_pdf(pptx_path: str, pdf_output: str):
    # Verificar que el archivo PPTX existe
    if not os.path.exists(pptx_path):
        raise FileNotFoundError(f"No se encontró el archivo: {pptx_path}")

    # Crear un motor Universal con el compilador Cranelift, habilitando hilos
    engine = wasmer_engine.Universal(Compiler)

    # Crear un almacén con el motor configurado
    store = Store(engine)

    # Cargar y compilar el módulo WASM de LibreOffice
    with open("soffice.wasm", "rb") as wasm_file:
        module = Module(store, wasm_file.read())

    # Obtener la versión de WASI compatible con el módulo
    wasi_version = wasi.get_version(module, strict=True)

    # Configurar el entorno WASI
    wasi_env = wasi.StateBuilder('soffice') \
        .argument('--headless') \
        .argument('--convert-to') \
        .argument('pdf') \
        .argument('/work/input.pptx') \
        .preopen_directory('/work') \
        .finalize()

    # Generar el objeto de importación para la instancia
    import_object = wasi_env.generate_import_object(store, wasi_version)

    # Instanciar el módulo WASM de LibreOffice
    instance = Instance(module, import_object)

    # Crear un tipo de memoria compartida
    memory_type = MemoryType(minimum=1, maximum=1, shared=True)

    # Crear una instancia de memoria compartida
    memory = Memory(store, memory_type)

    # Asignar la memoria compartida al entorno WASI
    wasi_env.memory = memory

    # Leer el archivo PPTX de entrada
    with open(pptx_path, "rb") as f:
        input_data = f.read()

    # Escribir el archivo de entrada en la memoria WASM
    memory.uint8_view()[:len(input_data)] = input_data

    # Ejecutar la función '_start' del módulo WASM
    start = instance.exports._start
    start()

    # Leer el PDF generado desde la memoria WASM
    output_data = memory.uint8_view()[:]

    # Guardar el PDF en el sistema de archivos del host
    with open(pdf_output, "wb") as f:
        f.write(output_data)

    print(f"Conversión completada: {pdf_output}")

# Ejemplo de uso
if __name__ == "__main__":
    convert_pptx_to_pdf("presentacion.pptx", "salida.pdf")