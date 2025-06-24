from setuptools import setup, find_packages

setup(
    name="comicdb",
    version="0.3.0",
    packages=find_packages(),
    install_requires=[
        # Aggiungi qui le dipendenze del tuo progetto
        'pillow',
        'comicapi',
        'rarfile',
        'pikepdf',
        'python-magic',
        'ttkbootstrap',
    ],
    # Metadati aggiuntivi
    author="Nsfr750",
    author_email="nsfr750@yandex.com",
    description="Un'applicazione per la gestione e la visualizzazione di fumetti digitali",
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Nsfr750/ComicDB",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GPL3 License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
    entry_points={
        'console_scripts': [
            'comicdb=comicdb.main:main',
        ],
    },
)
