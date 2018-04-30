# Panbuild

Panbuild is a _make-like_ builder for [`pandoc`][pandoc]. It is a command-line tool that aims to simplify the construction of _multiple output documents_ (in different formats, such as PDF, DOCX, EPUB, etc.) from a given _source document_ (e.g. one or several Markdown files).

Panbuild relies on YAML code -typically included in a separate _build_ file- to specify the various options that must be passed to [`pandoc`][pandoc] for the different output formats. This removes the need for repeatedly typing possibly long and complex pandoc commands for each and every target output format. At the same time, this tool greatly simplifies the integration of Pandoc with extensible text editors, by preventing the user from typing commands in a terminal window to fully access all Pandoc features. [Panbuild's plugin for the Sublime Text editor](https://github.com/jcsaezal/SublimeText-Panbuild) constitutes a good example of such a seamless interaction with Pandoc through `panbuild`. 

## Installation

To use Panbuild, you must install [Pandoc][pandoc] on your system. It is also highly recommended to update your PATH to include the directory where pandoc's binaries were installed (Pandoc's installer typically takes care of that).


### Binary installation (Windows and Mac OS X only)

In the Panbuild's [download page](https://github.com/jcsaezal/panbuild/releases/latest) you can find a ZIP file containing executable files for Windows and Mac OS X. For the installation, just extract the `panbuild` executable file from the ZIP archive and place it in any directory included in the PATH (e.g. the directory where `pandoc.exe` or the `pandoc` executable was installed on your system). 

### Installation from source

Installing `panbuild` from source requires [Python], a programming language whose interpreter comes pre-installed on Linux and Mac OS X, and which can be easily installed on [Windows]. Panbuild works with both Python v2.7 and v3.x.

The installation also requires `pip`, a program that downloads and installs modules from the Python Package Index ([PyPI]) or from a specified URL. On Mac OS X, it typically comes installed with your Python distribution. On Windows, make sure you choose to install `pip` during the installation of Python (latest Python installers provide such an option). On a Debian-based system (including Ubuntu), you can install `pip` (as root) as follows:

	apt-get install python-pip

There are basically two ways to install Panbuild from source: with and without `git`.

#### Git-based installation 

This approach is straightforward and perhaps more suitable for Linux and Mac OS X, where the `git` command can be easily installed. In following this approach you can install `panbuild` by using the following command as root:

    pip install git+https://github.com/jcsaezal/panbuild

To upgrade to the most recent release, proceed as follows:

    pip install --upgrade git+https://github.com/jcsaezal/panbuild

#### Installation without `git` 

If the one-command installation shown above does not work (i.e. `git` is not installed on your system) you can follow this two-step process:

1. Download a copy of the repository in [ZIP format](https://github.com/jcsaezal/SublimeText-Panbuild/archive/master.zip) and extract it in a _temporary_ folder on your computer.

2. Then install `panbuild` on your system by running `pip` as follows:
  ```
  pip install <full_path_of_your_temporary_folder>
  ```


## Usage

The `panbuild` command must be executed from the directory that contains the source code of your document (e.g. collection of Markdown files). When running `panbuild` without arguments it will try to open a _build.yaml_ file located on the current working directory. If the _build file_ was not found, an error message will be displayed:

```
$ panbuild
[Errno 2] No such file or directory: 'build.yaml'
```

Otherwise, Panbuild will retrieve the _targets_ found in the build file (one for each target document we want to generate) as well as the pandoc commands required to build those targets. Once this is done, it will invoke these commands sequentially, as in the following example, where three targets were found in the build file:

```
$ panbuild 
Building target PDF ...Success
Building target HTML ...Success
Building target EPUB ...Success
```

Information is provided below on [how to create a _build.yaml_ file](#syntax-of-build-files). To tell Panbuild to use another build file different from the default one (_build.yaml_), the `-f` option must be specified, which accepts an argument with the name of the actual build file to use.

We can also ask Panbuild to build specific targets of the build file, rather than all of them. We can do that by passing the name of each target in the command line as program arguments separated by a space. For example, to build the "PDF" target only, we should invoke the program as follows:

```
$ panbuild PDF
Building target PDF ...Success
```

Note also that Panbuild recognizes an implicit `clean` target (not defined in the build file) which will delete the files associated with each target:

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

### Introduction 

To understand the motivation behind Panbuild, let us consider an illustrative example. Suppose that we want to create a report consisting of three chapters that we will distribute through a website in various formats. To write that report, we use the Markdown language, which makes it possible to maintain a simple source code for our document, and which can be easily transformed into multiple document formats -such as PDF or HTML- thanks to [Pandoc][pandoc]. Suppose further that the Markdown source code our report has the following features:

* The content of each chapter in the report is written in a separate Markdown file, thus making maintenance more manageable. Therefore, in building the final document (e.g., PDF) with Pandoc, we must indicate the name of each input file in the command line, in the same order in which the corresponding chapter appears in the report.
* We expect chapters, sections and subsections to be given a number automatically (e.g., _Chapter 1_, _Section 1.2_, etc.). To make this happen we will invoke Pandoc with the `-N` option.
* Our report contains figures and tables that we want to refer to from the document text. So we want both figures and tables to be automatically numbered and to have a certain ID so that we can to refer to them in the text. Because Pandoc's Markdown does not yet feature specific support for figure/table referencing, we will turn to the [`pandoc-crossref`][pandoc_crossref] Pandoc filter. As such, in invoking Pandoc we will pass the following option `--filter=pandoc-crossref`.
* Finally, we want to distribute the document in three different formats: PDF -optimized for printing-, HTML -served directly by our site as a standalone page- and EPUB -for a better reading experience on mobile devices-. Moreover, we will tell Pandoc to use a specific CSS stylesheet for the HTML version, as well as to include a cover image in the EPUB version.   

Provided that the Markdown source for the various chapters is found in the `chapter1.md`,`chapter2.md` and `chapter3.md` files, the Pandoc commands below will generate the PDF, HTML and EPUB versions of the report (we assume pandoc v1.19 here):

```bash
# For PDF
$ pandoc chapter1.md chapter2.md chapter3.md  -o report.pdf -N --filter=pandoc-crossref -M documentclass:report -t latex -s --chapters 

# For HTML
$ pandoc chapter1.md chapter2.md chapter3.md -o report.html -N --filter=pandoc-crossref -t html -s --css=cool.css

# For EPUB
$ pandoc chapter1.md chapter2.md chapter3.md -o report.epub -N --filter=pandoc-crossref -t epub --epub-cover-image=cover.png
```

To avoid typing these somewhat long commands over and over again to see what a particular final document looks like, we could turn to the [GNU Make tool][make]. A very nice feature of [GNU Make][make] is that it enables the user to define various _targets_, which, in the context of Pandoc, could be used to represent the various final documents we may want to generate from our source document (e.g., Markdown). Unfortunately, getting familiar with the syntax of build files in this tool (called _Makefiles_) takes some time, especially for users that are not used to working with command-line tools. 

To overcome this issue, while still offering the _target_ abstraction to the user, Panbuild relies on the YAML language to define build files. Notably, most Pandoc users are already familiar with this language, since it allows them to define [Pandoc variables](https://pandoc.org/MANUAL.html#variables-set-by-pandoc) in our document sources via [YAML metadata blocks](https://pandoc.org/MANUAL.html#yaml_metadata_block). This fact, coupled with the simplicity of the [language syntax](https://learn.getgrav.org/advanced/yaml), makes YAML a suitable choice for the definition of build files for Panbuild.

### Syntax of build files  

Now, let us go back to our example to describe the syntax of Panbuild's build files. The following sample YAML code contains the necessary information for Panbuild to build the various final documents from our Markdown code with Pandoc:

```yaml
pandoc_common:
  filters:
  - pandoc-crossref
  input_files:
  - chapter1.md
  - chapter2.md
  - chapter3.md
pandoc_targets:
  PDF:
    options: -N -o report.pdf -t latex -s -M documentclass:report --chapters
  HTML:
    options: -N -o report.html -t html -s --css=cool.css
  EPUB:
    options: -N -o report.epub -t epub --epub-cover-image=cover.png
```

Clearly, the file consists of various nested sections, (e.g. the `filters` section is included within `pandoc_common` in the example). The name of a nested section (which ends with ':') is preceded by a number of spaces that depends on its nesting level. Specifically, provided that top-level sections (such as `pandoc_common` and `pandoc_targets`) are said to be at level 0, the name of a level-N section has _2N_ preceding spaces. The right indentation is required in the YAML file in order for Panbuild to be able to process the build rules. Due to the flexibility of the syntax of the YAML language, several other alternative ways exist to encode the same information of this example (as long as the various properties are defined in the same level and within the right section). Users are strongly encouraged to check out [this article on the YAML syntax](https://learn.getgrav.org/advanced/yaml).

In creating a build file two mandatory (top-level) sections are provided: `pandoc_common` and `pandoc_targets`. The first section defines those features that target commands have in common; in this case it enumerates the list of Pandoc filters (just one in the example) and the various input (source) files that our document is made up of. Panbuild uses this information when generating the actual Pandoc commands for each target. The second section (`pandoc_targets`) defines the set of targets in the build file; each target has an ID associated with it. In the example, three targets are defined, with IDs `PDF`, `HTML` and `EPUB`, respectively. The ID of each target in the example matches the uppercase version of the extension of the output file specified in `options`. Because each target is typically meant to build a file in a different format, assigning IDs in this way is a good practice. Nevertheless, assigning IDs to the various targets it is totally up to the user; IDs are just arbitrary case-sensitive strings made up of alphanumeric characters, and may include hyphens and underscores too.

The mandatory `options` section associated with each target specifies the options that will be passed to the pandoc command when building the target. As is evident, the filters and the input files were omitted in `options` for any target, as these aspects were included in the `pandoc_common` section (shared among targets). 

To use the YAML code shown above with Panbuild, we may store it in a _build.yaml_ file located in the same directory as our document's sources (Markdown files in this case). In doing so, invoking `panbuild` without any arguments when in that directory will execute the commands associated with _all_ the targets defined in the file:

```
$ ls
build.yaml	chapter2.md	cool.css
chapter1.md	chapter3.md	cover.png
...
$ panbuild 
Building target PDF ...Success
Building target HTML ...Success
Building target EPUB ...Success
```

The output files generated by Panbuild as a result of running the various pandoc commands will be available in the current working directory.

```
$ ls
build.yaml	chapter2.md	cool.css	report.epub	report.pdf
chapter1.md	chapter3.md	cover.png	report.html ...
```

Note that we can easily retrieve the complete Pandoc command for each target by using the `-Lv` option:

```
$ panbuild -Lv
PDF: pandoc -s --chapters -t latex -M documentclass:report -N -F pandoc-crossref -o report.pdf chapter1.md chapter2.md chapter3.md
HTML: pandoc -s -N -t html --css=cool.css -F pandoc-crossref -o report.html chapter1.md chapter2.md chapter3.md
EPUB: pandoc --epub-cover-image=cover.png -t epub -N -F pandoc-crossref -o report.epub chapter1.md chapter2.md chapter3.md
```

The value of the `options` property for the various targets shown earlier could be shortened by leveraging two observations:

1. The `-N` option of Pandoc is used in all targets, and so it appears multiple times in the file
2. The name of the output files for each target follows the same pattern: `<basename>.<extension>`, where `basename` is "report" for _all_ targets, and `<extension>` can be automatically determined by Pandoc, based on the `-t` and `-s` options (if present).

According to these observations, we could rewrite the build file as follows:

```yaml
pandoc_common:
  filters:
  - pandoc-crossref
  input_files:
  - chapter1.md
  - chapter2.md
  - chapter3.md
  output_basename: report
  options: -N	
pandoc_targets:
  PDF:
    options: -t latex -s -M documentclass:report --chapters
  HTML:
    options: -t html -s --css=cool.css
  EPUB:
    options: -t epub --epub-cover-image=cover.png
```

Essentially, the `-N` or the `-o` switches are no longer specified as target-specific options. Instead, two new properties are specified inside `pandoc_common`:

1. `output_basename` indicates the base name of the output file (the extension will be added automatically).
2. `options` specifies the set of options that will be applied for _all_ targets.   


The sample build file analyzed in this section exemplifies what would be used in a somewhat complex build scenario, thus allowing us to describe many aspects of the syntax of Panbuild's build files. However, other build properties may be also present inside a target's section, such as these:

* `preamble`: list of input files that will appear first in the command line, right before those listed in the `input_files` property. Essentially, this allows the user to add specific preambles (e.g. a cover) just for a certain target output formats.
* `metadata`: dictionary (set of key-value pairs) with variables and values that will be passed to pandoc's command line via the `-M` option. Example:
  ```yaml
  pandoc_common:
    ...
  pandoc_targets:
    PDF:
      options: -t latex -s --chapters
      metadata:
        documentclass: report
        lang: en-US
    ...  
  ```
* `variables`: dictionary with variables and values that will be passed to pandoc's command line via the `-V` option.  

Finally, we should highlight that the contents of the build file, which we have stored so far in a separate `build.yaml` file, could be also embedded as a [Pandoc's YAML metadata block](https://pandoc.org/MANUAL.html#yaml_metadata_block) inside one of the source files pased as input to Pandoc. More generally, such a block may define both the `pandoc_common` and `pandoc_targets` properties required for Panbuild, as well as any other Pandoc variables to control the style or any other features of the final document, as explained in [Pandoc's User Manual](https://pandoc.org/MANUAL.html#variables-set-by-pandoc). In case that Panbuild-related information is included in one of the source files rather than in _build.yaml_, the name of the source file should be passed to `panbuild` as an argument of the `-f` option (e.g. `panbuild -f source.md`). This choice is specially suitable for documents consisting of a single source file. Thus, that single file would be _self contained_, in the sense that would define both the document's contents as well as the build rules for Panbuild.


### Integration with extensible text editors

Panbuild has been designed from the ground up as a tool for creating Pandoc frontends using extensible text editors (i.e. those that support plugins/addons). Today, several Pandoc frontends exist, such as the [Typora Markdown Editor](https://typora.io/) or the [Pandoc plugin for Sublime Text](https://packagecontrol.io/packages/Pandoc). Unfortunately, at the time of this writing none of these solutions allow the user to access the full Pandoc's functionality from the GUI. In particular, in these environments the user cannot control what options are passed to Pandoc; instead a set of predefined output profiles are available to the user, which cannot be fully customized with specific pandoc options. In addition, documents divided into multiple source files (such as the example discussed earlier) are simply not supported: Pandoc can be only invoked with one input file from these editors. Under these circumstances, users often have to turn to the command line to invoke Pandoc commands directly.

Despite the fact that Panbuild is a command-line tool, it features several options to allow the creation of Pandoc plugins for extensible text editors. As a proof of concept, we created a [Panbuild's plugin for Sublime Text](https://github.com/jcsaezal/SublimeText-Panbuild), which illustrates the role of `panbuild` in the creation of a graphical frontend for Pandoc, enabling full access to its entire functionality without using the command line. 

The plugin relies on the following key options of `panbuild`:

* `-L`: displays the list of targets (IDs only) found in the build file 
* `-o`: displays the set of output files (argument of Pandoc's `-o` switch) for each target. 
  ```bash
  $ panbuild -o
  PDF: report.pdf
  HTML: report.html
  EPUB: report.epub
  ```
  This option allows a plugin to figure out what specific file is generated after the execution of a Panbuild target. For example, this information could be used by a plugin to open the file automatically with the default application for it, right after the file was built by Pandoc.       


## Support

If you experience any difficulties while using Panbuild, please do not hesitate to [open an issue](https://github.com/jcsaezal/panbuild/issues) on github so that we can help.



[Python]: https://www.python.org/
[Windows]: https://www.python.org/downloads/windows/
[PyPI]: https://pypi.python.org/pypi
[pandoc]: http://pandoc.org/
[pandoc_crossref]: https://github.com/lierdakil/pandoc-crossref
[make]: https://www.gnu.org/software/make/
