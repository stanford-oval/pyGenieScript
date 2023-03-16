# Installation of genienlp on Apple Silicone machines

The main modification needed to run `pyGenieScript` on Apple Silicon is related to the various python libraries used by genienlp.
The author of this page hasn't scucessfully installed genienlp natively.
(so if anyone discovered a method, definitely let us know!
The problem is not inside genienlp itself but is due to the various libraries used by it and its dependencies, e.g. `bootleg`).
Instead, we recommend using rosetta for now.

1. Credit to [here](https://stackoverflow.com/a/64883440), run `arch -x86_64 /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install.sh)"`, followed by `arch -x86_64 brew install python@3.7`. Then, export its path as prompted by brew: the command should be something like `export PATH="/Users/${whoami}/Library/Python/3.7/bin:$PATH"`.

2. Install genienlp as usual by running `pip3.7 install genienlp==0.7.0a4`;

3. Verify you can execute the binary by running `genienlp train`. You should be able to see a print out of arguments information.

## FAQs

- Where is the ARM brew? Is it still going to be around?

> Yes. After doing step 1, you should have two brews installed (unless you never installed brew). The ARM brew can typically be found at `/opt/homebrew/bin/brew` while the intel brew can be found at `/usr/local/bin/brew`. You can still prioritize the ARM brew for ordinary tasks and only use the intel brew for this installation.

- I have successfully installed `genienlp` but see `ImportError: cannot import name 'NonNegativeFloat' from 'pydantic'` when running `genienlp`. 

> This is due to an issue with `pydantic` version. You can run `pip3.7 install pydantic==1.8.2` to solve this problem.
