# Python interface for intel_nuc_led kernel driver

Some newer Intel NUCs support software controlled ring and power LEDs,
which are supported under Linux with a kernel module found in https://github.com/milesp20/intel_nuc_led .

This repository provides a simple python interface and a command-line tool using it.

# Preparation

See https://github.com/milesp20/intel_nuc_led for supported devices and instructions how to set-up the kernel driver.

# Command-line interface

```
$ nucled

== Ring LED ==
Brightness: 50
Color: Color.Red
Effect: Effect.Solid
```

```
Usage: nucled [OPTIONS] COMMAND [ARGS]...

  Control LEDs of Intel NUC computers.

Options:
  --ring   Control ring led
  --power  Control power led
  --help   Show this message and exit.

Commands:
  brightness  Get or set brightness [0,100].
  color       Get or set color.
  effect      Get or set effect.
  notify      Change the LED settings for a duration.
  raw         Write raw string, useful for testing.
  status      Print current values for the led.
```

# Library interface

Use either `Ring` or `Power` class for initialization.
All changes are done with property setters, and are first applied when calling `set_state()`.
Alternatively you can let context manager to handle this for you, e.g.,
```
from nucled import Ring, Color, Effect

with Ring() as ring:
    print("Current state: %s" % ring)
    ring.color = Color.Green
    ring.effect = Effect.FadeMedium
```
