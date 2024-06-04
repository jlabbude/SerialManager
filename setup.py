from setuptools import setup, find_packages

with open("README.md", "r") as f:
    description = f.read()

setup(
    name="SerialCFG",
    version="1.1.0",
    description="Abeeway configuration tool",
    author="João Lucas",
    url="https://github.com/jlabbude/SerialCFG",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "pyserial",
        "tk",
        "requests",
        "typing_extensions",
    ],
    entry_points={
        "console_scripts": [
            "abeewayconfig = SerialCFG.serialcfg:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3",
    ],
    python_requires='>=3.0',
    long_description=description,
    long_description_content_type="text/markdown",
)
