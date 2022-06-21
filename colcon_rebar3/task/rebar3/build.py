# Copyright 2018 Easymov Robotics
# Licensed under the Apache License, Version 2.0

from pathlib import Path
import shutil
import os

from colcon_rebar3.task.rebar3 import REBAR3_EXECUTABLE
from colcon_core.environment import create_environment_scripts
from colcon_core.logging import colcon_logger
from colcon_core.plugin_system import satisfies_version
from colcon_core.shell import create_environment_hook, get_command_environment
from colcon_core.task import run
from colcon_core.task import TaskExtensionPoint

logger = colcon_logger.getChild(__name__)


class Rebar3BuildTask(TaskExtensionPoint):
    """Build Rebar3 packages."""

    def __init__(self):  # noqa: D107
        super().__init__()
        satisfies_version(TaskExtensionPoint.EXTENSION_POINT_VERSION, '^1.0')

    def add_arguments(self, *, parser):  # noqa: D102
        parser.add_argument(
            '--rebar3-build-args',
            nargs='*', metavar='*', type=str.lstrip,
            help='Pass arguments to rebar3 projects. '
            'Arguments matching other options must be prefixed by a space,\n'
            'e.g. --rebar3-build-args " --help"')
        parser.add_argument(
            '--rebar3-release-args',
            nargs='*', metavar='*', type=str.lstrip,
            help='Pass arguments to rebar3 projects. '
            'Arguments matching other options must be prefixed by a space,\n'
            'e.g. --rebar3-release-args " --help"')
        # parser.add_argument(
        #     '--clean-build',
        #     action='store_true',
        #     help='Remove old build dir before the build.')

    async def build(  # noqa: D102
        self, *, additional_hooks=None, skip_hook_creation=False
    ):
        if additional_hooks is None:
            additional_hooks = []
        args = self.context.args

        logger.info(
            "Building rebar3 package in '{args.path}'".format_map(locals()))

        try:
            env = await get_command_environment(
                'build', args.build_base, self.context.dependencies)
        except RuntimeError as e:
            logger.error(str(e))
            return 1

        self.progress('prepare')
        self._prepare(env, additional_hooks)
        # if rc:
        #     return rc

        # Clean up the build dir
        # self.build_dir = Path(os.path.join(args.build_base, "default"))

        # if args.clean_build:
        #     if self.build_dir.is_symlink():
        #         self.build_dir.unlink()
        #     elif self.build_dir.exists():
        #         shutil.rmtree(build_dir)

        # Invoke build step
        if REBAR3_EXECUTABLE is None:
            raise RuntimeError("Could not find 'rebar3' executable")

        rc = await self._build(args, env)
        if rc and rc.returncode:
            return rc.returncode

        rc = await self._build_binary(args, env)
        if rc and rc.returncode:
            return rc.returncode

        rc = await self._install(args, env)
        if rc and rc.returncode:
            return rc.returncode

        if not skip_hook_creation:
            create_environment_scripts(
                self.context.pkg, args, additional_hooks=additional_hooks)

    # Overridden by colcon-rebar3
    def _prepare(self, env, additional_hooks):
        pkg = self.context.pkg

        additional_hooks += create_environment_hook(
            'rebar3_{}_ament_prefix_path'.format(pkg.name),
            Path(self.context.args.install_base),
            pkg.name,
            'AMENT_PREFIX_PATH', "",
            mode="prepend"
        )

    # Overridden by colcon-rebar3
    def _build_cmd(self, verb, rebar3_args):
        if rebar3_args is None:
            rebar3_args = []
        # args = self.context.args
        return [
            REBAR3_EXECUTABLE, verb
        ] + rebar3_args

    async def _build(self, args, env):
        self.progress('build')

        cmd = self._build_cmd("compile", args.rebar3_build_args)

        return await run(
            self.context, cmd, cwd=self.context.pkg.path, env=env)

    async def _build_binary(self, args, env):
        self.progress('build binary')

        # pkg = self.context.pkg
        # os.path.join(self.context.pkg.path, '_build', "rel")
        # logger.warn(self.context.pkg.path)

        cmd = self._build_cmd("release", args.rebar3_release_args)

        return await run(
            self.context, cmd, cwd=self.context.pkg.path, env=env)

    async def _install(self, args, env):
        self.progress('install')

        pkg = self.context.pkg

        rebar3_release_dir = os.path.join(
            self.context.pkg.path, "_build", "default", "rel")
        install_dir = os.path.join(
            self.context.args.install_base, "lib", pkg.name)

        if os.path.exists(install_dir):
            shutil.rmtree(install_dir)

        shutil.copytree(rebar3_release_dir, install_dir, dirs_exist_ok=True)

        # AMENT
        ament_directory = os.path.join(
            self.context.args.install_base, "share", "ament_index", "resource_index", "packages")
        package_file = os.path.join(ament_directory, pkg.name)
        if os.path.exists(ament_directory):
            shutil.rmtree(ament_directory)
        os.makedirs(ament_directory)
        Path(package_file).touch()
        # Path(os.path.join(args.build_base, "default")
        # os.symlink(rebar3_build_dir.absolute(), self.build_dir.absolute())

        # cmd = self._build_cmd("release", args.rebar3_args)

        # return await run(
        #     self.context, cmd, cwd=self.context.pkg.path, env=env)
