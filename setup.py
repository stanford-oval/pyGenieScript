from setuptools import setup, find_packages
from distutils.command.build import build
import subprocess


subprocess.run(["npm", "install", "genie-toolkit"])
subprocess.run(["npm", "link", "genie-toolkit"])

        
setup(
    name='pyGenieScript',
    author="Stanford University Open Virtual Assistant Lab",
    version='0.0.0-a0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        # List your Python dependencies here
    ],
)