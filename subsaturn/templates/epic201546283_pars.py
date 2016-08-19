# Example Keplerian fit configuration file
# Required packages for setup
import os
import pandas as pd
import numpy as np
import radvel
import cpsutils.io

# Define global planetary system and dataset parameters
nplanets= 1
instnames = ['j','harps-n','harps'] 
ntels = len(instnames) 
fitting_basis = 'per tc secosw sesinw k'
bjd0 = 2454833.

planet_letters = {1: 'b'}


# Load radial velocity data, in this example the data is contained in an ASCII file, must have 'time', 'mnvel', 'errvel', and 'tel' keys
df = cpsutils.io.load_vst(starname)
df = df[['jd','mnvel','errvel']]
df.columns.values[df.columns.values=='jd'] = 'time'
df['tel']='j'

import subsaturn.literature
lit = subsaturn.literature.read_lit()
lit = lit.rename(columns={'t':'time'})
lit = lit.query('starname=="K2-27"')
lit.index = lit.tel
lit['meanmnvel'] = lit.groupby('tel')['mnvel'].mean()
lit['mnvel'] -= lit['meanmnvel']

df = pd.concat([df,lit])



data = df



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


