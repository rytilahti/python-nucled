import enum
import re
import time
import logging

_LOGGER = logging.getLogger(__name__)


class LEDException(Exception):
    pass


class Effect(enum.Enum):
    BlinkFast = "blink_fast"
    BlinkMedium = "blink_medium"
    BlinkSlow = "blink_slow"
    FadeFast = "fade_fast"
    FadeMedium = "fade_medium"
    FadeSlow = "fade_slow"
    Solid = "none"


EFFECT_MAP = {
    0x00: Effect.Solid,  # for power
    0x01: Effect.BlinkFast,
    0x02: Effect.BlinkSlow,
    0x03: Effect.FadeFast,
    0x04: Effect.Solid,
    0x05: Effect.BlinkMedium,
    0x06: Effect.FadeSlow,
    0x07: Effect.FadeMedium,
}


class Color(enum.Enum):
    Off = "off"
    Amber = "amber"
    Cyan = "cyan"
    Pink = "pink"
    Yellow = "yellow"
    Blue = "blue"
    Red = "red"
    Green = "green"
    White = "white"


class LED:
    """Interface for Intel NUC power and ring LEDs.

    Changing the LED settings require you to call `set_state`,
    which promptly activates the current settings.

    .. code-block:
        led.color = 'green'
        led.brightness = 100
        led.set_state()

    Instead of manually doing that, a context-manager can be used to
    achieve the same result as above:
    .. code-block:
       with led:
           led.color = 'green'
           led.brightness = 100
    """

    def __init__(self, target, path="/proc/acpi/nuc_led"):
        self._path = path
        self._target = target
        self.supported_colors = {}

        self._brightness = None
        self._color = None
        self._effect = None

    def _parse_brightness(self, value):
        return int(value.strip().strip("%"))

    def _parse_color(self, value):
        x = re.search("\((.+)\)", value)
        return self.supported_colors[int(x.groups(1)[0], 16)]

    def _parse_effect(self, value):
        x = re.search("\((.+)\)", value)
        return EFFECT_MAP[int(x.groups(1)[0], 16)]

    def fetch_state(self):
        """Read the led state file and fill in property values."""
        _LOGGER.debug("Reading state")
        with open(self._path) as f:
            for l in f:
                l = l.strip()
                if len(l) == 0 or l == "\x00":
                    continue
                try:
                    desc, value = l.strip().split(":")
                except:
                    raise
                    pass
                if not desc.lower().startswith(self._target):
                    continue
                if "Brightness" in desc:
                    self._brightness = self._parse_brightness(value)
                elif "Blink" in desc:
                    self._effect = self._parse_effect(value)
                elif "Color" in desc:
                    self._color = self._parse_color(value)
                # print(desc, value)

    def get_state_string(self):
        """Return current state as wanted by the kernel driver."""
        if self._brightness is None:
            self.fetch_state()
        state = "%s,%i,%s,%s" % (
            self._target,
            self._brightness,
            self._effect.value,
            self._color.value,
        )
        _LOGGER.debug("Returning state: %s" % state)
        return state

    def set_state_from_string(self, x):
        """Set the led state from a raw control string.

        See `:func: get_state_string`
        """
        _LOGGER.debug("Setting raw state: %s" % x)
        with open(self._path, "w") as f:
            f.write(x)

        self.fetch_state()

    def set_state(self):
        """Set current state to the device."""
        state = self.get_state_string()
        _LOGGER.debug("Setting state: %s" % state)
        with open(self._path, "w") as f:
            f.write(state)

    @property
    def color(self):
        """Return currently active color."""
        if self._color is None:
            self.fetch_state()
        return self._color

    @color.setter
    def color(self, color: Color):
        """Set color."""
        if isinstance(color, str):
            color = Color(color)
        if color not in self.supported_colors.values():
            raise LEDException("Tried to set unsupported color: %s" % color)
        self._color = color

    @property
    def brightness(self) -> int:
        """Return current brightness."""
        if self._brightness is None:
            self.fetch_state()
        return self._brightness

    @brightness.setter
    def brightness(self, brightness: int):
        """Set brightness."""
        if brightness < 0 or brightness > 100:
            raise LEDException("Brightness must be [0-100], was: %s" % brightness)
        self._brightness = brightness

    @property
    def effect(self) -> Effect:
        """Return current effect."""
        if self._effect is None:
            self.fetch_state()
        return self._effect

    @effect.setter
    def effect(self, effect):
        """Set effect.

        Takes either name of the effect, or alternative an Effect instance."""
        if isinstance(effect, str):
            effect = Effect(effect)
        self._effect = effect

    def notify(self, *, color, brightness, effect, duration):
        """Set a temporary state for the LED for given duration."""
        current_state = self.get_state_string()
        _LOGGER.debug("Starting notifying, original state: %s" % current_state)
        if color is not None:
            self.color = color
        if brightness is not None:
            self.brightness = brightness
        if effect is not None:
            self.effect = effect
        self.set_state()
        time.sleep(duration)
        self.set_state_from_string(current_state)

    def __enter__(self):
        """Fetches the state and returns self."""
        self.fetch_state()
        return self

    def __exit__(self, *args, **kwargs):
        """On exit the current property values are set to the device."""
        self.set_state()

    def __repr__(self):
        return "%s: bright %s, color %s, effect %s" % (
            self._target,
            self._brightness,
            self._color,
            self._effect,
        )


class Ring(LED):
    """Represents NUC ring LED."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, target="ring", **kwargs)
        self.supported_colors = {
            0x00: Color.Off,
            0x01: Color.Cyan,
            0x02: Color.Pink,
            0x03: Color.Yellow,
            0x04: Color.Blue,
            0x05: Color.Red,
            0x06: Color.Green,
            0x07: Color.White,
        }


class Power(LED):
    """Represents NUC power LED."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, target="power", **kwargs)
        self.supported_colors = {0x00: Color.Off, 0x01: Color.Blue, 0x02: Color.Amber}
