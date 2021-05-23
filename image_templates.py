#!/usr/bin/env python3
import argparse
import os
import os.path
import shutil
from configparser import ConfigParser
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Sequence, Set

import jinja2
import pytest

ROOT_DIR = Path(os.path.dirname(__file__))
os.chdir(ROOT_DIR)


# --------------------------------------------------------------------------------------------------

@dataclass
class Context:
    images_dir: Path
    output_dir: Path


# --------------------------------------------------------------------------------------------------

@pytest.fixture
def context() -> Context:
    import tempfile
    tempdir = tempfile.TemporaryDirectory()
    with tempdir:
        yield Context(
            images_dir=ROOT_DIR / 'tests/fixtures',
            output_dir=(Path(tempdir.name)),
        )


# --------------------------------------------------------------------------------------------------


def find_templated_source_dirs(context: Context) -> Iterable[Path]:
    for image in context.images_dir.iterdir():
        if not image.name.endswith('.in'):
            continue

        yield image


def test_templated_source_dirs(context: Context):
    source_dirs = sorted(
        str(_dir.relative_to(context.images_dir))
        for _dir in find_templated_source_dirs(context)
    )

    assert source_dirs == ['node.in', 'php.in']

# --------------------------------------------------------------------------------------------------


def render_templated_dir(source: Path, destination: Path, context: dict) -> None:
    SPECIAL_FILES = {
        'template.ini',
    }

    def ignore(directory, contents: List[str]) -> Sequence[str]:
        return list(SPECIAL_FILES)

    shutil.copytree(source, destination, ignore=ignore)

    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(destination),
    )

    SUFFIX = '.j2'

    for root, dirs, files in os.walk(destination):
        root_path = Path(root)
        for name in files:
            if not name.endswith(SUFFIX):
                continue

            template_file = root_path / name
            output_file = root_path / name[:-len(SUFFIX)]

            template = env.get_template(str(template_file.relative_to(destination)))
            # print(f'> Rendering {template_file} to {output_file}')
            with open(output_file, 'w') as output:
                output.write(template.render(context))

            template_file.unlink()


def test_render_templated_dir(context: Context):
    source = context.images_dir / 'php.in'
    dest = context.output_dir / 'php_test.generated'

    if dest.is_dir():
        shutil.rmtree(dest)

    context = {'php_version': '8.0'}
    render_templated_dir(source, dest, context)

    file = dest / 'Dockerfile'
    assert file.is_file(), f"File should exist: {file}"

    contents = open(file).read()
    assert contents.startswith('FROM php:8.0-fpm-alpine\n')

# --------------------------------------------------------------------------------------------------


@dataclass
class TemplatedImage:
    source_dir: Path
    destination_dir: Path
    context: dict

    # Special context variables: identifiers are prefixed with CTX_
    CTX_IMAGE_NAME = 'image_name'

    @property
    def image_name(self) -> str:
        return self.context.get(self.CTX_IMAGE_NAME)


def find_templated_images(context: Context) -> Iterable[TemplatedImage]:
    IMAGE_SECTION_PREFIX = 'image.'
    output_dir = context.output_dir

    for source_dir in find_templated_source_dirs(context):
        config = ConfigParser()
        config.read(source_dir / 'template.ini')

        image_sections = [
            section
            for section in config.sections()
            if section.startswith(IMAGE_SECTION_PREFIX)
        ]

        for section_name in image_sections:
            section = config[section_name]
            image_name = section_name[len(IMAGE_SECTION_PREFIX):]

            context = dict(**section)
            context[TemplatedImage.CTX_IMAGE_NAME] = image_name

            destination_dir = output_dir / image_name

            yield TemplatedImage(
                source_dir=source_dir,
                destination_dir=destination_dir,
                context=context,
            )


def test_find_templates_to_render_and_contexts(context: Context):
    for t in find_templated_images(context):
        render_templated_dir(
            t.source_dir,
            t.destination_dir.with_name(t.destination_dir.name + '_test.generated'),
            t.context
        )

    image_dir = context.output_dir / 'php80_test.generated'
    assert image_dir.is_dir(), f"Directory should exist: {image_dir}"

    template_ini = image_dir / 'template.ini'
    assert not template_ini.exists(), f"File should not exist: {template_ini}"

    dockerfile = image_dir / 'Dockerfile'
    assert dockerfile.is_file(), f"File should exist: {dockerfile}"
    contents = open(dockerfile).read()
    assert contents.startswith('FROM php:8.0-fpm-alpine\n')


# --------------------------------------------------------------------------------------------------


def handler_generate(args, context):
    def ignore(template: TemplatedImage) -> bool:
        return args.only is not None \
               and template.image_name not in args.only

    for t in find_templated_images(context):
        if ignore(t):
            continue

        destination_dir = t.destination_dir.with_name(t.destination_dir.name + args.suffix)
        if destination_dir.exists():
            if not args.force:
                raise FileExistsError(f"{destination_dir} already exists. Use --force to allow removing it")

            shutil.rmtree(destination_dir)

        render_templated_dir(
            t.source_dir,
            destination_dir,
            t.context
        )


def comma_separated_set(values: str) -> Set[str]:
    return set(values.split(','))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--generate', action='store_const', const='generate', dest='handler')
    parser.add_argument('-f', '--force', action='store_true',
                        help="force removing and rebuilding images that already exist")
    parser.add_argument('--suffix', default='.generated')
    parser.add_argument('--only', type=comma_separated_set, default=None)
    parser.add_argument('--output-dir', '-o', metavar='DIR', required=True)
    args = parser.parse_args()

    context = Context(
        images_dir=ROOT_DIR,  # TODO
        output_dir=Path(args.output_dir),
    )

    if args.handler:
        handler = globals()['handler_' + args.handler]
        handler(args, context)
    else:
        raise ValueError('missing command')


if __name__ == "__main__":
    main()
