nplanets = 3
{% include 'epic205071984_data.py' %}

import subsaturn.rv
data = subsaturn.rv.read_subsat2()
data = data[(data.starname=='K2-32') & (data.tel.isin(['hires'])) ]
 # abscissa for slope and curvature terms (should be near mid-point of time baseline)
time_base = np.mean([np.min(data.time), np.max(data.time)])

starname = 'epic205071984_hires'
{% include 'epic205071984_three-planet-pars.py' %}
# Define global planetary system and dataset parameters
instnames = 'hires'.split() # list of instrument names. Can be whatever you like but should match 'tel' column in the input file.
ntels = len(instnames)       # number of instruments with unique velocity zero-points
fitting_basis = 'per tc secosw sesinw k' # Fitting basis, see radvel.basis.BASIS_NAMES for available basis names

params['gamma_hires'] = 1.0  
params['jit_hires'] = 2.6

vary = dict(
    dvdt = True,
    curv = True,
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
)

