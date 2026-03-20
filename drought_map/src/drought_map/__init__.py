from shiny import ui

def DroughtMap():
    return ui.div(
        {'id': 'drought-map-container',},
        ui.div({'id': '__next'}),  # Next.js default mount ID

        ui.tags.link(rel='stylesheet', href='drought_map/styles.css'),
        ui.tags.script(src='drought_map/main.js'),
    )

__all__ = ['DroughtMap']