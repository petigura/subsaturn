import os
import pandas as pd
import numpy as np
import radvel
import cpsutils.io
import subsaturn.literature

import subsaturn.rv
data = subsaturn.rv.read_subsat2()
instnames = ['hires','pfs','harps']
data = data[
    (data.starname=='K2-32') & data.tel.isin(instnames)
]
starname = 'epic205071984_hires+pfs+harps'
ntels = len(instnames)
fitting_basis = 'per tc secosw sesinw k'

bjd0 = 2454833.
nplanets = 3    # number of planets in the system
planet_letters = {1: 'b', 2:'c', 3:'d'}
params = radvel.RVParameters(nplanets,basis='per tc e w k') 

params['per1'] = 8.992135 # period of 1st planet
params['tc1'] = 2076.91832 + bjd0 # time of inferior conjunction of 1st planet
params['e1'] = 0.00 #
params['w1'] = np.pi/2. #
params['k1'] = 5.0         # velocity semi-amplitude for 1st planet
params['per2'] = 20.660155     # same parameters for 2nd planet ...
params['tc2'] = 2128.40674 + bjd0
params['e2'] = 0.00
params['w2'] = np.pi/2.
params['k2'] = 3.0
params['per3'] = 31.715392     # same parameters for 2nd planet ...
params['tc3'] = 2070.79012 + bjd0
params['e3'] = 0.00
params['w3'] = np.pi/2.
params['k3'] = 3.0
params['dvdt'] = 0.0         # slope
params['curv'] = 0.0         # curvature
params['gamma_hires'] = 1.0  
params['jit_hires'] = 1.0
params['gamma_harps'] = 1.0  
params['jit_harps'] = 1.0 
params['gamma_pfs'] = 1.0    
params['jit_pfs'] = 1.0 

# Define prior shapes and widths here.
priors = [
    radvel.prior.EccentricityPrior( nplanets ), # Keeps eccentricity < 1
# radvel.prior.PositiveKPrior( nplanets ), # Keeps K > 0
    radvel.prior.Gaussian('tc1', params['tc1'], 0.01), # Gaussian prior on tc1 with center at tc1 and width 0.01 days
    radvel.prior.Gaussian('per1', params['per1'], 0.01),
    radvel.prior.Gaussian('tc2', params['tc2'], 0.01),
    radvel.prior.Gaussian('per2', params['per2'], 0.01),
    radvel.prior.Gaussian('tc3', params['tc3'], 0.01),
    radvel.prior.Gaussian('per3', params['per3'], 0.01)
]

vary = dict(
    dvdt = False,
    curv = False,
    secosw1 = False,
    sesinw1 = False,
    secosw2 = False,
    sesinw2 = False,
    secosw3 = False,
    sesinw3 = False,
    per1 = False,
    tc1 = False,
    per2 = False,
    tc2 = False,
    per3 = False,
    tc3 = False,
    jit_hires = True,
    jit_harps = True,
    jit_pfs =  True,
)

time_base = np.mean([np.min(data.time), np.max(data.time)])
