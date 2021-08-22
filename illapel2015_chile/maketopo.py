"""
Script for downloading gauge and topography data, and generating differential topography data
Call functions with makeplots==True to create plots of topo, slip, and dtopo.
"""

from __future__ import absolute_import
from __future__ import print_function
import os

import clawpack.clawutil.data

try:
    CLAW = os.environ['CLAW']
except:
    raise Exception("*** Must first set CLAW enviornment variable")

scratch_dir = os.path.join(CLAW, 'geoclaw', 'scratch')

def get_topo(makeplots=False):
    """
    Retrieve the topo file from the GeoClaw repository.
    """
    from clawpack.geoclaw import topotools
    # download 10 arc-minute topography data in region around Chile
    topo_fname = 'etopo10min120W60W60S0S.asc'
    url = 'http://depts.washington.edu/clawpack/geoclaw/topo/etopo/' + topo_fname
    clawpack.clawutil.data.get_remote_file(url, output_dir=scratch_dir, file_name=topo_fname, verbose=True)

    if makeplots:
        from matplotlib import pyplot as plt
        topo = topotools.Topography(os.path.join(scratch_dir,topo_fname), topo_type=2)
        topo.plot()
        fname = os.path.splitext(topo_fname)[0] + '.png'
        plt.savefig(fname)
        print("Created ",fname)

# generate side-by-side fault slip and seafloor deformation contour plots
def plot_subfaults_dZ(t, fig, fault, dtopo, xlower, xupper, ylower, yupper, xylim, dz_max):
    fig.clf()
    ax1 = fig.add_subplot(121)
    ax2 = fig.add_subplot(122)
    fault.plot_subfaults(axes=ax1, slip_color=True,
                        slip_time=t, xylim=xylim)
    dtopo.plot_dZ_colors(axes=ax2, t=t, cmax_dZ=dz_max)
    ax2.set_xlim(xlower,xupper)
    ax2.set_ylim(ylower,yupper)
    return fig

# create dtopo file from finite fault data    
def make_dtopo(makeplots=False):
    from clawpack.geoclaw import dtopotools
    from matplotlib import pyplot as plt
    import numpy
    from get_dtopo_csv import get_csv

    # specify the URL for the USGS finite fault data file and properly format into a CSV file
    param_fname = 'basic_inversion.param'
    csv_fname = 'chile2015.csv'
    get_csv('https://earthquake.usgs.gov/product/finite-fault/us20003k7a/us/1539809967421/' + param_fname, param_fname, csv_fname)

    dtopo_fname = os.path.join(scratch_dir, "dtopo_usgs150916.tt3")

    # manually specify the bounds for the fault model (leave unchanged)
    xlower = -73
    xupper = -70.5
    ylower = -33
    yupper = -29.5
    xylim = [xlower,xupper,ylower,yupper]

    input_units = {
        'depth' : 'km',
        'slip' : 'cm', 
        'length' : 'km',
        'width' : 'km',
        'mu' : 'Pa'
    }

    fault = dtopotools.CSVFault()
    fault.read(csv_fname,input_units=input_units, coordinate_specification='noaa sift')
    fault.rupture_type = 'dynamic'

    print ("%s subfaults read in " % len(fault.subfaults))

    if os.path.exists(dtopo_fname):
        print("*** Not regenerating dtopo file (already exists): %s" \
                    % dtopo_fname)
    else:
        print("Using Okada model to create dtopo file")
        points_per_degree = 60
        mx = int((xupper - xlower)*points_per_degree + 1)
        my = int((yupper - ylower)*points_per_degree + 1)
        x = numpy.linspace(xlower, xupper, mx)
        y = numpy.linspace(ylower, yupper, my)
        
        # list of the times (in seconds) when the dtopo data is captured
        # here, `times` consists of the interval [0,200] divided evenly into 20 markers (0 and 200 included)
        # note: ensure that the maximum value in `times` exceeds the maximum rupture time of any subfault
        times = numpy.linspace(0,200,20)

        # create and write dtopo file
        fault.create_dtopography(x,y,times)
        dtopo = fault.dtopo
        dtopo.write(dtopo_fname, dtopo_type=3)

        import clawpack.visclaw.JSAnimation.JSAnimation_frametools as J
        plotdir = '_fault_slip_plots'
        J.make_plotdir(plotdir, clobber=True)
        fig = plt.figure(figsize=(12,5))
        dzmax = abs(dtopo.dZ).max()

        # generate fault slip and deformation plots
        for k,t in enumerate(times):
            plot_subfaults_dZ(t,fig, fault, dtopo, xlower, xupper, ylower, yupper, xylim, dzmax)
            J.save_frame(k, plotdir = plotdir, verbose=True)

    if makeplots:
        if fault.dtopo is None:
            # read in the pre-existing file:
            print("Reading in dtopo file...")
            dtopo = dtopotools.DTopography()
            dtopo.read(dtopo_fname, dtopo_type=3)
            x = dtopo.x
            y = dtopo.y
        plt.figure(figsize=(12,7))
        ax1 = plt.subplot(121)
        ax2 = plt.subplot(122)
        fault.plot_subfaults(axes=ax1,slip_color=True)
        ax1.set_xlim(x.min(),x.max())
        ax1.set_ylim(y.min(),y.max())
        dtopo.plot_dZ_colors(1.,axes=ax2)
        fname = os.path.splitext(os.path.split(dtopo_fname)[-1])[0] + '.png'
        plt.savefig(fname)
        print("Created ",fname)

# grabs gauge data from NOAA and formats it
def get_gauge():
    # find more gauge numbers here: https://www.ngdc.noaa.gov/hazard/dart/2015chile.html
    gaugeinfo = []
    # gaugeinfo.append([gauge_no, offset]) where `offset` is the nonzero equilibrium in the data
    gaugeinfo.append([32412, -0.03])
    gaugeinfo.append([32402, 0.00])

    for gaugeno, offset in gaugeinfo:
        url = 'https://www.ngdc.noaa.gov/hazard/data/DART/20150916_chile/dart{}_20150915to20150921_meter.txt'.format(gaugeno)
        clawpack.clawutil.data.get_remote_file(url, output_dir='.', file_name='dart{}.txt'.format(gaugeno), verbose=True)

    from format_gauge import format_gauges_chile2015
    format_gauges_chile2015(gaugeinfo)

if __name__=='__main__':
    get_topo(False)
    make_dtopo(False)
    get_gauge()