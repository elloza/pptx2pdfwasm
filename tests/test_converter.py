import os
import pytest
from pptx2pdfwasm import PPTXtoPDFConverter

@pytest.fixture
def converter():
    return PPTXtoPDFConverter(headless=True)

def test_conversion(converter):
    input_file = "tests/test.pptx"
    output_file = "tests/test.pdf"

    # Crear un PPTX de prueba vacío
    with open(input_file, "wb") as f:
        f.write(b"Dummy PPTX content")

    converter.convert(input_file, output_file)

    # Verificar que el PDF se generó
    assert os.path.exists(output_file)

    # Limpiar archivos de prueba
    os.remove(input_file)
    os.remove(output_file)