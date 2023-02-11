from setuptools import setup, find_packages
from setuptools.command.install import install as _install
from setuptools.command.sdist import sdist as _sdist
     
setup(
    name='pyGenieScript',
    author="Stanford University Open Virtual Assistant Lab",
    version='0.0.0-a0',
    packages=find_packages(),
    package_data={'pyGenieScript': ['package.json']},
    include_package_data=True,
    install_requires=[
        # List your Python dependencies here
    ],
)