import os
import pytest
from pptx2pdfwasm import PPTXtoPDFConverter

@pytest.fixture
def converter():
    return PPTXtoPDFConverter(headless=True, log_enabled=True, port=8000)

def test_conversion(converter):
    # Get folder of this test
    current_folder = os.path.dirname(os.path.abspath(__file__))
    input_file = os.path.join(current_folder, "test.pptx")
    output_file = os.path.join(current_folder, "test.pdf")
    # Start the server, convert the file and stop the server
    converter.start_server()
    converter.convert(input_file, output_file)
    converter.stop_server()
    # Check if the output file was created
    assert os.path.exists(output_file)
    # Check if the output file is not empty
    assert os.path.getsize(output_file) > 0
    # Clean up
    os.remove(output_file)