# pdm-mypyc

`pdm-mypyc` is a build hook for [pdm-backend](https://github.com/pdm-project/pdm-backend) to compile source files with
[mypyc](https://mypyc.readthedocs.io/).

## Activate the hook

To enable the hook, simply add it to the `build-system.requires`:

```toml
[build-system]
requires = ["pdm-mypyc", "pdm-backend"]
build-backend = "pdm.backend"
```

Besides, you can also disable it temporarily by setting environment variable `PDM_BUILD_WITHOUT_MYPYC` to `1`.

## Configuration

### Include and exclude files

By default, all `.py` files included by the `tool.pdm.build` configuration will be compiled with mypyc. You can override
it with the `includes` and `excludes` settings under `tool.pdm.build.hooks.mypyc` table:

```toml
[tool.pdm.build.hooks.mypyc]
includes = ["src/**/*.py"]
excludes = ["src/**/tests/*.py"]  # these files will be excluded **in addition to** the excluded files in the build config
```

### Mypy arguments

You can supply supported [mypy command line options](https://mypy.readthedocs.io/en/stable/command_line.html) to the `mypycify` function with `mypy-args` setting:

```toml
[tool.pdm.build.hooks.mypyc]
mypy-args = ["--disallow-untyped-defs", "--disallow-any-generics"]
```

### Options

You can specify options to pass to the [mypycify](https://github.com/python/mypy/blob/v0.930/mypyc/build.py#L429) function.

```toml
[tool.pdm.build.hooks.mypyc.options]
opt_level = "3"
```
