import setuptools

setuptools.setup(
    name="python-nucled",
    version="0.0.1",
    url="https://github.com/rytilahti/python-nucled",

    author="Teemu Rytilahti",
    author_email="tpr@iki.fi",

    description="Python interface for intel_nuc_led",
    long_description=open('README.md').read(),

    packages=['nucled'],

    install_requires=[],

    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
    ],
    entry_points={
        'console_scripts': [
            'nucled=nucled.cli:cli',
        ],
    },
)
