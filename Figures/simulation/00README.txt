ED vs MX geometry simulated refinement comparison
=================================================

Introduction
------------

Here, investigate differences in behaviour of geometry refinement for typical
electron diffraction geometry compared with X-ray MX. This has been done before,
for the CCP-EM Spring Symposium and for the PSI workshop. Now we are repeating
but using Max Clabbers' lysozyme dataset 1 as the start point. From the DIALS
processing of that, we take two files:

* ``static.pickle`` - 38.2 degree sweep of indexed reflections for a lysozyme
  electron diffraction dataset.
* ``static.json`` - the associated experimental geometry for the real
  ED experiment.

I want to produce regularised experimental geometries for both typical MX
geometry and ED geometry, and then produce indexed centroids for both
geometries by prediction and adding some noise.

Regularise input
----------------

The script ``regularise_experiments.py`` reads in ``static.json`` and
simplifies the geometry for the ED experiment as follows:

* Force beam direction along -Z axis.
* Create a new detector of the same overall size as the original Timepix
  detector, and at the same distance, but use a single panel instead of 4
  panels, and make it orthogonal to the beam, intersecting in the centre. We
  ignore thickness and material, so assume there is no parallax correction.
* Increase the scan range to a full turn. The simulation of new 'observations'
  from the updated geometry may cause reflections near the edges of the
  original scan to appear outside that scan range (particularly an issue for
  the conversion to MX geometry). During refinement, reflections outside the
  scan range will be discarded, so this ensures that all the original
  observations will be within the new scan range.

The updated geometry is then written to ``experiments_ED_regularised.json``.

Now a simple MX geometry is constructed:

* Change wavelength to 12 keV.
* Construct a single panel detector with dimensions of a Pilatus 6M at a
  distance of 200 mm, with the beam centre in the middle of the panel.

In either case, the rotation axis is not changed from its original direction,
which for ``static.json`` is slightly off from the Y axis
(-0.018138,-0.999803,0.008012). The reason to not regularise this to something
conventional such as (0, -1, 0) is that the crystal model orientation would
have to be changed so that the same reflections as contained in
``observed.pickle`` would be observed by rotation around the new axis. This way
is simpler and should still demonstrate the differences between MX and ED
refinement that I'm interested in.

Simulate observations
---------------------

The script ``create_indexed.py`` takes the original observations in
``static.pickle`` along with experimental descriptions in .json files to
generate new centroids for those observations. Here we run it like this::

  dials.python create_indexed.py static.pickle \
    experiments_ED_regularised.json experiments_MX_regularised.json

The output is as follows::

  Number of reflections loaded: 2106
  Simulating indexed observations for experiments_ED_regularised.json
  Simulating indexed observations for experiments_MX_regularised.json
  Selecting 1571 reflections common to each set
  Saving reflections to experiments_ED_regularised.pickle
  Saving reflections to experiments_MX_regularised.pickle

The two new files, ``experiments_ED_regularised.pickle`` and
``experiments_MX_regularised.pickle`` contain the simulated observations for
the 1571 common reflections that can be predicted in each case. Error has been
added to the predicted centroids to form observations. In either case the error
vector is the same in pixels/images, but this is scaled appropriately into
mm/rad for each experiment. The centroid variances from spot-finding are left
untouched for the centroids in pixels/images, but again these are scaled
appropriately for the centroids in mm/rad. Only reflections that can be
predicted with both geometries are written to the output files. This ensures
that refinement can be performed using the equivalent set of reflections in
each case, to help comparison.

Refinement
----------

Start with the electron diffraction geometry. Refine, with additional
diagnostics requested and the close_to_spindle cutoff and outlier rejection
both switched off so that the reflections used in refinement will be the
same in each case::

  dials.refine experiments_ED_regularised.json \
    experiments_ED_regularised.pickle \
    output.experiments=refined_ED.json \
    output.reflections=refined_ED.pickle \
    output.log=dials.refine.ED.log \
    output.history=history_ED.pickle \
    correlation_plot.filename=corrgram_ED.pdf \
    track_gradient=True \
    track_condition_number=True \
    close_to_spindle_cutoff=0 \
    outlier.algorithm=null

Now refine the MX case::

  dials.refine experiments_MX_regularised.json \
    experiments_MX_regularised.pickle \
    output.experiments=refined_MX.json \
    output.reflections=refined_MX.pickle \
    output.log=dials.refine.MX.log \
    output.history=history_MX.pickle \
    correlation_plot.filename=corrgram_MX.pdf \
    track_gradient=True \
    track_condition_number=True \
    close_to_spindle_cutoff=0 \
    outlier.algorithm=null

Print condition numbers in each case with this script::

  dials.python - <<EOF
  import cPickle as pickle
  with open('history_ED.pickle') as f:
    history_ED = pickle.load(f)
  with open('history_MX.pickle') as f:
    history_MX = pickle.load(f)
  K_ED = [str(e) for e in history_ED['condition_number']]
  K_MX = [str(e) for e in history_MX['condition_number']]
  print "Stepwise condition number for ED:"
  print "Step   K"
  for i, k in enumerate(K_ED):
    print i+1, k
  print "Stepwise condition number for MX:"
  print "Step   K"
  for i, k in enumerate(K_MX):
    print i+1, k
  EOF

Comparing the final steps in each case, the ED geometry has a condition number
of 851724.592042, while the MX geometry has only 2156.28337203

For the paper, want to generate corrgrams for Phi that exclude the detector
parameters. Use these refinement jobs::

  dials.refine experiments_ED_regularised.json \
    experiments_ED_regularised.pickle \
    output.experiments=junk.json \
    output.reflections=junk.pickle \
    output.log=junk.log \
    correlation_plot.filename=corrgram_ED_subset.pdf \
    col_select=6,7,8,9,10,11,12
    close_to_spindle_cutoff=0 \
    outlier.algorithm=null

  dials.refine experiments_MX_regularised.json \
    experiments_MX_regularised.pickle \
    output.experiments=junk.json \
    output.reflections=junk.pickle \
    output.log=junk.log \
    correlation_plot.filename=corrgram_MX_subset.pdf \
    col_select=6,7,8,9,10,11,12
    close_to_spindle_cutoff=0 \
    outlier.algorithm=null

Combine the resulting corrgram_ED_subset_Phi.pdf and corrgram_MX_subset_Phi.pdf
in one figure using Inkscape. Result: corrgrams_phi.svg

Also, check the condition number when the ED refinement has detector distance
and tilt and twist fixed, like in the real refinement done for dataset 1

  dials.refine experiments_ED_regularised.json \
    experiments_ED_regularised.pickle \
    output.experiments=junk.json \
    output.reflections=junk.pickle \
    output.log=junk.log \
    output.history=history_ED_constrained.pickle \
    detector.fix_list="Dist,Tau2,Tau3" \
    track_gradient=True \
    track_condition_number=True \
    close_to_spindle_cutoff=0 \
    outlier.algorithm=null
  dials.python - <<EOF
  import cPickle as pickle
  with open('history_ED_constrained.pickle') as f:
    history_ED = pickle.load(f)
  K_ED = [str(e) for e in history_ED['condition_number']]
  print "Stepwise condition number for ED:"
  print "Step   K"
  for i, k in enumerate(K_ED):
    print i+1, k
  EOF

Final step condition number is now 7604.02487169, so constraining the detector
parameters really helped to stabilise refinement.

Also look at condition numbers for each of the static refinement jobs done for
the real dataset processing::

  $ tail -n1 $(find . -name "static_condition_number.txt" | sort)
  ==> ./1/static_condition_number.txt <==
  11104.8817476
  ==> ./2/static_condition_number.txt <==
  9249.73060719
  ==> ./3/static_condition_number.txt <==
  20284.63499
  ==> ./4/static_condition_number.txt <==
  27234.788724
  ==> ./5/static_condition_number.txt <==
  27624.7028531
  ==> ./6/static_condition_number.txt <==
  10672.5128811
  ==> ./7/static_condition_number.txt <==
  22542.3157441
