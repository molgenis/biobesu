#!/user/bin/env python3

from setuptools import setup, find_namespace_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="biobesu",
    keywords=['benchmark', 'bioinformatics'],
    packages=find_namespace_packages(),
    version="0.1.0-SNAPSHOT",
    license='GNU Lesser General Public License v3 (LGPLv3)',
    author="MOLGENIS development team",
    author_email="molgenis@gmail.com",
    description="Bioinformatics Benchmark Suite",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/molgenis/biobesu",
    # download_url = '',
    python_requires='>=3.3',
    install_requires=[
        'requests'
    ],
    extras_require={
        'test': [
            'pytest',
        ]
    },
    entry_points={
        'console_scripts': [
            'biobesu = biobesu.cli:main'
        ],
        'biobesu_suites': [
            'hpo_generank = biobesu.suite.hpo_generank.cli:main'
        ],
        'biobesu_hpo_generank': [
            'lirical = biobesu.suite.hpo_generank.runner.lirical:main'
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)"
    ]
)