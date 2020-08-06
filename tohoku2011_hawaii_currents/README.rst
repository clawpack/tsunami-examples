
.. _tsunami-examples_tohoku2011_hawaii_currents:

Tohoku tsunami and comparison with gauge data in Hawaii
==============================================================

This example is set up to replicate some of the results from 
`this paper <http://dx.doi.org/10.1007/s00024-014-0980-y>`__::

    M. Arcos and R. J. LeVeque, Validating Velocities in the GeoClaw Tsunami 
    Model using Observations Near Hawaii from the 2011 Tohoku Tsunami, 
    Pure and Applied Geophysics, 2015.  DOI 10.1007/s00024-014-0980-y

For more details see the Jupyter notebook `compare_results.ipynb`.

This example uses the dtopo file `fujii.txydz`, which is downloaded from the 
script `maketopo.py`.  This can be run via::

    make topo

at the command line, which also downloads a topo file for the ocean bathymetry.
This bathymetry originally came from the NOAA National Geophysical Data
Center (NGDC), now NCEI (see `Sources of tsunami data
<http://www.clawpack.org/tsunamidata.html>`__).

To run the code and produce plots::

    make .plots

This produces plots of the surface and velocity at two gauges 1123 and 5680.
These gauges are at locations corresponding to the ADCP gauge HAI1123 (an
acoustic Doppler current profiler that was in place to record currents) and
the tide gauge in the Kahului Harbor.

To better view the gauge results and also plot comparisons with observations
at these gauges, run the Jupyter notebook `compare_results.ipynb`.

**A rendered version of the Jupyter notebook** for this example (with output
and plots) can be viewed from the `Clawpack gallery version of this file.
<http://www.clawpack.org/gallery/_static/??/README.html>`__

Note that `setrun.py` has::

    amrdata.amr_levels_max = 5

so that the code runs quickly (about 15 minutes of CPU time on a MacBook Pro).
Setting this to 6 gives another level refined by an additional factor 30
around Kahului Harbor, which agrees with the resolution used in the
original paper.  Running this way takes about 2 hours of CPU time.

Version
-------

- Developed using v5.7.0 in July, 2020.

