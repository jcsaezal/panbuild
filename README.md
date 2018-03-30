# Panbuild

Panbuild is a _make-like_ builder for [pandoc][pandoc]. It is a command-line tool that aims to simplify the construction of multiple output files (in different formats) from a given input (source) document. 


Panbuild relies on YAML code (e.g., included in a separate _build_ file) to specify the various options that must be passed to [pandoc][pandoc] for the different output formats. This removes the need for repeatedly typing possibly long and complex pandoc commands for each and every target output format. At the same time, this tool greatly simplifies the integration of Pandoc with extensible text editors, such as Sublime Text, and, more importantly, it prevents the user from interacting with pandoc directly via the command line.

[pandoc]: http://pandoc.org/

## Installation

Installing the latest version of `panbuild` requires [Python], a programming language that comes pre-installed on Linux and Mac OS X, and which can be easily installed on [Windows]. Panbuild works with both Python v2.7 and v3.x.

You can install `panbuild` by using the following command as root:

     pip install git+https://github.com/jcsaezal/panbuild

To upgrade to the most recent release, proceed as follows:

    pip install --upgrade --force git+https://github.com/jcsaezal/panbuild

`pip` is a program that downloads and installs modules from the Python Package Index ([PyPI]) or from a specified URL. On Mac OS X, it typically comes installed with your Python distribution. On Windows, make sure you choose to install `pip` during the installation of Python (latest Python installers provide such an option). On a Debian-based system (including Ubuntu), you can install `pip` (as root) as follows:

    apt-get install python-pip

[Python]: https://www.python.org/
[Windows]: https://www.python.org/downloads/windows/
[PyPI]: https://pypi.python.org/pypi

## Usage

TODO

## Documentation

TODO


## Support

TODO
