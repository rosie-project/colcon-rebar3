# Copyright 2018 Easymov Robotics
# Licensed under the Apache License, Version 2.0

from colcon_core.logging import colcon_logger
from colcon_core.package_identification \
    import PackageIdentificationExtensionPoint
from colcon_core.plugin_system import satisfies_version
import re

logger = colcon_logger.getChild(__name__)


class Rebar3PackageIdentification(PackageIdentificationExtensionPoint):
    """Identify Rebar3 packages with `rebar.config` files."""

    def __init__(self):  # noqa: D107
        super().__init__()
        satisfies_version(
            PackageIdentificationExtensionPoint.EXTENSION_POINT_VERSION,
            '^1.0')

    def identify(self, metadata):  # noqa: D102
        if metadata.type is not None and metadata.type != 'rebar3':
            return

        rebar_config = metadata.path / 'rebar.config'
        if not rebar_config.is_file():
            return

        data = extract_data(rebar_config)
        if not data:
            raise RuntimeError(
                'Failed to extract rebar3 package information from "%s"'
                % rebar_config.absolute())

        metadata.type = 'rebar3'
        # if metadata.name is None:
        #     metadata.name = data['name']
        metadata.name = metadata.path.stem
        metadata.dependencies['build'] |= data["depends"]
        metadata.dependencies['run'] |= data["depends"]


def extract_data(rebar_config):
    """
    Extract the project name and dependencies from a rebar.config file.

    :param Path rebar_config: The path of the rebar.config file
    :rtype: dict
    """

    with open(rebar_config, "r") as f:
        content = f.read()

    data = {}
    data["depends"] = extract_dependencies(content)

    return data


def extract_project_name(content):
    """
    Extract the Cargo project name from the Cargo.toml file.

    :param str content: The Cargo.toml parsed dictionnary
    :returns: The project name, otherwise None
    :rtype: str
    """
    try:
        return content['package']['name']
    except KeyError:
        return None


def extract_dependencies(content):
    """
    Extract the dependencies from the Cargo.toml file.

    :param str content: The Cargo.toml parsed dictionnary
    :returns: The dependencies name
    :rtype: list
    """

    res = set()
    pattern = re.compile(r"\{(\w+)\s*,\s*\{ros2")
    # print(result.groups())
    for match in pattern.finditer(content):
        res.add(match.group(1))
    return res
