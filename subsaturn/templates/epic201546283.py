# Example Keplerian fit configuration file
# Required packages for setup
import os
import pandas as pd
import numpy as np
import radvel
import cpsutils.io
starname = 'epic201546283'
{% include 'epic201546283_pars.py' %}
starname = 'epic201546283'

# Define global planetary system and dataset parameters
vary = dict(
    dvdt = False,
    curv = False,
    logjit_j = False,
    per1 = False,
    tc1 = False,
    secosw1 = False,
    sesinw1 = False,
)

# Define prior shapes and widths here.
priors = [
    radvel.prior.EccentricityPrior( nplanets ),           # Keeps eccentricity < 1
    radvel.prior.Gaussian('tc1', params['tc1'], 0.01), # Gaussian prior on tc1 with center at tc1 and width 0.01 days
    radvel.prior.Gaussian('per1', params['per1'], 0.01),
]


