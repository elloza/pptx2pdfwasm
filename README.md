# 📄 pptx2pdfwasm

This a Python library to convert a pptx file to pdf using the Libre Office wasm version. 🚀

In fact, you can convert a docx, xlsx, or pptx file to pdf using the Libre Office wasm version.🚀

💡 **Initial crazy idea**: Use Libre Office wasm version for creating a pptx2pdf library in Python compatible with several desktop platforms (Linux, MacOS, Windows).

This could be overkill, but it is a fun project to work on. 🎉

## 🛠️ The problem

It turns out that converting a pptx file to pdf is not that easy on Python. There are several libraries that can do that, but they are not cross-platform. For example, `python-pptx` is a great library, but it only works on Windows. `unoconv` is another great library, but it requires Libre Office to be installed on the system.

In my humble opinion, the straightforward way to solve this problem is to use Libre Office, but it requires that the final user has Libre Office installed on their system, the binary `soffice` must be in the PATH, and the user must have the correct permissions to run the binary... this is not a good solution for a library. 😕

## 💡 The solution

The crazy idea and also a PoC is to use the Libre Office wasm version to convert the pptx file to pdf. This way, we can create a library that works on several platforms without the need for the user to install anything. 🚀

The idea is to create a Python library that uses the Libre Office wasm version to convert the pptx file to pdf. The library will be a wrapper around the Libre Office wasm version, and it will be compatible with several platforms (Linux, MacOS, Windows). 🌍

## 📚 The resources

1. **The office WASM version**: The most interesting resource is the Libre Office wasm version. Particularly, the version from [ZetaOffice](https://github.com/allotropia/zetajs). This version is a fork of the Libre Office wasm version, and it is more up-to-date than the original version. The Libre Office wasm version is a full version of Libre Office compiled to WebAssembly. It is a full version of Libre Office, so it can do everything that the desktop version can do. The Libre Office wasm version is a great resource because it is a full version of Libre Office that can run on the browser. This means that we can use it to convert the pptx file to pdf without the need for the user to install anything. 🌐

2. **Python libraries**: The main idea is to serve a website and browse it with libraries like Playwright or Selenium. All the conversion will be done on the browser and controlled from Python. This is no different from using a headless browser to convert a webpage to pdf. It is overkill, but it's working. 🖥️

## 🔧 The workarounds

To avoid the limitation of git of 100MB, the files of the web are compressed in a zip file. The zip file is extracted in the first run of the library. The zip file is stored in the package, so it is not necessary to download it again. It's not the best solution, but it's working. 📦

## 🚀 Status

**Status**: Finally, it's working! 🎉

**Prerequisites**:

Install Playwright:

```bash
pip install playwright
playwright install
```

For installing the package:

```bash
pip install git+https://github.com/elloza/pptx2pdfwasm
```

# How to use it 📚

```python
from pptx2pdfwasm import PPTXtoPDFConverter
converter = PPTXtoPDFConverter(headless=True, log_enabled=True, port=8000)
converter.start_server()
converter.convert("example.pptx", "example.pdf")
# More conversions with the server running
converter.stop_server()
```

Command line:

```bash
python -m pptx2pdfwasm example.pptx example.pdf
```

# TODO 📝

- [X] Test on Windows 🪟
- [ ] Test on MacOS 🍏
- [ ] Conversion for complete folders 📁


# Known issues and limitation 🐞

* The conversion of pptx could change the tables, the text, or the images. The best way to deal with this is to open previously your file with Libre Office and check if everything is ok.

# License 📜 and distribution

* The main issue is the distribution of wasm files from this package. All the rights are reserved to the ZetaOffice team. The files are compressed in a zip file and stored in the package. The zip file is extracted in the first run of the library. The zip file is stored in the package, so it is not necessary to download it again. It's not the best solution, but it's working. 📦

If this approach broke any license, please let me know and I will delete it 📧

It's done in this way for convenience and to avoid the limitation of git of 100MB and pypi of 100MB. 📦

# Acknowledgments

Thank you to the [ZetaOffice](https://github.com/allotropia/zetajs) team for the Libre Office wasm version. 🙏

And their great work on the Libre Office wasm version and supporting the community. 🌟
Check this [link](https://github.com/allotropia/zetajs/issues/11)