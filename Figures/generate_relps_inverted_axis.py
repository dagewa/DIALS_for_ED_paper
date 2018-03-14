#!/usr/bin/env dials.python

from dials.algorithms.spot_prediction import RotationAngles
from dxtbx.model import Crystal, Beam
from cctbx import sgtbx
from math import pi
from scitbx import matrix

RAD2DEG = 180./pi

# Crystal
xl=Crystal(real_space_a=(0,10,0),
           real_space_b=(0,0,10),
           real_space_c=(10,0,0),
           space_group=sgtbx.space_group('P 1'))

# Spindle
axis = matrix.col((1,0,0))

# Rotate crystal by 12.039 degrees, which means the first relp is predicted
# at 15.0 degrees
R = axis.axis_and_angle_as_r3_rotation_matrix(-12.039,deg=True)
UB = R * matrix.sqr(xl.get_A())
xl.set_A(UB)

# Beam
beam = Beam(direction=(0,0,1), wavelength=1.0332)
s0 = matrix.col(beam.get_s0())
ewald_diam = 2.*s0.length()

# Reflections
hkl_list = [(1,0,0),
            (2,0,0),
            (3,0,0),
            (4,0,0),
            (5,0,0)]

# Predictions
ra = RotationAngles(s0, axis)
angles = []
for h in hkl_list:
  preds = ra(h, UB)
  angles.append([e * RAD2DEG for e in preds])

# Show the results
print
print "Ewald sphere radius = {0:.3f} A^-1".format(s0.length())
print "Ewald sphere diameter = {0:.3f} A^-1".format(2.*s0.length())
print
print "Predicted reflection angles"
print "(h, k, l)   d(A)  phi1   phi2"
print "==============================="
for h, ang in zip(hkl_list, angles):
  r = UB * matrix.col(h)
  d = 1./r.length()
  print str(h) + "   {0:<5.2f} {1:<6.3f} {2:<6.3f}".format(d, ang[0], ang[1])
print

# Now set up to draw the figure.
from matplotlib import patches
import matplotlib.transforms as transforms
import matplotlib.pyplot as plt
col_width = 8.8 / 2.54 # Acta D column width is 8.8 cm
fig = plt.figure(figsize=(col_width, col_width))
plt.rc('font', family='serif')
# https://github.com/matplotlib/matplotlib/issues/8702/
plt.rcParams['mathtext.fontset'] = 'dejavuserif'


# Create axes as large as the figure and set appropriate data limits
ax = fig.add_axes([0.0, 0.0, 1.0, 1.0], frameon=False, aspect=1)
ax.set_xlim(-0.5,0.3)
ax.set_ylim(-0.00,0.8)

# Do not show tickmarks
ax.get_xaxis().set_visible(False)
ax.get_yaxis().set_visible(False)

# Align the figure plane fX, fY such that fX is along lab -Z (i.e. along the
# beam direction) and fY is along lab Y
fX = matrix.col((0,0,-1))
fY = matrix.col((0,1,0))

# Get the centre of the data coords (lab frame origin) in figure coords
#labCentre = ax.transData.transform((0,0))

# Angular range of arcs to be drawn, in degrees
arc_start = 0
arc_end = 35

# Calculate the Ewald sphere centre in data coordinates
ewald_centre = (-1.*s0).dot(fX), (-1.*s0).dot(fY)

# Add initial Ewald sphere for debugging
#e1 = patches.Arc(ewald_centre, ewald_diam, ewald_diam, theta1=0, theta2=359)
#ax.add_patch(e1)

# Loop over the smaller of the two predicted angles
angles, _ = zip(*angles)
for ang in angles:

  # Rotate beam
  rot_s0 = s0.rotate_around_origin(axis, -1.*ang, deg=True)

  # Create an arc
  arc = patches.Arc(ewald_centre, width=ewald_diam, height=ewald_diam,
      theta1=arc_start, theta2=arc_end)

  # Rotate the arc around the spindle
  tr = transforms.Affine2D().rotate_deg_around(0,0, -1.*ang)
  arc.set_transform(tr + ax.transData)

  # Add to the axes
  ax.add_patch(arc)

# Add relps and text labels
for i, h in enumerate(hkl_list):
  r = UB * matrix.col(h)
  x, y = r.dot(fX), r.dot(fY)
  circle = patches.Circle((x,y), 0.01, alpha=1.0, fc='black')
  ax.add_patch(circle)

  ax.text(x+0.05, y -0.01, r"$h={0}$".format(i+1))

# Now loop over angles assuming inverted rotation axis
for ang in angles:

  # Rotate beam
  rot_s0 = s0.rotate_around_origin(axis, ang, deg=True)

  # Create an arc
  arc = patches.Arc(ewald_centre, width=ewald_diam, height=ewald_diam,
      theta1=arc_start, theta2=arc_end)

  # Rotate the arc around the spindle
  tr = transforms.Affine2D().rotate_deg_around(0,0, ang)
  arc.set_transform(tr + ax.transData)

  # Add to the axes
  ax.add_patch(arc)

# Add relps, rotated onto the Ewald sphere with an inverted rotation axis
for h, ang in zip(hkl_list, angles):
  r = UB * matrix.col(h)
  x, y = r.dot(fX), r.dot(fY)
  circle = patches.Circle((x,y), 0.01, alpha=0.5)

  # Rotate around the spindle. Need to rotate *twice* - once takes the straight
  # line of relps and puts them onto the curved surface of the Ewald sphere
  # at phi=0, the second rotation puts them individually onto the family of
  # Ewald spheres at their positions assuming the inverted rotation axis
  tr = transforms.Affine2D().rotate_deg_around(0, 0, 2.*ang)
  circle.set_transform(tr + ax.transData)

  ax.add_patch(circle)

#####################

# Create an electron diffraction beam to add to the figure
beam = Beam(direction=(0,0,1), wavelength=0.0250793)
s0 = matrix.col(beam.get_s0())
ewald_diam = 2.*s0.length()

# Predictions
ra = RotationAngles(s0, axis)
angles = []
for h in hkl_list:
  preds = ra(h, UB)
  angles.append([e * RAD2DEG for e in preds])

# Show the results
print
print "Ewald sphere radius = {0:.3f} A^-1".format(s0.length())
print "Ewald sphere diameter = {0:.3f} A^-1".format(2.*s0.length())
print
print "Predicted reflection angles"
print "(h, k, l)   d(A)  phi1   phi2"
print "==============================="
for h, ang in zip(hkl_list, angles):
  r = UB * matrix.col(h)
  d = 1./r.length()
  print str(h) + "   {0:<5.2f} {1:<6.3f} {2:<6.3f}".format(d, ang[0], ang[1])
print

# Angular range of arcs to be drawn, in degrees
arc_start = 0
arc_end = 0.85

# Calculate the Ewald sphere centre in data coordinates
ewald_centre = (-1.*s0).dot(fX), (-1.*s0).dot(fY)

# Add initial Ewald sphere for debugging
#e1 = patches.Arc(ewald_centre, ewald_diam, ewald_diam, theta1=0, theta2=0.5, ec='red')
#ax.add_patch(e1)

# For clarity just show the Ewald sphere at +ve and -ve angle for the third
# reflection, as they are all at nearly the same angle
angles, _ = zip(*angles)

# Correct axis
for ang in (angles[2],):

  # Rotate beam
  rot_s0 = s0.rotate_around_origin(axis, -1.*ang, deg=True)

  # Create an arc
  arc = patches.Arc(ewald_centre, width=ewald_diam, height=ewald_diam,
      theta1=arc_start, theta2=arc_end)

  # Rotate the arc around the spindle
  tr = transforms.Affine2D().rotate_deg_around(0, 0, -1.*ang)
  arc.set_transform(tr + ax.transData)

  # Add to the axes
  ax.add_patch(arc)

# Inverted axis
for ang in (angles[2],):

  # Rotate beam
  rot_s0 = s0.rotate_around_origin(axis, ang, deg=True)

  # Create an arc
  arc = patches.Arc(ewald_centre, width=ewald_diam, height=ewald_diam,
      theta1=arc_start, theta2=arc_end)

  # Rotate the arc around the spindle
  tr = transforms.Affine2D().rotate_deg_around(0, 0, ang)
  arc.set_transform(tr + ax.transData)

  # Add to the axes
  ax.add_patch(arc)

# Add relps, rotated onto the Ewald sphere with an inverted rotation axis
for h, ang in zip(hkl_list, angles):
  r = UB * matrix.col(h)
  x, y = r.dot(fX), r.dot(fY)
  circle = patches.Circle((x,y), 0.01, alpha=0.5, fc='green')

  # Rotate around the spindle. Need to rotate *twice* - once takes the straight
  # line of relps and puts them onto the curved surface of the Ewald sphere
  # at phi=0, the second rotation puts them individually onto the family of
  # Ewald spheres at their positions assuming the inverted rotation axis
  tr = transforms.Affine2D().rotate_deg_around(0, 0, 2.*ang)
  circle.set_transform(tr + ax.transData)

  ax.add_patch(circle)

# Create a custom legend
#legend_elements = [
#    patches.Circle((0,0), 0.01, alpha=1.0, fc='black', label='correct rotation'),
#    patches.Circle((0,0), 0.01, alpha=0.5, label='inverted rotation, MX'),
#    patches.Circle((0,0), 0.01, alpha=0.5, fc='green', label='inverted rotation, ED')]
#ax.legend(handles=legend_elements, loc='upper center', frameon=False)

x, y = (-0.4,0.75)
circle1 = patches.Circle((x,y), 0.01, alpha=1.0, fc='black')
ax.add_patch(circle1)
ax.text(x+0.03, y -0.01, "correct rotation")

x, y = (-0.4,0.7)
circle3 = patches.Circle((x,y), 0.01, alpha=0.5, fc='green')
ax.add_patch(circle3)
ax.text(x+0.03, y -0.01, "inverse rotation, MX")

x, y = (-0.4,0.65)
circle2 = patches.Circle((x,y), 0.01, alpha=0.5)
ax.add_patch(circle2)
ax.text(x+0.03, y -0.01, "inverse rotation, ED")

fig.savefig('relps_inverted_axis.pdf')
plt.show()
