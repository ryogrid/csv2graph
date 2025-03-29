from setuptools import setup, find_packages

setup(
    name="csv2graph",
    version="0.1.0",
    description="Generate scatter plots from CSV files",
    author="Your Name",
    packages=find_packages(),
    py_modules=["csv2graph"],
    install_requires=[
        "pandas",
        "Pillow",
    ],
    entry_points={
        'console_scripts': [
            'csv2graph=csv2graph:main',
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: Public Domain",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)