"""
Module for interacting with Lopez grids
"""
import os 

import xarray as xr
import pandas as pd
import numpy as np
from scipy.interpolate import RegularGridInterpolator
from scipy.optimize import brentq
from astropy.io import fits
import subsaturn.literature
from subsaturn.literature import gauss_samp, set_quantiles
from subsaturn.config import DATADIR

fitsfn = os.path.join(DATADIR,'MassRadiusGrid_HHe_sunlike_2_17_2015_Darin.fits')
sscmffn = '/Users/petigura/Research/subsaturn/subsaturn/data/subsaturns_cmf.xls'

def read_grid():
    """Read in the lopez grids

    Args:
        None

    Returns:
        _logradius (xarray): labelled 4-D array with the base-10 log
            of the following quantities: 
               -`time` age (gyrs) , `flux`
            irradiation (Earth-units), `comp`
    """

    with fits.open(fitsfn) as hduL:
        table = hduL[1].data
        radius = table['RADIUSEND'][0,:,0,:,:,:]
        mass = table['MASSVECT'].reshape(-1)
        comp = table['COMPVECT'].reshape(-1)
        flux = table['FLUXVECT'].reshape(-1)
        time = table['TIMEVECT'].reshape(-1)

    logradius = xr.DataArray(
        np.log10(radius), 
        [('logtime', np.log10(time) ), 
         ('logflux', np.log10(flux)), 
         ('logcomp', np.log10(comp)), 
         ('logmass', np.log10(mass))]
    )

    # arange coordinates in strictly increasing order
    df = logradius.to_dataframe(name='logradius')
    df = df.to_records()
    df = pd.DataFrame(df,index=None)
    df = df.sort_values(by=['logtime','logflux','logcomp','logmass'])
    df = df.groupby(['logtime','logflux','logcomp','logmass']).first()
    logradius = xr.Dataset.from_dataframe(df)
    return logradius

class LopezInterpolator(object):
    def __init__(self):
        logradius = read_grid()
        points = (
            logradius.logtime, 
            logradius.logflux, 
            logradius.logcomp, 
            logradius.logmass
        )
        values = logradius.to_array().values[0]
        self.logradius = logradius
        self._logradius_interpolate = RegularGridInterpolator(points, values, )

    def core_mass_fraction(self, mass, radius, flux, time):
        """Core mass fraction

        Args:
            mass (float): mass of planet (Earth-masses)
            radius (float): radius of planet (Earth-radii)
            flux (float): incident flux (Earth-units)
            time (time): Age of planet (Gyr)

        Returns:
            (float): core mass fraction (Mcore/Menv)

        Notes: 
            The interpolation is done in log space, but the input
            parameters are in linear space.

        """

        logmass, logradius, logflux, logtime = self.to_logspace(mass, radius, flux, time)
        def func(logcomp):
            point_i = [logtime, logflux, logcomp, logmass]
            logradius_i = self._logradius_interpolate(point_i)
            return logradius_i - logradius

        logcomp = brentq(
            func, self.logradius.logcomp.min(), self.logradius.logcomp.max()
        )
        comp = 10**logcomp
        return comp

    def to_logspace(self, mass, radius, flux, time):
        logmass = np.log10(mass)
        logradius = np.log10(radius)
        logflux = np.log10(flux)
        logtime = np.log10(time * 1e9)
        return logmass, logradius, logflux, logtime

def sample_ss_cmf(lopi, plnt, sample_age=False, age=5, size=100):
    """
     Draw distributions of mass, radius, teq


    Args:
        lopi (LopezInterpolator): instance of LopezInterpolator object
        plnt (pandas.Series): contains pl_masse, pl_rade, pl_teq, columns
 
    Returns
        pd.DataFrame: with following columns
            - cmf
            - mcore
            - menv
    """
    teq_earth = 279
    masse = gauss_samp(
        plnt.pl_masse, plnt.pl_masseerr1, plnt.pl_masseerr2, size=size
    )
    radius = gauss_samp(
        plnt.pl_rade, plnt.pl_radeerr1, plnt.pl_radeerr2,size=size
    )
    teq = gauss_samp(
        plnt.pl_teq, plnt.pl_teqerr1, plnt.pl_teqerr2,size=size
    )
    age = np.ones(size) * age
    flux = (teq / teq_earth)**4.0

    df = []
    for i in range(size):
        try:
            _masse = masse[i]
            _radius = radius[i]
            _flux = flux[i]
            _age = age[i]
            _cmf = lopi.core_mass_fraction(_masse, _radius, _flux, _age)
            _mcore = _masse * _cmf
            _menv = _masse * (1.0 - _cmf) 
            d = dict(cmf=_cmf, mcore=_mcore, menv=_menv)
        except ValueError:
            d = dict(cmf=np.nan, mcore=np.nan, menv=np.nan)            
        finally:
            df.append(d)

    df = pd.DataFrame(df)
    return df

def compute_ss_cmf(size=100):
    ss = subsaturn.literature.load_ss()

    print "interpolating the Lopez grids using {} samples per planet".format(size)
    lopi = LopezInterpolator()
    i_count = 0
    for i, plnt in ss.iterrows():

        df = sample_ss_cmf(lopi, plnt, size=size)
        nfailed = df.cmf.isnull().sum()
        df = df.dropna()
        set_quantiles(ss, i, df.cmf, 'pl_cmf')
        set_quantiles(ss, i, df.mcore, 'pl_mcore')
        set_quantiles(ss, i, df.menv, 'pl_menv')
        i_count+=1
        print "{},{}: {} samples fell outside grid".format(
            i_count, i, nfailed)

    ss.to_excel(sscmffn)


