import pytest

from image_templates import *


@pytest.fixture
def context() -> Context:
    import tempfile
    tempdir = tempfile.TemporaryDirectory()
    with tempdir:
        yield Context(
            images_dir=ROOT_DIR / 'tests/fixtures',
            output_dir=(Path(tempdir.name)),
        )


def test_templated_source_dirs(context: Context):
    source_dirs = sorted(
        str(_dir.relative_to(context.images_dir))
        for _dir in find_templated_source_dirs(context)
    )

    assert source_dirs == ['node.in', 'php.in']


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
