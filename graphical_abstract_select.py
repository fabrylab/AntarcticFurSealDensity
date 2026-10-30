"""Choose the map areas shown in the graphical abstract.

    python graphical_abstract_select.py density    # seal density maps (column 2): each beach on its own
    python graphical_abstract_select.py overlap    # overlap panels (last 3 columns): each beach on its own

Left click: centre the frame there.  Mouse wheel: frame smaller / larger.
s: save to assets/graphical_abstract/extents.json.  q: close.
The frame has the shape of the panel in the graphical abstract. Then re-run graphical_abstract.ipynb.
"""
import json
import sys

import matplotlib
matplotlib.use("TkAgg")
matplotlib.rcParams["keymap.save"] = ["ctrl+s"]          # "s" saves the areas, not the window
import nbformat

MODE = sys.argv[1] if len(sys.argv) > 1 else "density"
assert MODE in ("density", "overlap"), "mode must be 'density' or 'overlap'"

# setup, helpers, data and layout from the notebook (fast: only the small files in assets/graphical_abstract)
g = {}
for c in nbformat.read("graphical_abstract.ipynb", as_version=4).cells:
    if c.cell_type == "code" and not c.source.startswith("fig, ax = make_layout()"):
        exec(c.source, g)
plt, ccrs, np, Rectangle = g["plt"], g["ccrs"], g["np"], g["Rectangle"]
BEACHES, DATA, colors, fov, areas, sd = g["BEACHES"], g["DATA"], g["colors"], g["fov"], g["areas"], g["seal_density"]

fig_l, ax_l = g["make_layout"]()
RATIO = g["panel_ratio"](ax_l["FWB", "density"] if MODE == "density" else ax_l["FWB", "overlap", "giant petrel"])
plt.close(fig_l)

path = DATA / "extents.json"
extents = json.load(open(path)) if path.exists() else {}
state = {b: dict(v) for b, v in extents.get(MODE, {}).items()}

fig, axs = plt.subplots(1, 2, figsize=(15, 7.5), subplot_kw={"projection": ccrs.Mercator()})
ax = dict(zip(BEACHES, axs))
rect = {}
for b, a in ax.items():
    g["plot_site_map"](g["SITES"][b], a, g["LAYERS"][b], layer_colors=g["FIG1_COLORS"])
    pc = ccrs.PlateCarree()
    if MODE == "density":
        a.pcolormesh(sd[b]["lon"], sd[b]["lat"], np.ma.masked_less(sd[b]["density"], 0.01), cmap="magma_r",
                     transform=pc, zorder=5)
    else:
        for c in ["pup"] + g["BIRDS"]:
            a.add_geometries([areas[b][c]], crs=pc, facecolor=colors[c] if c == "pup" else "none",
                             edgecolor=colors[c], alpha=0.5 if c == "pup" else 1, lw=1.2, zorder=5)
    lon0, lat0 = fov[b]["camera"]
    for lon1, lat1 in fov[b]["edges"]:
        a.plot([lon0, lon1], [lat0, lat1], transform=pc, color="k", lw=1, zorder=8)
    a.scatter(lon0, lat0, marker="^", s=50, color="k", transform=pc, zorder=12)
    x0, x1, y0, y1 = a.get_extent(crs=pc)
    a.set_extent([x0, x1, y0, y1], crs=pc)                  # keep the full map while frames move
    if b not in state:
        state[b] = {"center": [(x0 + x1) / 2, (y0 + y1) / 2], "width_m": 80.0}
    rect[b] = Rectangle((0, 0), 1, 1, transform=pc, fill=False, edgecolor=colors[b.lower()], lw=2.5, zorder=20)
    a.add_patch(rect[b])


def redraw():
    for b, a in ax.items():
        (lon, lat), w = state[b]["center"], state[b]["width_m"]
        mx, my = g["meters_per_deg_lon"](lat), 111_320.0
        hw, hh = w / 2 / mx, w * RATIO / 2 / my
        rect[b].set_xy((lon - hw, lat - hh)); rect[b].set_width(2 * hw); rect[b].set_height(2 * hh)
        a.set_title(f"{b}: frame {w:.0f} m × {w * RATIO:.0f} m", fontsize=11)
    fig.suptitle(f"[{MODE}]  click = centre,  wheel = size,"
                 "  s = save,  q = close", fontsize=12)
    fig.canvas.draw_idle()


def beach_of(event):
    return next((b for b, a in ax.items() if a is event.inaxes), None)


def on_click(event):
    b = beach_of(event)
    if b and event.button == 1 and event.xdata is not None:
        lon, lat = ccrs.PlateCarree().transform_point(event.xdata, event.ydata, ax[b].projection)
        state[b]["center"] = [float(lon), float(lat)]
        redraw()


def on_scroll(event):
    b = beach_of(event)
    if b:
        f = 1 / 1.1 if event.button == "up" else 1.1
        state[b]["width_m"] = float(state[b]["width_m"] * f)
        redraw()


def on_key(event):
    if event.key == "s":
        extents[MODE] = state
        json.dump(extents, open(path, "w"), indent=1)
        fig.suptitle(f"saved to {path}", fontsize=12, color="green")
        fig.canvas.draw_idle()
    elif event.key == "q":
        plt.close(fig)


fig.canvas.mpl_connect("button_press_event", on_click)
fig.canvas.mpl_connect("scroll_event", on_scroll)
fig.canvas.mpl_connect("key_press_event", on_key)
redraw()
plt.tight_layout()
plt.show()
