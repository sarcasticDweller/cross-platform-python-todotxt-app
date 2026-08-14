# KivyMD elevation-shadow crash: `ValueError: x1 must be greater than or equal to x0`

Any KivyMD 1.0.2 widget with `CommonElevationBehavior` (the `elevation` property that all the
"floating"/"raised" widgets have) can crash the app on its first layout pass with:

```
ValueError: x1 must be greater than or equal to x0
```

This has already bitten this project twice (see resolved ISSUE-030 and ISSUE-038 in
`docs/issues.md`) in two unrelated files, so it's worth understanding once instead of
rediscovering it per-widget.

## Root cause

It's a geometry bug in `kivymd/uix/behaviors/elevation.py`, not a Pillow version issue.

`RoundedRectangularElevationBehavior.__draw_shadow__` draws the shadow as four corner
pie-slices plus two straight-edge rectangle strips filling the gap between them:

```python
context.rectangle([origin[0] + radius, origin[1], end[0] - radius, end[1]], ...)
context.rectangle([origin[0], origin[1] + radius, end[0], end[1] - radius], ...)
```

That only makes sense if `radius` is smaller than half the widget's size — otherwise the two
corner pie-slices already cover the whole shape, and the "straight edge" strip's start point
(`origin + radius`) ends up *past* its end point (`end - radius`). Passing a rectangle where
`x1 < x0` to Pillow's `ImageDraw.rectangle()` raises this exact `ValueError`. Reproduced directly:

```python
from PIL import Image, ImageDraw
img = Image.new("RGBA", (60, 60))
ImageDraw.Draw(img).rectangle([30, 2, 29, 57], fill=(255, 255, 255, 255))  # raises
```

**This reproduces with `pillow==9.5.0`, the version already pinned in this repo** — it is not
a newer-Pillow regression. `CLAUDE.md`'s dependency-pinning section currently attributes an
earlier instance of this same `ValueError` to an unpinned Pillow resolving to 12.3.0; that
diagnosis doesn't hold up empirically and is worth reconciling (flagged, not fixed here — this
doc only covers the elevation-shadow bug itself).

So: `radius >= size / 2` on any elevated widget crashes, regardless of Pillow version. That
condition is exactly "fully rounded" — i.e. **any perfectly circular elevated widget** — which
is why it keeps showing up on `MDFloatingActionButton`: KivyMD's own `set__radius()` sets its
corner radius to `dp(28)` for the M3 style, and its default size is `dp(56) x dp(56)` — radius
is exactly half the size, a perfect circle.

## Why it crashes on startup, not on drawing

The crash isn't triggered by anything ever appearing on screen. `CommonElevationBehavior.__init__`
schedules its first shadow computation with `Clock.schedule_once(self.shadow_preset, -1)` —
i.e. "run on the next frame" — and that computation happens in pure Python/Pillow, independent
of whether the widget has actually been rendered. Any widget with nonzero `elevation` and a
radius at or above half its size will crash on the very next Kivy frame after it's constructed.

## The fix: force `elevation = 0` before the next frame

The whole shadow-drawing code path is gated behind one check
(`elevation.py`, inside `_update_shadow`):

```python
if self._elevation > 0 and self._fake_elevation is False:
    # ... all the Pillow drawing happens here
```

So forcing `elevation = 0` on the offending widget entirely skips the buggy code, before it
ever runs. Two shapes this takes in this codebase:

**Widgets you build yourself in KV** — set it as part of construction, before the first frame:

```kv
MDFloatingActionButton:
    on_kv_post: self.elevation = 0
```

**Widgets a third-party class builds internally** (e.g. `MDFileManager` builds its own
floating action button and toolbar from KV you don't control) — walk the resulting tree
right after construction and zero out anything with an `elevation` property:

```python
self.file_manager = MDFileManager(...)
for widget in self.file_manager.walk():
    if hasattr(widget, "elevation"):
        widget.elevation = 0
```

Watch for widgets that exist but aren't part of the widget tree `.walk()` sees — e.g.
`MDTopAppBar` keeps its own floating action button as a plain `self.action_button` attribute,
not necessarily an added child, so it needs the same override applied explicitly:

```python
self.file_manager.ids.toolbar.action_button.elevation = 0
```

Both must run synchronously, in the same call stack as construction — waiting until after
`.show()`/`.open()` or the next frame is too late.

## How to avoid this going forward

Before giving any KivyMD widget a nonzero `elevation`, check whether its corner radius can
reach (or exceed) half its width/height — a fully rounded pill shape or a circle. If so, either:

- leave `elevation` at `0` (this project's current default for every FAB/app-bar, since the
  shadow effect isn't otherwise in use), or
- keep the widget's `radius` strictly below half its size if the shadow effect is wanted.

If you hit this crash on a new widget, `self.<widget>.radius` vs `self.<widget>.size` at crash
time is the first thing to check — if radius is ≥ half the size on either axis, this is why.
