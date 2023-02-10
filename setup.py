import os, sys
try:
    from setuptools import setup, find_packages
    from setuptools.command.install import install as _install
    from setuptools.command.sdist import sdist as _sdist
except ImportError:
    from distutils.core import setup
    from distutils.command.install import install as _install
    from distutils.command.sdist import sdist as _sdist
import subprocess


current_file_directory = os.path.dirname(os.path.abspath(__file__))
pyGenieScript_directory = os.path.join(current_file_directory, "pyGenieScript")
class NpmInstallCommand(_install):
    """Custom command to install Node.js modules."""

    description = 'install Node.js modules'
    user_options = []

    def initialize_options(self):
        """Set default values for options."""
        pass

    def finalize_options(self):
        """Set final values for options."""
        pass

    def run(self):
        """Run command to install Node.js modules."""
        _install.run(self)
        subprocess.call(["[ -s '/usr/local/opt/nvm/nvm.sh' ] && \. '/usr/local/opt/nvm/nvm.sh' && nvm install 18.12"], cwd=pyGenieScript_directory, shell=True)
        subprocess.call(["[ -s '/usr/local/opt/nvm/nvm.sh' ] && \. '/usr/local/opt/nvm/nvm.sh' && nvm use 18.12 && npm install genie-toolkit"], cwd=pyGenieScript_directory, shell=True)

# command = '''export NVM_DIR="$HOME/.nvm"; \
#             [ -s "/usr/local/opt/nvm/nvm.sh" ] && \. "/usr/local/opt/nvm/nvm.sh"; \
#             [ -s "/usr/local/opt/nvm/etc/bash_completion.d/nvm" ] && \. "/usr/local/opt/nvm/etc/bash_completion.d/nvm"; \

#              nvm use 18.12; \
#              npm install genie-toolkit; \
#              npm link genie-toolkit'''
# process = subprocess.Popen(command, shell=True)
# process.communicate()
        
setup(
    name='pyGenieScript',
    author="Stanford University Open Virtual Assistant Lab",
    version='0.0.0-a0',
    packages=["pyGenieScript.geniescript"],
    include_package_data=True,
    install_requires=[
        # List your Python dependencies here
    ],
)