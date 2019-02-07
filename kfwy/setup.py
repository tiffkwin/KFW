import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="kfwy",
    version="0.0.12",
    author="Tiffany Nguyen",
    description="A data analysis toolkit for the KFW lab (Windows)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tiffkwin/KFW",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 2.7",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: Microsoft :: Windows",
    ],
)
