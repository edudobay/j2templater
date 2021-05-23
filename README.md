# Templated Dockerfiles — a template processing tool

This tool was designed for generating similar Docker builds from a common template, addressing the maintenance burden that might emerge when many similar files must be kept in sync but with some differences.

There's nothing about the tool that is specific for Docker, although the naming of the concepts might be slightly biased. The tool simply takes a directory and a set of input variables, processes templated or untemplated files, and outputs it to another directory.


## Setup

Requires Python ≥ 3.7.

### Install using native OS packages

Install the [Jinja][jinja] dependency:

* Alpine Linux: `apk add py3-jinja`
* Debian/Ubuntu: `apt-get install python3-jinja2`
* pip (usually in a virtual environment): `pip install Jinja2`

Then copy `image_templates.py` to the folder of your liking.


### Install using pip (Python package manager)

Run `pip install .` in the current directory, in an appropriate virtual environment.

If in doubt, run `python -m venv ./venv` and then use `./venv/bin/pip` to run `pip` inside the virtual environment.


## Examples

Example INI file:

```ini
# images/php.in/template.ini
[image.php80]
php_version = 8.0

[image.php74]
php_version = 7.4
```

[jinja]: https://jinja.palletsprojects.com/
