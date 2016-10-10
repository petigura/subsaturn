# Example Keplerian fit configuration file
# Required packages for setup
import os
import pandas as pd
import numpy as np
import radvel
import pdb
import cpsutils.io
import subsaturn.literature

# Define global planetary system and dataset parameters
starname = 'epic206247743'
instnames = ['hires','harps','pfs','fies']    # list of instrument names. Can be whatever you like but should match 'tel' column in the input file.
ntels = len(instnames)       # number of instruments with unique velocity zero-points
fitting_basis = 'per tc secosw sesinw k' # Fitting basis, see radvel.basis.BASIS_NAMES for available basis names
bjd0 = 2454833.
planet_letters = {1: 'b', 2:'c'}
nplanets = len(planet_letters.keys())

# Define prior centers (initial guesses) here.
params = radvel.RVParameters(nplanets,basis='per tc e w k') # initialize RVparameters object

params['per1'] = 4.604969 
params['tc1'] = 2152.43155 + bjd0
params['e1'] = 0.0 
params['w1'] = np.pi/2. 
params['k1'] = 8.0 
params['per2'] = 330.0
params['tc2'] = 2082.62516 + bjd0 #  Some arbitrary starting value
params['e2'] = 0.0
params['w2'] = np.pi/2.
params['k2'] = 10.0
params['dvdt'] = 0.0 # slope
params['curv'] = 0.0 # curvature
params['gamma_hires'] = -5.0 # Entered in by hand from some prelimary fits
params['jit_hires'] = 5
params['gamma_harps'] = -19.0 # Entered in by hand from some prelimary fits
params['jit_harps'] = 5
params['gamma_pfs'] = -9.0 # Entered in by hand from some prelimary fits
params['jit_pfs'] = 2.6 
params['gamma_fies'] = -9.0 # Entered in by hand from some prelimary fits
params['jit_fies'] = 5


df = cpsutils.io.load_vst('epic206247743',verbose=False)
df['tel'] = 'hires'
df_lit = subsaturn.literature.read_lit()
df_lit = df_lit.rename(columns={'t':'jd'})
df_lit = df_lit[df_lit.starname=='K2-39']

g = df_lit.groupby('tel')
groupmn = g['mnvel'].mean()
df_lit.index = df_lit.tel
df_lit['telmn'] = groupmn
df_lit['mnvel'] -= df_lit['telmn']
df = df.append(df_lit)
df = df[['jd','mnvel','errvel','tel']]
df.columns.values[df.columns.values=='jd'] = 'time'
data = df

# Set parameters to be held constant (default is for all parameters to
# vary). Must be defined in the fitting basis
vary = dict(
    dvdt = False,
    curv = False,
    jit_hires = True,
    jit_harps = True,
    jit_fies = True,
    jit_pfs = True,
    per1 = False,
    tc1 = False,
    secosw1 = False,
    sesinw1 = False,
    per2 = True,
    tc2 = True,
    secosw2 = False,
    sesinw2 = False,
    per3 = True,
    tc3 = True,
    secosw3 = False,
    sesinw3 = False
)

# Define prior shapes and widths here.
priors = [
    radvel.prior.EccentricityPrior( nplanets ), # Keeps eccentricity < 1
    radvel.prior.PositiveKPrior( nplanets ), # Keeps K > 0
    radvel.prior.Gaussian('jit_hires', 5, 2), # Adding reasonable bounds to jitter to keep it from growing too large.
    radvel.prior.Gaussian('jit_harps', 5, 2),
    radvel.prior.Gaussian('jit_pfs', 5, 2),
    radvel.prior.Gaussian('jit_fies', 5, 2),
]

time_base = np.mean([np.min(data.time), np.max(data.time)])
