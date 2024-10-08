from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="mgpustat",
    version="0.1.0",
    author="Rathul Anand",
    author_email="notifyrathul@gmail.com",
    description="A GPU statistics utility for Apple Silicon Macs.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/rathull/mgpustat",
    packages=find_packages(),
    install_requires=[
        "rich",
    ],
    extras_require={
        "dev": ["pytest", "pre-commit"],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: MacOS :: MacOS X",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    python_requires=">=3.7",
    entry_points={
        "console_scripts": [
            "mgpustat=mgpustat.main:main",
        ],
    },
)
