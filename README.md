# Packaged GenieScript for Python

GenieScript's core engine is originally built in Java/TypeScript. This is its language extension in Python.
The goal of this package is to:

- Provide an easy installation, almost directly from `pip`
  
- Expose the GenieScript engine as a set of easy-to-use APIs, enabling it to be used in larger Python projects

# Installation

1. Install [node](https://nodejs.org/en/download/) in your current environment.
   
    - GenieScript recommends `node >= 18`, although it is yet to be tested on earlier nodes. If you have multiple nodes in your environment, we recommend using [nvm](https://github.com/nvm-sh/nvm). After installing it, run (1) `nvm install 18`, (2) `nvm use 18`, and finally (3) `nvm alias default 18`.

2. Install some required system dependency of `pyGenieScript`, including:

    - install [gettext](https://www.gnu.org/software/gettext/). Install by [brew on Mac](https://formulae.brew.sh/formula/gettext) and by other package managers on linux.

3. `pip install pyGenieScript`

4. `pip install genienlp==0.7.0a4` (because installation of `genienlp` depends on more libraries, it is not included as a mandatory dependency of `pyGenieScript`). **For Mac M1/M2 users, refer to this [installation guide](https://github.com/stanford-oval/pyGenieScript/blob/master/genienlp-apple-silicone.md).**

# Usage

## A minimalist example to run the yelp semantic parser

You can use GenieScript to query yelp database in natural language. We have prepared a yelp parser. Here are the steps to run this example:

1. Open a `python` REPL process. Do the following:

```python
>>> import pyGenieScript.geniescript
>>> genie = pyGenieScript.geniescript.Genie() # This command installs genie-toolkit and might take a while for the first time
>>> genie.nlu_server('yelp') # This command will download the yelp parser and might take a while for the first time
```

*Tip: If you see `Prediction worker had an error: spawn genienlp ENOENT`, this means `genienlp` is not installed correctly.*

If successful, the final message you see should be similar to this:

```[I 230211 02:15:11 util:299] TransformerSeq2Seq has 139,420,416 parameters```

Keep this REPL running, and in a separate terminal, run:

2. The yelp skill requires you to [register an API online](https://fusion.yelp.com/) and obtain a developer key. Register an account, retrieve the API key, and run:

```bash
export YELP_API_KEY=[your key]
```

3. Open another `python` REPL process. Do the following:
   
```python
>>> import pyGenieScript.geniescript
>>> genie = pyGenieScript.geniescript.Genie() # You should not need to wait now
>>> genie.initialize('localhost', 'yelp') # This sets the semantic parser to be accesible over local server
>>> genie.query("show me a chinese restaurant") # You should see meaningful results returned from Genie
>>> genie.quit() # Shuts down Genie server
```

# Installation FAQ

If you encounter a stall of `genie.query()` when running for the first time (see [here](https://github.com/stanford-oval/pyGenieScript/issues/4)), please
cancel the stalled process and run again.

# API documentation

Main API documentations are aviliable [here](https://stanford-oval.github.io/pyGenieScript/pyGenieScript/geniescript.html).
