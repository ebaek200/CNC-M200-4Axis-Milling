"""
CNC-M200 4-Axis Milling Machine — Complete 3D Assembly Model
=============================================================
Machine Type   : Fixed Column Box Frame, 4-Axis CNC Mill
Work Area      : 200 x 200 x 100 mm (XYZ)
4th Axis       : A-axis rotary (K11-100 chuck)
Total Weight   : ~76 kg
All dims in mm.

Layer Map:
  A_Frame        — Steel Blue   — Base, columns, top plate, back wall, gussets,
                                   Y-saddle, X-table
  B_Linear       — Green        — HGR20 rails, HGH20CA blocks, SFU1605 ball screws,
                                   BK12/BF12 bearings
  C_Spindle      — Orange       — Z-head plate, spindle body, ER11 collet
  D_Rotary       — Purple       — Rotary body, K11-100 chuck, tailstock
  E_Motors       — Yellow       — NEMA23 x4 (X, Y, Z, A)
  F_Electronics  — Cyan         — Control box, VFD, PSU

Script for Rhino 7/8 Python (rhinoscriptsyntax).
Run via: _RunPythonScript or drag into Rhino viewport.
"""

import rhinoscriptsyntax as rs
import Rhino
import System.Drawing.Color as Color

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_box(corner, lx, ly, lz):
    """Create an axis-aligned box from a corner point and dimensions."""
    pts = [
        (corner[0],      corner[1],      corner[2]),
        (corner[0] + lx, corner[1],      corner[2]),
        (corner[0] + lx, corner[1] + ly, corner[2]),
        (corner[0],      corner[1] + ly, corner[2]),
        (corner[0],      corner[1],      corner[2] + lz),
        (corner[0] + lx, corner[1],      corner[2] + lz),
        (corner[0] + lx, corner[1] + ly, corner[2] + lz),
        (corner[0],      corner[1] + ly, corner[2] + lz),
    ]
    return rs.AddBox(pts)


def make_cylinder_z(cx, cy, cz, radius, height):
    """Cylinder along +Z from base centre (cx, cy, cz)."""
    base = rs.AddCircle((cx, cy, cz), radius)
    cyl = rs.ExtrudeCurveStraight(base, (0, 0, 0), (0, 0, height))
    cap = rs.CapPlanarHoles(cyl)
    rs.DeleteObject(base)
    return cap if cap else cyl


def make_cylinder_y(cx, cy, cz, radius, length):
    """Cylinder along +Y from base centre."""
    base = rs.AddCircle(rs.PlaneFromNormal((cx, cy, cz), (0, 1, 0)), radius)
    cyl = rs.ExtrudeCurveStraight(base, (0, 0, 0), (0, length, 0))
    cap = rs.CapPlanarHoles(cyl)
    rs.DeleteObject(base)
    return cap if cap else cyl


def make_cylinder_x(cx, cy, cz, radius, length):
    """Cylinder along +X from base centre."""
    base = rs.AddCircle(rs.PlaneFromNormal((cx, cy, cz), (1, 0, 0)), radius)
    cyl = rs.ExtrudeCurveStraight(base, (0, 0, 0), (length, 0, 0))
    cap = rs.CapPlanarHoles(cyl)
    rs.DeleteObject(base)
    return cap if cap else cyl


def set_layer(obj, layer_name):
    """Assign object to layer."""
    if obj:
        rs.ObjectLayer(obj, layer_name)


def label(text, pt, layer_name):
    """Place a text dot label and assign to layer."""
    dot = rs.AddTextDot(text, pt)
    if dot:
        rs.ObjectLayer(dot, layer_name)


def make_gusset_triangle(origin, dx, dy, thickness, axis='z'):
    """
    Create a triangular gusset plate as a closed polysurface.
    The right-angle triangle lies in the plane defined by axis.
    axis='z' means the triangle spans dx in X, dy in Y, and is extruded along Z.
    axis='x' means the triangle spans dy in Y, dz in Z, extruded along X.
    """
    ox, oy, oz = origin
    if axis == 'z':
        pts = [(ox, oy, oz), (ox + dx, oy, oz), (ox, oy + dy, oz), (ox, oy, oz)]
        crv = rs.AddPolyline(pts)
        ext = rs.ExtrudeCurveStraight(crv, (0, 0, 0), (0, 0, thickness))
        cap = rs.CapPlanarHoles(ext)
        rs.DeleteObject(crv)
        return cap if cap else ext
    elif axis == 'x':
        pts = [(ox, oy, oz), (ox, oy + dy, oz), (ox, oy, oz + thickness), (ox, oy, oz)]
        crv = rs.AddPolyline(pts)
        ext = rs.ExtrudeCurveStraight(crv, (0, 0, 0), (dx, 0, 0))
        cap = rs.CapPlanarHoles(ext)
        rs.DeleteObject(crv)
        return cap if cap else ext


# ---------------------------------------------------------------------------
# Layer Setup
# ---------------------------------------------------------------------------

layers = {
    "A_Frame":        Color.FromArgb(70, 130, 180),   # Steel Blue
    "B_Linear":       Color.FromArgb(0, 180, 0),      # Green
    "C_Spindle":      Color.FromArgb(255, 140, 0),    # Orange
    "D_Rotary":       Color.FromArgb(148, 0, 211),    # Purple
    "E_Motors":       Color.FromArgb(230, 200, 0),    # Yellow
    "F_Electronics":  Color.FromArgb(0, 200, 200),    # Cyan
}

for name, color in layers.items():
    if not rs.IsLayer(name):
        rs.AddLayer(name, color)
    else:
        rs.LayerColor(name, color)

# ---------------------------------------------------------------------------
# A_Frame — Structural Frame
# ---------------------------------------------------------------------------
LY = "A_Frame"

# Base plate P1: 500 x 450 x 20  (origin at 0,0,0 means centred in X/Z)
p1 = make_box((-250, 0, -225), 500, 20, 450)
set_layer(p1, LY)
label("P1 Base Plate\n500x450x20", (0, 10, 0), LY)

# Left column P2: 20 x 400 x 350  at x = -230 (inner face)
p2 = make_box((-250, 20, -175), 20, 400, 350)
set_layer(p2, LY)
label("P2 Left Column", (-240, 220, 0), LY)

# Right column P3: 20 x 400 x 350  at x = +230 (inner face)
p3 = make_box((230, 20, -175), 20, 400, 350)
set_layer(p3, LY)
label("P3 Right Column", (240, 220, 0), LY)

# Top plate P4: 500 x 20 x 350  at y = 400
p4 = make_box((-250, 420, -175), 500, 20, 350)
set_layer(p4, LY)
label("P4 Top Plate\n500x20x350", (0, 430, 0), LY)

# Back wall P5: 500 x 380 x 20  at z = -165
p5 = make_box((-250, 20, -175), 500, 400, 20)
set_layer(p5, LY)
label("P5 Back Wall", (0, 220, -165), LY)

# Gussets — 4 triangular plates at frame corners (50x50x10)
# Bottom-left
g1 = make_gusset_triangle((-230, 20, -155), 50, 50, 10, 'z')
set_layer(g1, LY)
# Bottom-right
g2 = make_gusset_triangle((180, 20, -155), 50, 50, 10, 'z')
set_layer(g2, LY)
# Top-left
g3 = make_gusset_triangle((-230, 370, -155), 50, 50, 10, 'z')
set_layer(g3, LY)
# Top-right
g4 = make_gusset_triangle((180, 370, -155), 50, 50, 10, 'z')
set_layer(g4, LY)
label("Gussets x4", (-230, 45, -150), LY)

# ---------------------------------------------------------------------------
# Y-axis Saddle (on A_Frame layer) — slides on Y rails on base
# 350 x 30 x 300, at y=60
# ---------------------------------------------------------------------------
saddle = make_box((-175, 50, -150), 350, 30, 300)
set_layer(saddle, LY)
label("Y Saddle\n350x30x300", (0, 65, 0), LY)

# ---------------------------------------------------------------------------
# X-axis Table (on A_Frame layer)
# T-slot table: 250 x 25 x 250, at y=90
# ---------------------------------------------------------------------------
table = make_box((-125, 80, -125), 250, 25, 250)
set_layer(table, LY)
label("X Table\n250x25x250", (0, 92, 0), LY)

# T-slots — 5 grooves (8mm wide x 10mm deep) across X direction
for i in range(5):
    z_start = -100 + i * 50
    slot = make_box((-125, 95, z_start - 4), 250, 10, 8)
    if slot:
        # Boolean difference would be ideal, but we draw the slots as
        # separate darker boxes for visual clarity
        set_layer(slot, LY)

# ---------------------------------------------------------------------------
# B_Linear — Rails, Blocks, Ball Screws, Bearings
# ---------------------------------------------------------------------------
LY_B = "B_Linear"

# --- HGR20 Rails (20 x 20 x L thin boxes) ---

# X-axis rails: 2 rails at y=80, z=+/-100, length 400mm along X
for z_off in [-100, 100]:
    rail = make_box((-200, 108, z_off - 10), 400, 20, 20)
    set_layer(rail, LY_B)
label("HGR20 X-Rails x2", (0, 118, 110), LY_B)

# Y-axis rails: 2 rails on base plate, x=+/-150, length 350mm along Z
for x_off in [-150, 150]:
    rail = make_box((x_off - 10, 20, -175), 20, 20, 350)
    set_layer(rail, LY_B)
label("HGR20 Y-Rails x2", (160, 30, 0), LY_B)

# Z-axis rails: 2 rails on back wall, x=+/-80, length 300mm along Y
for x_off in [-80, 80]:
    rail = make_box((x_off - 10, 130, -155), 20, 300, 20)
    set_layer(rail, LY_B)
label("HGR20 Z-Rails x2", (90, 280, -145), LY_B)

# --- HGH20CA Blocks (44 x 30 x 28) — 2 per rail = 12 total ---

# X-axis blocks (4): 2 per rail, at x offsets -80 and +80
for z_off in [-100, 100]:
    for x_off in [-80, 80]:
        blk = make_box((x_off - 22, 105, z_off - 14), 44, 30, 28)
        set_layer(blk, LY_B)

# Y-axis blocks (4): 2 per rail, at z offsets -60 and +60
for x_off in [-150, 150]:
    for z_off in [-60, 60]:
        blk = make_box((x_off - 15, 18, z_off - 14), 30, 28, 44)
        set_layer(blk, LY_B)

# Z-axis blocks (4): 2 per rail, at y offsets 200 and 330
for x_off in [-80, 80]:
    for y_off in [200, 330]:
        blk = make_box((x_off - 15, y_off - 22, -160), 30, 44, 28)
        set_layer(blk, LY_B)

label("HGH20CA Blocks x12", (-80, 135, -114), LY_B)

# --- SFU1605 Ball Screws (dia 16mm cylinders) ---

# X ball screw: length 350, along X, centred at y~115, z=0
x_screw = make_cylinder_x(-175, 118, 0, 8, 350)
set_layer(x_screw, LY_B)
label("SFU1605 X-Screw\nL350", (0, 118, 0), LY_B)

# Y ball screw: length 300, along Z (Y-axis of machine travels in Z here)
y_screw = make_cylinder_z(0, 30, -150, 8, 300)
set_layer(y_screw, LY_B)
label("SFU1605 Y-Screw\nL300", (0, 30, 0), LY_B)

# Z ball screw: length 250, along Y (vertical)
z_screw = make_cylinder_y(0, 150, -145, 8, 250)
set_layer(z_screw, LY_B)
label("SFU1605 Z-Screw\nL250", (0, 275, -145), LY_B)

# --- BK12/BF12 Bearings — small cylinders at screw ends ---
# X screw bearings
for cx in [-175, 175]:
    brg = make_cylinder_x(cx - 10, 118, 0, 12, 20)
    set_layer(brg, LY_B)

# Y screw bearings
for cz in [-150, 150]:
    brg = make_cylinder_z(0, 30, cz - 10, 12, 20)
    set_layer(brg, LY_B)

# Z screw bearings
for cy in [150, 400]:
    brg = make_cylinder_y(0, cy - 10, -145, 12, 20)
    set_layer(brg, LY_B)

label("BK12/BF12 x6", (185, 118, 0), LY_B)

# ---------------------------------------------------------------------------
# C_Spindle — Z-axis head plate, spindle body, ER11 collet
# ---------------------------------------------------------------------------
LY_C = "C_Spindle"

# Z-axis head plate: 200 x 250 x 20, centred on Z rails
head_plate = make_box((-100, 180, -155), 200, 250, 20)
set_layer(head_plate, LY_C)
label("Z-Head Plate\n200x250x20", (0, 305, -145), LY_C)

# Spindle body: cylinder dia 65, length 200, hanging below head plate
# Mounted on head plate face, pointing toward workpiece (+Z direction)
spindle = make_cylinder_z(0, 280, -135, 32.5, 200)
set_layer(spindle, LY_C)
label("Spindle\ndia65 L200", (0, 280, -35), LY_C)

# ER11 collet: small cylinder dia 20, length 30 at spindle tip
collet = make_cylinder_z(0, 280, 65, 10, 30)
set_layer(collet, LY_C)
label("ER11 Collet", (0, 280, 95), LY_C)

# ---------------------------------------------------------------------------
# D_Rotary — 4th Axis: Rotary body, K11-100 chuck, Tailstock
# ---------------------------------------------------------------------------
LY_D = "D_Rotary"

# Rotary body: cylinder dia 100, length 80, on the X-table
# Positioned on left side of table, axis along X
rotary_body = make_cylinder_x(-80, 105, 0, 50, 80)
set_layer(rotary_body, LY_D)
label("Rotary Body\ndia100 L80", (-40, 155, 0), LY_D)

# K11-100 chuck: cylinder dia 100, length 40
chuck = make_cylinder_x(0, 105, 0, 50, 40)
set_layer(chuck, LY_D)
label("K11-100 Chuck\ndia100", (20, 155, 0), LY_D)

# Tailstock: box 60 x 65 x 80 + cone tip
tailstock_body = make_box((70, 105, -40), 60, 65, 80)
set_layer(tailstock_body, LY_D)

# Tailstock cone (approximated as a small cylinder tapering)
tail_cone = make_cylinder_x(70, 137, 0, 10, -20)
set_layer(tail_cone, LY_D)
label("Tailstock", (100, 137, 40), LY_D)

# ---------------------------------------------------------------------------
# E_Motors — NEMA23 x 4
# ---------------------------------------------------------------------------
LY_E = "E_Motors"

# NEMA23 motor body: 56 x 56 x 56 mm

# X motor — at end of X ball screw (left side, -X)
mx = make_box((-231, 90, -28), 56, 56, 56)
set_layer(mx, LY_E)
label("NEMA23\nX-Motor", (-203, 118, 28), LY_E)

# Y motor — at end of Y ball screw (front, -Z)
my = make_box((-28, 2, -231), 56, 56, 56)
set_layer(my, LY_E)
label("NEMA23\nY-Motor", (0, 30, -203), LY_E)

# Z motor — at top of Z ball screw (top)
mz = make_box((-28, 420, -173), 56, 56, 56)
set_layer(mz, LY_E)
label("NEMA23\nZ-Motor", (0, 448, -145), LY_E)

# A motor — attached to rotary (left end)
ma = make_box((-136, 77, -28), 56, 56, 56)
set_layer(ma, LY_E)
label("NEMA23\nA-Motor", (-108, 105, 0), LY_E)

# ---------------------------------------------------------------------------
# F_Electronics — Control box, VFD, PSU
# ---------------------------------------------------------------------------
LY_F = "F_Electronics"

# Control box: 200 x 150 x 100, attached to back wall exterior
ctrl = make_box((-100, 200, -275), 200, 150, 100)
set_layer(ctrl, LY_F)
label("Control Box\n200x150x100", (0, 275, -225), LY_F)

# VFD: 100 x 150 x 80, next to control box
vfd = make_box((110, 200, -255), 100, 150, 80)
set_layer(vfd, LY_F)
label("VFD\n100x150x80", (160, 275, -215), LY_F)

# PSU: 120 x 60 x 40 (RSP-750-48), inside control box area
psu = make_box((-60, 210, -265), 120, 60, 40)
set_layer(psu, LY_F)
label("PSU RSP-750-48\n120x60x40", (0, 240, -245), LY_F)

# ---------------------------------------------------------------------------
# Final — Zoom to fit
# ---------------------------------------------------------------------------
rs.ZoomExtents()

print("=" * 60)
print("  CNC-M200 4-Axis Milling Machine model generated.")
print("  Layers: A_Frame / B_Linear / C_Spindle / D_Rotary /")
print("          E_Motors / F_Electronics")
print("=" * 60)
