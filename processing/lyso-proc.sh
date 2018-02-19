#!/bin/bash

# DIALS processing script for Max Clabbers' lysozyme ED data, consisting of
# images converted to CBF files. Run by passing in a dials.import template on
# the command line:
#
#   ./lyso-proc.sh /path/to/frame_value_###.cbf
#
# Prerequisites:
# * DIALS version 1.dev.2046-g8c6ed7a or newer
# * CCP4 7.0.051 or newer (for pointless and aimless)
# * Source CCP4 environment first, then DIALS to get the right version of
#   DIALS in the path
# * FormatCBFMiniTimepix.py placed in the directory ~/.dxtbx (this script will
#   download the expected version if the file doesn't exist)

if [ $# -ne 1 ]; then
    echo usage: $0 /path/to/frame_value_###.cbf
    exit 1
fi

TEMPLATE=$1

# Download the format class if needed
if [ ! -f ~/.dxtbx/FormatCBFMiniTimepix.py ]; then
  mkdir -p ~/.dxtbx
  curl -o ~/.dxtbx/FormatCBFMiniTimepix.py https://raw.githubusercontent.com/dials/dxtbx_ED_formats/907d18cc6f8037056f9b1a202e30830852adc033/FormatCBFMiniTimepix.py
fi

# Geometry overrides for import
cat << EOF >site.phil
geometry.scan.oscillation=0,0.076
geometry.goniometer.axes=-0.018138,-0.999803,0.008012
geometry.detector.hierarchy{
  fast_axis=1,0,0
  slow_axis=0,-1,0
  origin=-26.3525,30.535,-1890
}
EOF

# Mask definition to avoid picking up noise along a panel edge
cat <<EOF >mask.phil
untrusted {
  panel = 2
  rectangle = 500 515 0 98
}
untrusted {
  rectangle = 504 514 438 515
}
EOF

# Spot finding settings - DIALS nightly needed for dispersion scope
cat <<EOF >find_spots.phil
spotfinder {
  threshold {
    dispersion {
      gain = 0.833
      sigma_strong = 1
      global_threshold = 1
    }
  }
}
EOF

# Fix detector distance, tilt and twist rotations
cat <<EOF >refine.phil
refinement {
  parameterisation {
    detector {
      fix_list = "Dist,Tau2,Tau3"
    }
  }
}
EOF

# Initial import, set geometry overrides to get beam centre and rotation axis
# approximately right. Set a mask (originally determined interactively using
# the image viewer), find spots and get the right indexing solution
dials.import template=$TEMPLATE site.phil
dials.generate_mask mask.phil datablock.json
dials.import template=$TEMPLATE site.phil mask=mask.pickle
dials.find_spots nproc=8 min_spot_size=6 filter.d_min=2.5 filter.d_max=20 \
  datablock.json find_spots.phil
dials.index datablock.json strong.pickle refine.phil
dials.refine_bravais_settings indexed.pickle experiments.json refine.phil
dials.refine bravais_setting_5.json indexed.pickle refine.phil

# Re-import using the refined geometry. Still need to set the oscillation as
# this is not taken from the reference. Index again and refine the correct
# solution
dials.import template=$TEMPLATE mask=mask.pickle \
  reference_geometry=refined_experiments.json geometry.scan.oscillation=0,0.076
dials.index datablock.json strong.pickle refine.phil
dials.refine_bravais_settings indexed.pickle experiments.json refine.phil
dials.refine bravais_setting_5.json indexed.pickle refine.phil \
  output.experiments=static.json output.reflections=static.pickle

# Scan-varying refinement of the beam and crystal parameters with the detector
# fixed at the geometry of the static refinement run. Integration results are
# apparently better with default smoothness of the refinement rather than
# allowing the beam and crystal to vary more sharply
#FIXME - currently compose_model_per=image does not work correctly
#dials.refine static.json static.pickle scan_varying=True \
#  compose_model_per=image \
#  detector.fix=all \
#  beam.fix="all in_spindle_plane out_spindle_plane *wavelength" \
#  beam.force_static=False \
#  output.experiments=varying.json \
#  output.reflections=varying.pickle
#FIXME - use default compose_model_per=block instead
dials.refine static.json static.pickle scan_varying=True \
  detector.fix=all \
  beam.fix="all in_spindle_plane out_spindle_plane *wavelength" \
  beam.force_static=False \
  output.experiments=varying.json \
  output.reflections=varying.pickle

# Integrate and export MTZ
dials.integrate varying.json varying.pickle nproc=8
dials.export integrated_experiments.json integrated.pickle

# Scale
pointless hklin integrated.mtz hklout sorted.mtz > pointless.log
aimless hklin sorted.mtz \
  hklout scaled.mtz > aimless.log <<+
resolution 20.0 to 2.0
+
