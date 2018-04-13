# Panbuild

Panbuild is a _make-like_ builder for [`pandoc`][pandoc]. It is a command-line tool that aims to simplify the construction of _multiple output documents_ (in different formats, such as PDF, DOCX, EPUB, etc.) from a given _source document_ (e.g. one or several Markdown files).

Panbuild relies on YAML code -typically included in a separate _build_ file- to specify the various options that must be passed to [`pandoc`][pandoc] for the different output formats. This removes the need for repeatedly typing possibly long and complex pandoc commands for each and every target output format. At the same time, this tool greatly simplifies the integration of Pandoc with extensible text editors, by preventing the user from typing commands in a terminal window to fully access all Pandoc features. [Panbuild's plugin for the Sublime Text editor](https://github.com/jcsaezal/SublimeText-Panbuild) constitutes a good example of such a seamless interaction with Pandoc through `panbuild`. 

## Installation

Apart from [`pandoc`][pandoc], installing the latest version of `panbuild` requires [Python], a programming language that comes pre-installed on Linux and Mac OS X, and which can be easily installed on [Windows]. Panbuild works with both Python v2.7 and v3.x.

The installation also requires `pip`, a program that downloads and installs modules from the Python Package Index ([PyPI]) or from a specified URL. On Mac OS X, it typically comes installed with your Python distribution. On Windows, make sure you choose to install `pip` during the installation of Python (latest Python installers provide such an option). On a Debian-based system (including Ubuntu), you can install `pip` (as root) as follows:

	apt-get install python-pip

There are basically two ways to install Panbuild: with and without `git`.

### Git-based installation 

This approach is straightforward and perhaps more suitable for Linux and Mac OS X, where the `git` command can be easily installed. In following this approach you can install `panbuild` by using the following command as root:

    pip install git+https://github.com/jcsaezal/panbuild

To upgrade to the most recent release, proceed as follows:

    pip install --upgrade git+https://github.com/jcsaezal/panbuild


### Installation without `git` 

If the one-command installation shown above does not work (i.e. `git` is not installed on your system) you can follow this two-step process:

1. Download a copy of the repository in [ZIP format](https://github.com/jcsaezal/SublimeText-Panbuild/archive/master.zip) and extract it in a _temporary_ folder on your computer.

2. Then install `panbuild` on your system by running `pip` as follows:

		pip install <full_path_of_your_temporary_folder>


### Note on a binary release

In future releases we plan to provide a binary version of `panbuild` for Windows (EXE file) to remove dependencies from Python and `pip`. The installation would be then as simple as placing that binary file in any directory included in the PATH (e.g. the directory where the `pandoc.exe` file was installed on your system).  
    

[Python]: https://www.python.org/
[Windows]: https://www.python.org/downloads/windows/
[PyPI]: https://pypi.python.org/pypi
[pandoc]: http://pandoc.org/

## Usage

TODO

## Documentation

TODO


## Support

TODO
