from setuptools import setup, find_packages

setup(
    name="lamcp",
    version="0.0.1",
    packages=find_packages(),
    install_requires=[
        "requests",
        "cromulent>=1.0.1",
        "ujson",
        "dateutils",
        "edtf",
        "dateparser",
        "shapely",
        "lxml",
        "numpy",
        "bs4",
        "pyluach",
    ],
)
