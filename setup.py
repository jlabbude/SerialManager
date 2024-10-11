from setuptools import setup, find_packages

with open("README.md", "r") as f:
    description = f.read()

setup(
    name="SerialManager",
    version="1.9.5.1",
    description="Abeeway configuration tool",
    author="João Lucas",
    url="https://github.com/jlabbude/SerialManager",
    packages=find_packages(where="src"),
    package_dir={"SerialManager": "src/SerialManager"},
    install_requires=[
        "pyserial",
        "tk",
        "requests",
        "typing_extensions",
        "kapak",
        "pyyaml",
        "fuzzyfinder"
    ],
    entry_points={
        "console_scripts": [
            "serialmgr = SerialManager.serialmgr:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3",
    ],
    python_requires='>=3.0',
    long_description=description,
    long_description_content_type="text/markdown",
    include_package_data=True,
    package_data={
        '': ['*.yaml'],
    },
)
