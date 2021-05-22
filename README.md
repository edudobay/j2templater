# Templated Dockerfiles — a template processing tool

This tool was designed for generating similar Docker builds from a common template, addressing the maintenance burden that might emerge when many similar files must be kept in sync but with some differences.

There's nothing about the tool that is specific for Docker, although the naming of the concepts might be slightly biased. The tool simply takes a directory and a set of input variables, processes templated or untemplated files, and outputs it to another directory.


## Setup

Requires Python ≥ 3.7 and [Jinja][jinja]. Dependencies can be installed using pip (Python package manager) or native operating system packages:

* Virtual environment: `pip install Jinja2`
* Alpine Linux: `apk add py3-jinja`
* Debian/Ubuntu: `apt-get install python3-jinja2`


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
