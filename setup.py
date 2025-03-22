from setuptools import setup, find_packages

setup(
    name="pptx2pdfwasm",
    version="0.1.0",
    author="elloza",
    author_email="loza@usal.es",
    description="Convert PPTX to PDF using LibreOffice WASM and Playwright. Probably the most inefficient way to convert a PPTX to PDF.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/elloza/pptx2pdfwasm",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "pptx2pdfwasm": ["static/*"]
    },
    install_requires=[
        "playwright"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    entry_points={
        "console_scripts": [
            "pptx2pdf=pptx2pdfwasm.converter:main"
        ]
    }
)
