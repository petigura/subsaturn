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
nplanets = 3    # number of planets in the system
instnames = ['hires','harps','pfs','fies']    # list of instrument names. Can be whatever you like but should match 'tel' column in the input file.
ntels = len(instnames)       # number of instruments with unique velocity zero-points
fitting_basis = 'per tc secosw sesinw k'    # Fitting basis, see radvel.basis.BASIS_NAMES for available basis names
bjd0 = 2454833.
planet_letters = {1: 'b', 2:'c',3:'d'}

# Define prior centers (initial guesses) here.
params = radvel.RVParameters(nplanets,basis='per tc e w k') # initialize RVparameters object

params['per1'] = 4.604969 
params['tc1'] = 2152.43155 + 2454833. 
params['e1'] = 0.0 
params['w1'] = np.pi/2. 
params['k1'] = 8.0 
params['per2'] = 19.0 
params['tc2'] = 2082.62516 + 2454833.
params['e2'] = 0.0
params['w2'] = np.pi/2.
params['k2'] = 10.0
params['per3'] = 200.0
params['tc3'] = 2082.62516 + 2454833.
params['e3'] = 0.0
params['w3'] = np.pi/2.
params['k3'] = 10.0
params['dvdt'] = 0.0 # slope
params['curv'] = 0.0 # curvature
params['gamma_hires'] = 1.0 
params['jit_hires'] = 5
params['gamma_harps'] = 1.0
params['jit_harps'] = 5
params['gamma_pfs'] = 1.0
params['jit_pfs'] = 2.6 
params['gamma_fies'] = 1.0
params['jit_fies'] = 5


df = cpsutils.io.load_vst('epic206247743')
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
print data

# Set parameters to be held constant (default is for all parameters to vary). Must be defined in the fitting basis
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
    e1=False,
    w1=False,
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
    radvel.prior.Gaussian('tc1', params['tc1'], 0.01), 
    radvel.prior.Gaussian('per1', params['per1'], 0.01),
    radvel.prior.Gaussian('per2', params['per2'], 5),
    radvel.prior.Gaussian('per3', params['per3'], 20),
    radvel.prior.Gaussian('jit_hires', 5, 2),
    radvel.prior.Gaussian('jit_harps', 5, 2),
    radvel.prior.Gaussian('jit_pfs', 5, 2),
    radvel.prior.Gaussian('jit_fies', 5, 2),
]

time_base = np.mean([np.min(df.time), np.max(df.time)])   # abscissa for slope and curvature terms (should be near mid-point of time baseline)

isochrones_file = '/Users/petigura/Research/subsaturn/subsaturn/data/stellar/epic206247743_brewer_isochrones.hdf'

lightcurvefn = '/Users/petigura/Research/subsaturn/subsaturn/data/lightcurve.xlsx'

df = pd.read_excel(lightcurvefn)
df.index=df.id

planet = dict(
    rp_on_rstar1 = df.ix['epic206247743b','rp_on_rstar'],
    rp_on_rstar_err1 = 0.5*(
        abs(df.ix['epic206247743b','rp_on_rstar_err1']) + 
        df.ix['epic206247743b','rp_on_rstar_err2']
    ),
    rp_on_rstar2 = np.nan,
    rp_on_rstar_err2 = np.nan,
    rp_on_rstar3 = np.nan,
    rp_on_rstar_err3 = np.nan,
)

{% include 'planet_radius+stellar_mass.py' %}

