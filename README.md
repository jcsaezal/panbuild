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
    

## Getting started

To understand the motivation behind Panbuild, let us consider an illustrative example. Suppose that we want to create a report consisting of three chapters that we want to distribute through a website in various formats. To write that report, we use the Markdown language, which makes it possible to maintain a simple source code for our document, and which can we easily transform into multiple final document formats thanks to [Pandoc][pandoc]. In preparing the source Markdown document of our report we want it to have the following features:

* We want to write each chapter of our report in a separate Markdown file, so to make maintenance more manageable. Hence, in building the final document (e.g., PDF) with Pandoc, we will indicate the name of each input file in the command-line (in the order in which the corresponding chapter appears in the report).
* We expect chapters, sections and subsections to be given a number automatically and in a hierarchic way (e.g., _Chapter 1_, _Section 1.2_, etc.). To make this happen we will invoke Pandoc with the `-N` option.
* Our report will contain figures and tables that we want to refer to from the document text. So we want both figures and tables to be automatically numbered and to have a certain ID so that we can to refer to them in the text. Because Pandoc's Markdown does not yet feature specific support for figure/table referencing, we will turn to the [`pandoc-crossref`][pandoc_crossref] Pandoc filter. So, in invoking Pandoc we will pass the following option `--filter=pandoc-crossref`.
* Finally, we want to distribute the document in three formats: PDF -optimized for printing-, HTML -served directly at our site- and EPUB -for a better reading experience from a mobile handheld device, such as a tablet-. Moreover, we will tell Pandoc to use a specific CSS stylesheet for the HTML version, and will assign a cover to the EPUB version.   

Provided that the Markdown source for the various chapters is found in the `chapter1.md`,`chapter2.md` and `chapter3.md` files, the Pandoc commands below will generate the PDF, HTML and EPUB versions of the report:

```bash
# For PDF
$ pandoc chapter1.md chapter2.md chapter3.md -o report.pdf -N --filter=pandoc-crossref 

# For HTML
$ pandoc chapter1.md chapter2.md chapter3.md -o report.html -N --filter=pandoc-crossref -t html -s --css=cool.css

# For EPUB
$ pandoc chapter1.md chapter2.md chapter3.md -o report.epub -N --filter=pandoc-crossref -t epub --epub-cover-image=cover.png
```   


## Usage

To obtain information about the various command-line options supported by `panbuild`, just type the following command:

```bash
$ panbuild -h
usage: panbuild [-h] [-f BUILD_FILE] [-L] [-o] [-v] [-d PANDOC_DIR]
                [-S PANDOC_OPTIONS] [-y]
                [TARGETS [TARGETS ...]]

Panbuild, a YAML-based builder for Pandoc

positional arguments:
  TARGETS               a target name (must be defined in the build file)

optional arguments:
  -h, --help            show this help message and exit
  -f BUILD_FILE, --build-file BUILD_FILE
                        Indicates which file contains the build rules. If
                        omitted, panbuild searches for rules in "build.yaml"
  -L, --list-targets    List targets found in build file
  -o, --list-output     List the name of the output file for each target
  -v, --verbose         Enable verbose mode
  -d PANDOC_DIR, --pandoc-dir PANDOC_DIR
                        Used to point to pandoc executable's directory, in the
                        event it is not in the PATH
  -S PANDOC_OPTIONS, --sample-build-file PANDOC_OPTIONS
                        Print a sample build file for the pandoc options
                        passed as a parameter. Format PANDOC_OPTIONS ::=
                        '[list-input-files] REST_OF_OPTIONS'
  -y, --use-yaml-options
                        Show options in YAML format when generating sample
                        build file
```


## Support

TODO



[Python]: https://www.python.org/
[Windows]: https://www.python.org/downloads/windows/
[PyPI]: https://pypi.python.org/pypi
[pandoc]: http://pandoc.org/
[pandoc_crossref]: https://github.com/lierdakil/pandoc-crossref 
