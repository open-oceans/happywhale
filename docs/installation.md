# General Installation

This assumes that you have native python & pip installed in your system, you can test this by going to the terminal (or windows command prompt) and trying

```python``` and then ```pip list```

**happywhale only support Python v3.7 or higher**

To install **happywhale: Simple CLI for HappyWhale.com API** you can install using two methods.

```pip install happywhale```

or you can also try

```
git clone https://github.com/open-oceans/happywhale.git
cd happywhale
python setup.py install
```
For Linux use sudo or try ```pip install happywhale --user```.

I recommend installation within a virtual environment. Find more information on [creating virtual environments here](https://docs.python.org/3/library/venv.html).

## Getting started

As usual, to print help:

```
happywhale -h
usage: happywhale [-h] {readme,auth,species,stats,fetch,search,download} ...

Simple CLI for HappyWhale.com

positional arguments:
  {readme,auth,species,stats,fetch,search,download}
    readme              Go to the web based happywhale cli readme page
    auth                Saves your username and password
    species             Get species list
    stats               Go site stats for happywhale
    fetch               Fetch details on an encounter based on encounter id
    search              Search and export results (Default: Global 1 month)
    download            Download images from search results (Default: Global 1 month)

options:
  -h, --help            show this help message and exit
```

To obtain help for specific functionality, simply call it with _help_ switch, e.g.: `happywhale species -h`. If you didn't install happywhale, then you can run it just by going to *happywhale* directory and running `python happywhale.py [arguments go here]`
