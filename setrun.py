"""
Module to set up run time parameters for Clawpack.

The values set in the function setrun are then written out to data files
that will be read in by the Fortran code.

"""

import os

import numpy

import clawpack.geoclaw.topotools as topotools

#------------------------------
def setrun(claw_pkg='geoclaw'):
#------------------------------

    """
    Define the parameters used for running Clawpack.

    INPUT:
        claw_pkg expected to be "geoclaw" for this setrun.

    OUTPUT:
        rundata - object of class ClawRunData

    """

    import clawpack.clawutil.data as clawdata

    assert claw_pkg.lower() == 'geoclaw',  "Expected claw_pkg = 'geoclaw'"

    num_dim = 2
    rundata = clawdata.ClawRunData(claw_pkg, num_dim)

    #------------------------------------------------------------------
    # Standard Clawpack parameters to be written to claw.data:
    #   (or to amr2ez.data for AMR)
    #------------------------------------------------------------------
    clawdata = rundata.clawdata  # initialized when rundata instantiated


    # Set single grid parameters first.
    # See below for AMR parameters.


    # ---------------
    # Spatial domain:
    # ---------------

    # Number of space dimensions:
    clawdata.num_dim = num_dim

    # Lower and upper edge of computational domain:
    clawdata.lower[0] = -100.e3
    clawdata.upper[0] = 100.e3

    clawdata.lower[1] = -100.e3
    clawdata.upper[1] = 100.e3
    # clawdata.lower[0] = -1.0
    # clawdata.upper[0] = 1.0

    # clawdata.lower[1] = -1.0
    # clawdata.upper[1] = 1.0


    # Number of grid cells: Coarsest grid
    clawdata.num_cells[0] = 100
    clawdata.num_cells[1] = 5


    # ---------------
    # Size of system:
    # ---------------

    # Number of equations in the system:
    clawdata.num_eqn = 3

    # Number of auxiliary variables in the aux array (initialized in setaux)
    clawdata.num_aux = 5

    # Index of aux array corresponding to capacity function, if there is one:
    clawdata.capa_index = 0

    
    
    # -------------
    # Initial time:
    # -------------

    clawdata.t0 = 0.0


    # Restart from checkpoint file of a previous run?
    # Note: If restarting, you must also change the Makefile to set:
    #    RESTART = True
    # If restarting, t0 above should be from original run, and the
    # restart_file 'fort.chkNNNNN' specified below should be in 
    # the OUTDIR indicated in Makefile.

    clawdata.restart = False               # True to restart from prior results
    clawdata.restart_file = 'fort.chk00006'  # File to use for restart data

    # -------------
    # Output times:
    #--------------

    # Specify at what times the results should be written to fort.q files.
    # Note that the time integration stops after the final output time.
    # The solution at initial time t0 is always written in addition.

    clawdata.output_style = 3
    clawdata.tfinal = 1e10

    if clawdata.output_style == 1:
        short_time = False
        if short_time:
            days = 1
            # Output nout frames at equally spaced times up to tfinal:
            clawdata.num_output_times = int(days) * 24 * 6
        else:
            days = 12
            clawdata.num_output_times = int(days) * 2
        clawdata.tfinal = float(days) * 24.0 * 60.0**2
        clawdata.output_t0 = True  # output at initial (or restart) time?

    elif clawdata.output_style == 2:
        # Specify a list of output times.
        clawdata.output_times = [0.5, 1.0]

    elif clawdata.output_style == 3:
        # Output every iout timesteps with a total of ntot time steps:
        clawdata.output_step_interval = 1
        clawdata.total_steps = 100
        clawdata.output_t0 = True
        

    clawdata.output_format = 'ascii'      # 'ascii' or 'netcdf' 

    clawdata.output_q_components = 'all'   # could be list such as [True,True]
    clawdata.output_aux_components = 'none'  # could be list
    clawdata.output_aux_onlyonce = True    # output aux arrays only at t0



    # ---------------------------------------------------
    # Verbosity of messages to screen during integration:
    # ---------------------------------------------------

    # The current t, dt, and cfl will be printed every time step
    # at AMR levels <= verbosity.  Set verbosity = 0 for no printing.
    #   (E.g. verbosity == 2 means print only on levels 1 and 2.)
    clawdata.verbosity = 2



    # --------------
    # Time stepping:
    # --------------

    # if dt_variable==1: variable time steps used based on cfl_desired,
    # if dt_variable==0: fixed time steps dt = dt_initial will always be used.
    clawdata.dt_variable = True

    # Initial time step for variable dt.
    # If dt_variable==0 then dt=dt_initial for all steps:
    clawdata.dt_initial = 50.0

    # Max time step to be allowed if variable dt used:
    clawdata.dt_max = 1e+99

    # Desired Courant number if variable dt used, and max to allow without
    # retaking step with a smaller dt:
    # clawdata.cfl_desired = 0.8
    # clawdata.cfl_max = 1.0
    clawdata.cfl_desired = 0.4
    clawdata.cfl_max = 0.5

    # Maximum number of time steps to allow between output times:
    clawdata.steps_max = 500000




    # ------------------
    # Method to be used:
    # ------------------
    # (order, transverse_waves, cfl_max, rpt)
    # 
    # working    = (1, 0, 0.5, geo), (1, 1, 0.5, geo), (1, 1, 1.0, min)
    # suspicious = (2, 1, 0.5, geo), (2, 1, 0.5, min)
    # not        = (2, 2, 0.5, geo), (2, 0, 1.0, geo), (2, 0, 0.5, geo),
    #              (2, 1, 1.0, geo), (2, 0, 1.0, min), (2, 1, 1.0, geo)

    # Order of accuracy:  1 => Godunov,  2 => Lax-Wendroff plus limiters
    clawdata.order = 1
    
    # Use dimensional splitting? (not yet available for AMR)
    clawdata.dimensional_split = 'unsplit'
    
    # For unsplit method, transverse_waves can be 
    #  0 or 'none'      ==> donor cell (only normal solver used)
    #  1 or 'increment' ==> corner transport of waves
    #  2 or 'all'       ==> corner transport of 2nd order corrections too
    clawdata.transverse_waves = 0

    # Number of waves in the Riemann solution:
    clawdata.num_waves = 3
    
    # List of limiters to use for each wave family:  
    # Required:  len(limiter) == num_waves
    # Some options:
    #   0 or 'none'     ==> no limiter (Lax-Wendroff)
    #   1 or 'minmod'   ==> minmod
    #   2 or 'superbee' ==> superbee
    #   3 or 'mc'       ==> MC limiter
    #   4 or 'vanleer'  ==> van Leer
    # clawdata.limiter = ['mc', 'mc', 'mc']
    clawdata.limiter = ['none','none','none']

    clawdata.use_fwaves = True    # True ==> use f-wave version of algorithms
    
    # Source terms splitting:
    #   src_split == 0 or 'none'    ==> no source term (src routine never called)
    #   src_split == 1 or 'godunov' ==> Godunov (1st order) splitting used, 
    #   src_split == 2 or 'strang'  ==> Strang (2nd order) splitting used,  not recommended.
    clawdata.source_split = 'none'


    # --------------------
    # Boundary conditions:
    # --------------------

    # Number of ghost cells (usually 2)
    clawdata.num_ghost = 2

    # Choice of BCs at xlower and xupper:
    #   0 => user specified (must modify bcN.f to use this option)
    #   1 => extrapolation (non-reflecting outflow)
    #   2 => periodic (must specify this at both boundaries)
    #   3 => solid wall for systems where q(2) is normal velocity

    clawdata.bc_lower[0] = 'wall'
    clawdata.bc_upper[0] = 'wall'

    clawdata.bc_lower[1] = 'wall'
    clawdata.bc_upper[1] = 'wall'
    # clawdata.bc_lower[0] = 'periodic'
    # clawdata.bc_upper[0] = 'periodic'

    # clawdata.bc_lower[1] = 'periodic'
    # clawdata.bc_upper[1] = 'periodic'

    # Specify when checkpoint files should be created that can be
    # used to restart a computation.

    clawdata.checkpt_style = 0

    if clawdata.checkpt_style == 0:
        # Do not checkpoint at all
        pass

    elif clawdata.checkpt_style == 1:
        # Checkpoint only at tfinal.
        pass

    elif clawdata.checkpt_style == 2:
        # Specify a list of checkpoint times.  
        clawdata.checkpt_times = [0.1,0.15]

    elif clawdata.checkpt_style == 3:
        # Checkpoint every checkpt_interval timesteps (on Level 1)
        # and at the final time.
        clawdata.checkpt_interval = 5


    # ---------------
    # AMR parameters:
    # ---------------
    amrdata = rundata.amrdata

    # max number of refinement levels:
    amrdata.amr_levels_max = 1

    # List of refinement ratios at each level (length at least mxnest-1)
    amrdata.refinement_ratios_x = [2,4,4]
    amrdata.refinement_ratios_y = [2,4,4]
    amrdata.refinement_ratios_t = [2,4,4]

    # Specify type of each aux variable in amrdata.auxtype.
    # This must be a list of length maux, each element of which is one of:
    #   'center',  'capacity', 'xleft', or 'yleft'  (see documentation).

    amrdata.aux_type = ['center','center','yleft','center','center']


    # Flag using refinement routine flag2refine rather than richardson error
    amrdata.flag_richardson = False    # use Richardson?
    amrdata.flag2refine = True

    # steps to take on each level L between regriddings of level L+1:
    amrdata.regrid_interval = 3

    # width of buffer zone around flagged points:
    # (typically the same as regrid_interval so waves don't escape):
    amrdata.regrid_buffer_width  = 2

    # clustering alg. cutoff for (# flagged pts) / (total # of cells refined)
    # (closer to 1.0 => more small grids may be needed to cover flagged cells)
    amrdata.clustering_cutoff = 0.700000

    # print info about each regridding up to this level:
    amrdata.verbosity_regrid = 0  


    #  ----- For developers ----- 
    # Toggle debugging print statements:
    amrdata.dprint = False      # print domain flags
    amrdata.eprint = False      # print err est flags
    amrdata.edebug = False      # even more err est flags
    amrdata.gprint = False      # grid bisection/clustering
    amrdata.nprint = False      # proper nesting output
    amrdata.pprint = False      # proj. of tagged points
    amrdata.rprint = False      # print regridding summary
    amrdata.sprint = False      # space/memory output
    amrdata.tprint = False      # time step reporting each level
    amrdata.uprint = False      # update/upbnd reporting
    
    # More AMR parameters can be set -- see the defaults in pyclaw/data.py

    # == setregions.data values ==
    regions = rundata.regiondata.regions
    # to specify regions of refinement append lines of the form
    #  [minlevel,maxlevel,t1,t2,x1,x2,y1,y2]
    # regions.append([1, 1, 0., 1.e10, -100.,100., -100.,100.])
    # regions.append([1, 2, 0., 1.e10,    0.,100.,    0.,100.])
    # regions.append([2, 3, 3., 1.e10,   52., 72.,   52., 72.])
    # regions.append([2, 3, 3., 1.e10,   75., 95.,   -10.,  10.])
    # regions.append([2, 4, 3.4, 1.e10,   57., 68.,   57., 68.])
    # regions.append([2, 4, 3.4, 1.e10,   83., 92.,   -4.,  4.])

    # == setgauges.data values ==
    # for gauges append lines of the form  [gaugeno, x, y, t1, t2]
    # rundata.gaugedata.add_gauge()
    rundata.gaugedata.gauges.append([1,0.0,0.0,0.0,rundata.clawdata.tfinal])
    rundata.gaugedata.gauges.append([2,50359.3,72874.5,0.0,rundata.clawdata.tfinal])
    rundata.gaugedata.gauges.append([3,-50359.3,-72874.5,0.0,rundata.clawdata.tfinal])

    #------------------------------------------------------------------
    # GeoClaw specific parameters:
    #------------------------------------------------------------------
    rundata = setgeo(rundata)

    return rundata
    # end of function setrun
    # ----------------------


#-------------------
def setgeo(rundata):
#-------------------
    """
    Set GeoClaw specific runtime parameters.
    For documentation see ....
    """

    try:
        geo_data = rundata.geo_data
    except:
        print "*** Error, this rundata has no geo_data attribute"
        raise AttributeError("Missing geo_data attribute")
       
    # == Physics ==
    geo_data.gravity = 9.81
    geo_data.coordinate_system = 1
    geo_data.earth_radius = 6367.5e3

    # == Forcing Options
    geo_data.coriolis_forcing = False

    # == Algorithm and Initial Conditions ==
    geo_data.sea_level = 0.0
    geo_data.dry_tolerance = 1.e-3
    geo_data.friction_forcing = False
    geo_data.manning_coefficient = 0.025
    geo_data.friction_depth = 300e3

    # Refinement parameters
    refinement_data = rundata.refinement_data
    refinement_data.variable_dt_refinement_ratios = True
    refinement_data.wave_tolerance = 1.e-2
    refinement_data.deep_depth = 1e2
    refinement_data.max_level_deep = 3

    # == settopo.data values ==
    topo_data = rundata.topo_data
    topo_data.topofiles = []

    # Jump Bathymetry
    # topo_data.test_topography = 1
    # topo_data.topo_location = 0.0
    # topo_data.topo_left = -100.0
    # topo_data.topo_right = -10.0

    # Island
    topo_data.test_topography = 5
    topo_data.location = [0.0, 0.0]
    topo_data.island_width = [100001.0, 200e3]
    topo_data.island = -10.0
    topo_data.offshore = -1000.0

    # == setdtopo.data values ==
    rundata.dtopo_data.dtopofiles = []
    # for moving topography, append lines of the form :   (<= 1 allowed for now!)
    #   [topotype, minlevel,maxlevel,fname]

    # == setqinit.data values ==
    qinit_path = './qinit.txt'
    rundata.qinit_data.qinit_type = 0
    rundata.qinit_data.qinitfiles = [[1, 1, qinit_path]]
    # make_qinit_file(rundata, path=qinit_path, A=1e-1, sigma=10e3, 
    #                          center=(0.0, 0.0), refinement_factor=2, 
    #                          plot=False)
    make_qinit_file(rundata, path=qinit_path, A=1e-1, sigma=10e3, 
                             center=(-75e3, 0.0), refinement_factor=2, 
                             plot=False, init_type="plain-wave-sine")

    # == setfixedgrids.data values ==
    rundata.fixed_grid_data.fixedgrids = []
    # for fixed grids append lines of the form
    # [t1,t2,noutput,x1,x2,y1,y2,xpoints,ypoints,\
    #  ioutarrivaltimes,ioutsurfacemax]
    # geodata.fixedgrids.append([3,8,6,52.0,72.0,52.0,72.0,100,100,0,1])

    return rundata
    # end of function setgeo
    # ----------------------

def make_qinit_file(rundata, path="./qinit.txt", A=1.0, sigma=10.0, 
                             center=(0.0, 0.0), refinement_factor=2,
                             plot=False, init_type="gaussian"):

    x = numpy.linspace(rundata.clawdata.lower[0], rundata.clawdata.upper[0], 
                              rundata.clawdata.num_cells[0] * refinement_factor)
    y = numpy.linspace(rundata.clawdata.lower[1], rundata.clawdata.upper[1], 
                              rundata.clawdata.num_cells[1] * refinement_factor)
    X, Y = numpy.meshgrid(x, y)
    
    if init_type == "gaussian":
        eta = A * numpy.exp(- ((X - center[0])**2 + (Y - center[1])**2) / sigma**2)
    elif init_type == "random":
        eta = 2e-4 * numpy.random.uniform(-1.0, 1.0, (x.shape[0],y.shape[0]))
    elif init_type == "plain-wave-sine":
        eta = A * numpy.sin((X - center[0]) / sigma) * (center[0] < x) * (x < center[0] + sigma * 0.5)
    else:
        raise ValueError("Unknown init_type")

    if plot:
        import matplotlib.pyplot as plt
        fig = plt.figure()
        axes = fig.add_subplot(1, 1, 1)
        plot = axes.pcolor(X, Y, eta)
        plt.colorbar(plot)
        # plt.savefig("init_condition.png")

        plt.show()

    # if not os.path.exists(path):
    with open(path, 'w') as qinit_file:
        for (j, latitude) in enumerate(numpy.flipud(y)):
            for (i, longitude) in enumerate(x):
                # print "(%s, %s), (%s, %s), eta = %s" % (i,j,longitude, latitude, eta[j,i])
                qinit_file.write("%s %s %s\n" % (longitude, latitude, eta[j,i]))




if __name__ == '__main__':
    # Set up run-time parameters and write all data files.
    import sys
    rundata = setrun(*sys.argv[1:])
    rundata.write()

