import click
from .nucled import *

pass_dev = click.make_pass_decorator(LED)


@click.group(invoke_without_command=True)
@click.option("--ring", is_flag=True, help="Control ring led")
@click.option("--power", is_flag=True, help="Control power led")
@click.pass_context
def cli(ctx, ring, power):
    """Control LEDs of Intel NUC computers."""
    if ring and power:
        click.echo("Please specify only ring or power")
        return -1

    if ring:
        dev = Ring()
    elif power:
        dev = Power()
    else:
        dev = Ring()

    ctx.obj = dev

    if ctx.invoked_subcommand is None:
        ctx.invoke(status)


@cli.command()
@click.argument("raw")
@pass_dev
def raw(ring, raw):
    """Write raw string, useful for testing."""
    ring.set_state_from_string(raw)


@cli.command()
@click.argument("brightness", type=int, required=False)
@pass_dev
def brightness(ring, brightness):
    """Get or set brightness [0,100]."""
    if brightness:
        with ring:
            ring.brightness = brightness

    click.echo("Brightness: %s" % ring.brightness)


@cli.command()
@click.argument("color", required=False)
@pass_dev
def color(ring, color):
    """Get or set color."""
    if color:
        with ring:
            ring.color = color
            return

    click.echo("Color: %s" % ring.color)
    click.echo("Available colors")
    for c in ring.supported_colors.values():
        click.echo("- %s" % c.value)


@cli.command()
@click.argument("effect", required=False)
@pass_dev
def effect(ring, effect):
    """Get or set effect."""
    if effect:
        with ring:
            ring.effect = effect
            return

    click.echo("Current effect: %s" % ring.effect)
    click.echo("Available options:")
    for eff in list(Effect):
        print("- %s" % eff.value)


@cli.command()
@click.option("--color", required=False)
@click.option("--brightness", type=int, required=False)
@click.option("--effect", required=False)
@click.option("--duration", type=int, required=True)
@pass_dev
def notify(ring, color, brightness, effect, duration):
    """Change the LED settings for a duration."""
    with ring:
        ring.notify(
            color=color, brightness=brightness, effect=effect, duration=duration
        )


@cli.command()
@pass_dev
def status(ring):
    """Print current values for the led."""
    click.echo("== %s LED ==" % ring.__class__.__name__)
    click.echo("Brightness: %s" % ring.brightness)
    click.echo("Color: %s" % ring.color)
    click.echo("Effect: %s" % ring.effect)


if __name__ == "__main__":
    cli()
