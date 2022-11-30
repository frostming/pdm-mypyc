from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from mypyc.build import mypycify
from pdm.backend.hooks import Context
from pdm.backend.wheel import WheelBuilder


class MypycBuildHook:
    DEFAULT_TARGET_DIR = ".mypy_build"

    def hook_config(self, context: Context) -> dict[str, Any]:
        return (
            context.config.data.get("tool", {})
            .get("pdm", {})
            .get("build", {})
            .get("hooks", {})
            .get("mypyc", {})
        )

    def pdm_build_hook_enabled(self, context: Context) -> bool:
        if context.target == "sdist":
            return False
        return os.getenv("PDM_BUILD_WITHOUT_MYPYC", "false").lower() == "false"

    def pdm_build_initialize(self, context: Context) -> None:
        # Save the change to the context
        context.config.data.setdefault("tool", {}).setdefault("pdm", {}).setdefault(
            "build", {}
        )
        context.config.build_config["run-setuptools"] = True

    def pdm_build_update_files(self, context: Context, files: dict[str, Path]) -> None:
        if not context.build_dir.exists():
            return
        # collect generated *.so and *.pyd files under the build dir
        for path in context.build_dir.iterdir():
            if path.name.endswith((".so", ".pyd")) and path.name not in files:
                files[path.name] = path

    def pdm_build_update_setup_kwargs(
        self, context: Context, setup_kwargs: dict[str, Any]
    ) -> None:
        hook_config = self.hook_config(context)
        args = hook_config.get("mypy-args", [])
        options = hook_config.get("options", {})
        options.setdefault("target_dir", self.DEFAULT_TARGET_DIR)
        context.config.data.setdefault("tool", {}).setdefault("pdm", {}).setdefault(
            "build", {}
        )
        if "includes" in hook_config:
            context.config.build_config["includes"] = hook_config["includes"]
        if "excludes" in hook_config:
            context.config.build_config.setdefault("excludes", []).extend(
                hook_config["excludes"]
            )

        builder = WheelBuilder(context.root, context.config_settings)
        builder.config = context.config
        files = sorted(
            k
            for k in builder._collect_files(context, context.root)
            if k.endswith(".py")
        )
        setup_kwargs.update(ext_modules=mypycify([*args, *files], **options))
