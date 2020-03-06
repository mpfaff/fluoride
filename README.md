# Fluoride

Fluoride is a WIP logging framework for Python 3.

## Features

- More log levels available than the native logging module.
- `sys.stdout` and `sys.stderr` are rerouted through fluoride logging, allowing for better handling of error messages and formatting of print statements.
- Integration with syslog (Linux only) and LogDNA

## Installation

```console
user@host:~$ pip3 install fluoride
```

## Usage

The first `App` registered is used for the rerouting of `sys.stdout` and `sys.stderr`.

```python
from fluoride import Level, App

app = App('Fluoride Test')
app.logger.setLevel(Level.FINEST.level)

print('Hello, World!')
app.log(Level.INFO, 'I am Chuck.')
app.log(Level.WARNING, 'There is a chance the world will end soon.')
app.log(Level.FATAL, 'THE WORLD IS ENDING!')
```
