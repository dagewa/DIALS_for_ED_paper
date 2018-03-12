Figure showing the effect of varying spotfinding settings. Image
frame_value_438.cbf from dataset 1 is a good one as it shows a clear row of
spots that are not picked up by default settings, but are when the settings
listed in find_spots.phil are applied. Procedure used to produce the raw images
for the figure:

Ensure the format class is present:

  curl -o ~/.dxtbx/FormatCBFMiniTimepix.py https://raw.githubusercontent.com/dials/dxtbx_ED_formats/907d18cc6f8037056f9b1a202e30830852adc033/FormatCBFMiniTimepix.py

Import the dataset using site.phil, in order to get the beam centre correct:

  dials.import dataset_1_frame_value_438.cbf site.phil

Open the image viewer:

  dials.image_viewer datablock.json

Default brightness of 100 seems appropriate. Screenshot whole image at zoom
level of 50%.

Zoom to 400% in lower right region of upper left quad along the line of spots.
Screenshot region of interest while in "image" mode.

Change to "threshold" mode and screenshot again.

Set gain=0.833, sigma_strong=1 and global_threshold=1 as per find_spots.phil.
Screenshot the threshold image again.

Manually edit screenshots in Gimp to remove window decorations etc. This
resulted in the files whole_image.png, roi.png, roi_threshold.png and
roi_threshold_find_spots.png.

Assembled the images in inkscape.
