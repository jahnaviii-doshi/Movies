"""The Weather Keeper of Block C: film-specific rigs, sets, audio and scenes.

Importing this package sets the film's drawing style: flat-graphic with a gentle
hand-drawn line wobble that boils at 8 fps.
"""
from ... import core as _core

_core.STYLE.update(wobble=0.55, wobble_seg=5.0, boil_fps=8)
