from setuptools import setup, find_packages

setup(
    name='cvts',
    description='Tools for working with commercial vehicles GPS traces in Vietnam',
    author='Simon Knapp',
    author_email='simon.knapp@csiro.au',
    version='0.0.2',
    python_requires='>=3',
    packages=find_packages(),
    scripts=[
        'bin/csv2json',
        'bin/json2geojson',
        'bin/regioncounts',
        'bin/speed'],
    install_requires=[
        'dataclasses',
        'luigi',
        'nptyping',
        'numpy',
        'pandas',
        'pyshp',
        'scipy',
        'shapely',
        'tqdm'],
    extras_require={
        "dev": [
            "sphinx",
            "sphinx-autodoc-typehints"]}
)
