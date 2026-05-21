"""
XYZ Grid integration for Prompt Formatter.

Adds a "[Prompt Formatter] Enabled" axis option so you can grid-test
generations with and without prompt formatting enabled.
"""

from modules import scripts


def str_to_bool(v: str) -> bool:
    """Convert "True"/"False" (or any casing) to bool."""
    return v.strip().lower() == "true"


def patch_xyz_grid():
    """Register Prompt Formatter axis options into the global xyz_grid module."""
    xyz_grid = None
    for data in scripts.scripts_data:
        if data.script_class.__module__ in ("xyz_grid.py", "scripts.xyz_grid") and hasattr(data, "module"):
            xyz_grid = data.module
            break

    if xyz_grid is None:
        print("[Prompt Formatter] xyz_grid not found — skipping XYZ Grid integration")
        return

    # Avoid duplicate registration if the script is reloaded
    label = "[Prompt Formatter] Enabled"
    if any(x.label == label for x in xyz_grid.axis_options):
        return

    xyz_grid.axis_options.extend([
        xyz_grid.AxisOption(
            label,
            str_to_bool,                                         # type_func: "True" → True
            xyz_grid.apply_field("prompt_formatter_enabled"),    # sets p.prompt_formatter_enabled
            choices=lambda: ["True", "False"],
        ),
    ])


try:
    patch_xyz_grid()
except Exception as e:
    print(f"[Prompt Formatter] Failed to patch xyz_grid: {e}")
