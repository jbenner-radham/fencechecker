fencechecker
============

A CLI app that will execute any fenced code blocks of Python in Markdown files
to ensure they don't raise any errors.

![Animated demo of fencechecker.](images/demo.gif)

Usage
-----

### [Pre-commit](https://pre-commit.com/)

You can add `fencechecker` to your `.pre-commit-config.yaml` like so:

```yaml
repos:
  - repo: https://github.com/jbenner-radham/fencechecker
    rev: be38e65
    hooks:
      # Check Python fenced code blocks in Markdown files.
      - id: fencechecker
        args: [--venv-path, .venv]
```

**NOTE**: The `rev` property is usually the version tag of the project repo.
However, `fencechecker` does not yet have any tagged releases. So feel free to
use the rev specified above. If you desire to use a different rev you can pull
this repo down and run `git rev-parse --short HEAD` to get the rev.

**NOTE**: You will almost assuredly need to set the `--venv-path` flag to define
your virtualenv so that `fencechecker` will be able to locate your project
modules and dependencies.

### CLI

```sh-session
❯ fencechecker --help

 Usage: fencechecker [OPTIONS] FILEPATHS...

 Check Python fenced code blocks in Markdown files.


╭─ Arguments ──────────────────────────────────────────────────────────────────╮
│ *    filepaths      FILEPATHS...  Check these Markdown files. [required]     │
╰──────────────────────────────────────────────────────────────────────────────╯
╭─ Options ────────────────────────────────────────────────────────────────────╮
│ --only-report-errors  -e            Only include errors when reporting.      │
│ --python-binary       -p      TEXT  Use this Python binary to execute code.  │
│                                     [default: python3]                       │
│ --venv-path           -V      PATH  Operate within this virtualenv.          │
│ --version             -v            Print version info and exit.             │
│ --install-completion                Install completion for the current       │
│                                     shell.                                   │
│ --show-completion                   Show completion for the current shell,   │
│                                     to copy it or customize the              │
│                                     installation.                            │
│ --help                -h            Show this message and exit.              │
╰──────────────────────────────────────────────────────────────────────────────╯
```

**NOTE**: The exit code of the app is the number of errors encountered. Thus, a
run without issue will exit with a code of `0`.

Example
-------

You can run `fencechecker` with this readme and yield the following results:

The below code example will pass with a status of OK.

```python
assert 1 == 1
```

The below code example will fail with an error status.

```python
assert 2 == 3
```

License
-------

The MIT License. See the [license file](LICENSE) for details.
