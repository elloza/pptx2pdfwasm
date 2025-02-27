# pptx2pdfwasm

Crazy idea: use Libre Office wasm version for creating a pptx2pdf library in python compatible with several desktop platforms (Linux, MacOS, Windows)

This could be overkill, but it is a fun project to work on.

Status: Bad luck. Work in progress....

## The problem

It turns out that converting a pptx file to pdf is not that easy on Python. There are several libraries that can do that, but they are not cross-platform. For example, `python-pptx` is a great library, but it only works on Windows. `unoconv` is another great library, but it requires Libre Office to be installed on the system.

In my humble opinion, the straightforward way to solve this problem is to use Libre Office, but it requires that the final user has Libre Office installed on his system, the binary soffice must be in the PATH, and the user must have the correct permissions to run the binary... this is not a good solution for a library.

## The solution

The crazy idea and also a PoC is to use the Libre Office wasm version to convert the pptx file to pdf. This way, we can create a library that works on several platforms without the need for the user to install anything.

The idea is to create a python library that uses the Libre Office wasm version to convert the pptx file to pdf. The library will be a wrapper around the Libre Office wasm version, and it will be compatible with several platforms (Linux, MacOS, Windows).

## The resources

1. The office WASM version: the most interesting resource is the Libre Office wasm version. Particulary, the version from [ZetaOffice](https://github.com/allotropia/zetajs). This version is a fork of the Libre Office wasm version, and it is more up-to-date than the original version. The Libre Office wasm version is a full version of Libre Office compiled to WebAssembly. It is a full version of Libre Office, so it can do everything that the desktop version can do. The Libre Office wasm version is a great resource because it is a full version of Libre Office that can run on the browser. This means that we can use it to convert the pptx file to pdf without the need for the user to install anything.

2. Python libraries for working with WebAssembly: there are several python libraries for working with WebAssembly. The most interesting libraries are `Wasmer` and  `wasmtime-py`. These libraries allow us to run WebAssembly code from Python. This means that we can use the Libre Office wasm version from Python.
