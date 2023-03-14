# Installation of genienlp on Apple Silicone machines

The main modification needed to run `pyGenieScript` on Apple Silicon is related to the various python libraries used by genienlp.
The author of this page hasn't scucessfully installed genienlp natively.
(so if anyone discovered a method, definitely let us know!
The problem is not inside genienlp itself but is due to the various libraries used by it and its dependencies, e.g. `bootleg`).
Instead, we recommend using rosetta for now.

1. Credit to [here](https://stackoverflow.com/a/64883440), run `arch -x86_64 /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install.sh)"`, followed by `arch -x86_64 brew install python@3.7`. Then, export its path as prompted by brew: the command should be something like `export PATH="/Users/${whoami}/Library/Python/3.7/bin:$PATH"`.

2. Install genienlp as usual by running `pip3.7 install genienlp==0.7.0a4`;
