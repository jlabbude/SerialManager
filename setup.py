from setuptools import setup, find_packages

with open("README.md", "r") as f:
    description = f.read()

setup(
    name="AbeewayConfig",
    version="0.2.5",
    description="Abeeway configuration tool",
    author="João Lucas",
    url="https://github.com/jlabbude/AbeewayConfig",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "pyserial",
        "tk",
        "requests",
    ],
    entry_points={
        "console_scripts": [
            "abeewayconfig = AbeewayConfig.abeewayconfig:main",
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
