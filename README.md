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

In future releases we plan to provide a binary version of `panbuild` for Windows (EXE file) to remove dependencies from Python and `pip`. The installation of such a binary version would be then as simple as placing the executable file in any directory included in the PATH (e.g. the directory where the `pandoc.exe` file was installed on your system).  
    
## Usage

When running the `panbuild` command without arguments it will try to open a _build.yaml_ file located on the current working directory. If the _build file_ was not found, an error message will be displayed:

```
$ panbuild
[Errno 2] No such file or directory: 'build.yaml'
```

Otherwise, Panbuild will retrieve the _targets_ found in the build file (one for each target document we want to generate) as well as the pandoc commands required to build those targets. Once this is done it will invoke these commands sequentially, as in the following example, where three targets were found in the build file:

```
$ panbuild 
Building target PDF ...Success
Building target HTML ...Success
Building target EPUB ...Success
```

In the next section of this article, information is provided on how to create a _build.yaml_ file. To tell Panbuild to use another build file different from the default one (_build.yaml_), the '-f' option must be specified, which accepts an argument with the actual name of the actual build file to use.

We can also ask Panbuild to build specific targets found on the build file, rather than all of them. We can do that by passing the name of each target in the command line as program arguments separated by a space. For example, to build the "PDF" target only, we should invoke the program as follows:

```
$ panbuild PDF
Building target PDF ...Success
```

Note also that Panbuild recognizes an implicit target `clean` (not defined in the build file) which will delete the files associated with each target:

```
$ panbuild clean
Removing file out.pdf
Removing file out.html
Removing file out.epub
```

Another interesting option of the Panbuild program is `-L`, which allows us to obtain a list of the targets found in the build file:

```
$ panbuild -L
PDF
HTML
EPUB
```

To obtain more information about the various command-line options supported by `panbuild`, just use the `-h` switch:

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


## Documentation

To understand the motivation behind Panbuild, let us consider an illustrative example. Suppose that we want to create a report consisting of three chapters that we will distribute through a website in various formats. To write that report, we use the Markdown language, which makes it possible to maintain a simple source code for our document, and which can be easily transformed into multiple document formats -such as PDF or HTML- thanks to [Pandoc][pandoc]. Suppose further that the Markdown source code our report has the following features:

* The contents of each chapter in the report is found in a separate Markdown file, thus making maintenance more manageable. Therefore, in building the final document (e.g., PDF) with Pandoc, we must indicate the name of each input file in the command line, in the same order in which the corresponding chapter appears in the report.
* We expect chapters, sections and subsections to be given a number automatically (e.g., _Chapter 1_, _Section 1.2_, etc.). To make this happen we will invoke Pandoc with the `-N` option.
* Our report will contain figures and tables that we want to refer to from the document text. So we want both figures and tables to be automatically numbered and to have a certain ID so that we can to refer to them in the text. Because Pandoc's Markdown does not yet feature specific support for figure/table referencing, we will turn to the [`pandoc-crossref`][pandoc_crossref] Pandoc filter. So, in invoking Pandoc we will pass the following option `--filter=pandoc-crossref`.
* Finally, we want to distribute the document in three formats: PDF -optimized for printing-, HTML -served directly by our site as a standalone page- and EPUB -for a better reading experience on mobile handheld devices-. Moreover, we will tell Pandoc to use a specific CSS stylesheet for the HTML version, and to include a cover image in the EPUB version.   

Provided that the Markdown source for the various chapters is found in the `chapter1.md`,`chapter2.md` and `chapter3.md` files, the Pandoc commands below will generate the PDF, HTML and EPUB versions of the report:

```bash
# For PDF
$ pandoc chapter1.md chapter2.md chapter3.md -o report.pdf -N --filter=pandoc-crossref 

# For HTML
$ pandoc chapter1.md chapter2.md chapter3.md -o report.html -N --filter=pandoc-crossref -t html -s --css=cool.css

# For EPUB
$ pandoc chapter1.md chapter2.md chapter3.md -o report.epub -N --filter=pandoc-crossref -t epub --epub-cover-image=cover.png
```   

To avoid typing these somewhat long commands over and over again to see what a particular final document looks like, we could turn to the [GNU Make tool][make]. A very nice feature of [GNU Make][make] is that it enables the user to define various _targets_, which, in the context of Pandoc, could be used to represent the various final documents we may want to generate from our source document (e.g., Markdown). Unfortunately, getting familiar with the syntax of build files in this tool (called _Makefiles_) takes some time, especially for users that do not typically rely on command-line tools. 

To overcome this issue while still offerring the _target_ abstraction to the user, Panbuild relies on the YAML language to define build files. Notably, many Pandoc users are already familiar with this language, since it allows them to define [Pandoc variables](https://pandoc.org/MANUAL.html#variables-set-by-pandoc) in our document sources via [YAML metadata blocks](https://pandoc.org/MANUAL.html#yaml_metadata_block). This fact coupled with the simplicity of the [syntax of the language](http://docs.ansible.com/ansible/latest/reference_appendices/YAMLSyntax.html), makes YAML a suitable choice for the definition of build files.

Now, Let us go back to our example to describe the syntax of Panbuild's build files. The following sample YAML file defines the necessary targets to build the various final documents that we want to generate from our Markdown code:

```yaml
pandoc_common:
  filters:
  - pandoc-crossref
  input_files:
  - chapter1.md
  - chapter2.md
  - chapter3.md
  - chapter4.md
pandoc_targets:
  EPUB:
    options: -N --filter=pandoc-crossref -t epub --epub-cover-image=cover.png
```


## Support

TODO



[Python]: https://www.python.org/
[Windows]: https://www.python.org/downloads/windows/
[PyPI]: https://pypi.python.org/pypi
[pandoc]: http://pandoc.org/
[pandoc_crossref]: https://github.com/lierdakil/pandoc-crossref 
[make]: https://www.gnu.org/software/make/
