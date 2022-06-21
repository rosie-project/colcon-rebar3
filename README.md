# colcon-rebar3

An extension for [colcon-core](https://github.com/colcon/colcon-core) to support [rebar3](https://rebar3.readme.io/) projects.

## Features

For all packages with `rebar.config` files:

- `colcon build` will call `rebar3 release`

## Try it out

### Using pip

```bash
python -m pip install -U git+https://github.com/rosie-project/colcon-rebar3.git
```

### From source

Follow the instructions at https://colcon.readthedocs.io/en/released/developer/bootstrap.html, except in "Fetch the sources" add the following to `colcon.repos`:

```yaml
  colcon-rebar3:
    type: git
    url: https://github.com/rosie-project/colcon-rebar3.git
    version: main
```

After that, run the `local_setup` file, build any colcon workspace with rebar3 projects in it, and report any issues!
