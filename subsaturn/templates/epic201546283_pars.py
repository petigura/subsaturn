# Example Keplerian fit configuration file
# Required packages for setup
import os
import pandas as pd
import numpy as np
import radvel
import cpsutils.io

# Define global planetary system and dataset parameters
nplanets= 1
instnames = ['hires','harps-n','harps'] 
ntels = len(instnames) 
fitting_basis = 'per tc secosw sesinw k'
bjd0 = 2454833.

planet_letters = {1: 'b'}


# Load radial velocity data, in this example the data is contained in an ASCII file, must have 'time', 'mnvel', 'errvel', and 'tel' keys
import subsaturn.rv
data = subsaturn.rv.read_subsat2()
print data
instnames = ['hires','harps','harps-n']
data = data[(data.starname=='K2-27') & data.tel.isin(instnames)]


data.index=data.tel
data['meanmnvel'] = data.groupby('tel')['mnvel'].mean()
data['mnvel'] -= data['meanmnvel']

# Define prior centers (initial guesses) here.
params = radvel.RVParameters(nplanets,basis='per tc e w k') 
params['per1'] = 6.771315     # period of 1st planet
params['tc1'] = 1979.84484 + 2454833.   # time of inferior conjunction of 1st planet
params['e1'] = 0.01          # eccentricity of 'per tc secosw sesinw logk'1st planet
params['w1'] = np.pi/2.      # argument of periastron of the star's orbit for 1st planet
params['k1'] = 8.0         # velocity semi-amplitude for 1st planet
params['dvdt'] = 0.0         # slope
params['curv'] = 0.0         # curvature
params['gamma_j'] = 1.0      # "                   "   hires_rj
params['jit_j'] = 2.6        # "      "   hires_rj
params['gamma_harps-n'] = 1.0      # "                   "   hires_rj
params['jit_harps-n'] = 2.6        # "      "   hires_rj
params['gamma_harps'] = 2.6        # "      "   hires_rj
params['jit_harps'] = 2.6        # "      "   hires_rj
params['gamma_hires'] = 2.6        # "      "   hires_rj
params['jit_hires'] = 2.6        # "      "   hires_rj


time_base = np.mean([np.min(data.time), np.max(data.time)])   # abscissa for slope and curvature terms (should be near mid-point of time baseline)

isochrones_file = '/Users/petigura/Research/subsaturn/subsaturn/data/stellar/epic201546283_isochrones.hdf'
lightcurvefn = '/Users/petigura/Research/subsaturn/subsaturn/data/lightcurve.xlsx'

df = pd.read_excel(lightcurvefn)
df.index=df.id

planet = dict(
    rp_on_rstar1 = df.ix['epic201546283b','rp_on_rstar'],
    rp_on_rstar_err1 = 0.5 * ( 
        abs(df.ix['epic201546283b','rp_on_rstar_err1']) + 
        df.ix['epic201546283b','rp_on_rstar_err2'])
    )

{% include 'planet_radius+stellar_mass.py' %}


