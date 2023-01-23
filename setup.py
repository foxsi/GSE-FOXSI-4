import setuptools

setuptools.setup(
    name="FOGSE",
    version="0.0.1",
    description="ground station software for FOXSI-4",
    url="https://github.com/foxsi/GSE-FOXSI-4",
    install_requires=[
            "numpy", 
            "PyQt6", 
            "pyqtgraph"
        ],
    packages=setuptools.find_packages(),
    zip_safe=False
)