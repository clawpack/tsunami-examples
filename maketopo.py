"""
Create topo and dtopo files needed for this example:
    etopo10min120W60W60S0S.asc        download from GeoClaw topo repository
    dtopo_usgs100227.tt3              create using Okada model 
Prior to Clawpack 5.2.1, the fault parameters we specified in a .cfg file,
but now they are explicit below.
    
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

# Scratch directory for storing topo and dtopo files:
scratch_dir = os.path.join(CLAW, 'geoclaw', 'scratch')

def get_topo(makeplots=False):
    """
    Retrieve the topo file from the GeoClaw repository.
    """
    from clawpack.geoclaw import topotools
    topo_fname = 'gebco_2020_n0.0_s-60.0_w-120.0_e-60.0.asc'
    #topo_fname = 'etopo10min120W60W60S0S.asc'
    #url = 'http://depts.washington.edu/clawpack/geoclaw/topo/etopo/' + topo_fname
    #clawpack.clawutil.data.get_remote_file(url, output_dir=scratch_dir, 
    #        file_name=topo_fname, verbose=True)

    if makeplots:
        from matplotlib import pyplot as plt
        topo = topotools.Topography(os.path.join(scratch_dir,topo_fname), topo_type=2)
        topo.plot()
        fname = os.path.splitext(topo_fname)[0] + '.png'
        plt.savefig(fname)
        print("Created ",fname)


def plot_subfaults_dZ(t, fig, fault, dtopo, xlower, xupper, ylower, yupper, xylim, dz_max):
    fig.clf()
    ax1 = fig.add_subplot(121)
    ax2 = fig.add_subplot(122)
    fault.plot_subfaults(axes=ax1, slip_color=True,
                        slip_time=t, xylim=xylim)
    dtopo.plot_dZ_colors(axes=ax2, t=t, cmax_dZ=dz_max)
    # ax1.plot(shoreline_xy[:,0],shoreline_xy[:,1],'g')
    # ax2.plot(shoreline_xy[:,0],shoreline_xy[:,1],'g')
    ax2.set_xlim(xlower,xupper)
    ax2.set_ylim(ylower,yupper)
    return fig

    
def make_dtopo(makeplots=False):
    """
    Create dtopo data file for deformation of sea floor due to earthquake.
    Uses the Okada model with fault parameters and mesh specified below.
    """
    from clawpack.geoclaw import dtopotools
    from matplotlib import pyplot as plt
    import numpy
    from get_dtopo_csv import get_csv

    param_fname = 'basic_inversion.param'
    csv_fname = 'chile2015.csv'
    get_csv('https://earthquake.usgs.gov/product/finite-fault/us20003k7a/us/1539809967421/' + param_fname, param_fname, csv_fname)

    dtopo_fname = os.path.join(scratch_dir, "dtopo_usgs100227.tt3")

    # Specify subfault parameters for this simple fault model consisting
    # of a single subfault:


    xlower = -73
    xupper = -70.5
    ylower = -33
    yupper = -29.5
    xylim = [xlower,xupper,ylower,yupper]

    """ [IGNORE - MANUAL SUBFAULT ENTRY]
        

        # dtopo parameters:
        points_per_degree = 60   # 1 minute resolution
        mx = int((xupper - xlower)*points_per_degree + 1)
        my = int((yupper - ylower)*points_per_degree + 1)
        x = numpy.linspace(xlower,xupper,mx)
        y = numpy.linspace(ylower,yupper,my)
        print ("dZ arrays will have shape %s by %s" % (len(y),len(x)))

        usgs_subfault = dtopotools.SubFault()
        usgs_subfault.strike = 16.
        usgs_subfault.length = 450.e3
        usgs_subfault.width = 100.e3
        usgs_subfault.depth = 35.e3
        usgs_subfault.slip = 15.
        usgs_subfault.rake = 104.
        usgs_subfault.dip = 14.
        usgs_subfault.longitude = -72.668
        usgs_subfault.latitude = -35.826
        usgs_subfault.coordinate_specification = "top center"

        fault = dtopotools.Fault()
        fault.subfaults = [usgs_subfault]

        print("Mw = ",fault.Mw())
    """

    subfault_fname = 'chile2015.csv'
    input_units = {
        'depth' : 'km',
        'slip' : 'cm', 
        'length' : 'km',
        'width' : 'km',
        'mu' : 'Pa'
    }
    fault = dtopotools.CSVFault()
    fault.read(subfault_fname,input_units=input_units, coordinate_specification='noaa sift')
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
        times = numpy.linspace(0,200,20)
        # times = [1.]

        fault.create_dtopography(x,y,times)
        dtopo = fault.dtopo
        dtopo.write(dtopo_fname, dtopo_type=3)
        dzmax =  abs(dtopo.dZ).max()
        print('dzmax={}'.format(dzmax))

        from clawpack.visclaw.JSAnimation import IPython_display
        import clawpack.visclaw.JSAnimation.JSAnimation_frametools as J
        plotdir = '_fault_slip_plots'
        J.make_plotdir(plotdir, clobber=True)
        fig = plt.figure(figsize=(12,5))

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


def get_gauge():
    gaugeinfo = []
    gaugeinfo.append([32412, 0.03])
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
