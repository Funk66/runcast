from setuptools import setup

setup(
    name="runcast",
    version="0.1.0",
    author="Guillermo Guirao Aguilar",
    author_email="contact@guillermoguiraoaguilar.com",
    description="Podcast downloader",
    url="https://github.com/Funk66/runcast",
    license="MIT",
    classifiers=["Programming Language :: Python :: 3.9"],
    install_requires=["dateutils", "feedparser", "requests"],
    py_modules=["runcast"],
    entry_points={"console_scripts": ["runcast=runcast:run"]},
)
