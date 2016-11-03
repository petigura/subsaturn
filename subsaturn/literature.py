from cStringIO import StringIO as sio

import numpy as np
import pandas as pd
from astropy import constants as c 
from astropy import units as u

import radvel.orbit
import cpsutils.nea

csvfn = '/Users/petigura/Research/cpsutils/cpsutils/data/exoplanet-archive_planets.csv'
extra_ssfn = '/Users/petigura/Research/subsaturn/subsaturn/data/extra_subsaturns.xls'

def load_ss(verbose=False):
    """Load subsaturn table"""

    # Constants
    SS_RP_MIN = 4 # Lower bound on sub-saturn (Earth-radii)
    SS_RP_MAX = 8 # Upper bound
    
    nea = cpsutils.nea.read_nea(csvfn)
    nea.index = nea.pl_name


    pl_masserr = 0.5*(nea.pl_masseerr1 - nea.pl_masseerr2)
    pl_masssig = nea.pl_masse / pl_masserr 

    pl_radiuserr = 0.5*(nea.pl_radeerr1 - nea.pl_radeerr2)
    pl_radiussig = nea.pl_rade / pl_radiuserr    

    # Perform an initial round of cuts
    b = (
        nea.pl_rade.between(SS_RP_MIN,SS_RP_MAX) & 
        nea.pl_masse.notnull() & 
        (nea.pl_masselim==0.0) & 
        (pl_masssig > 2) & 
        (pl_radiussig > 4) 
    )
    cut = nea[b]

    # Augment info from excel spreadsheet
    extra_ss = pd.read_excel(extra_ssfn)
    extra_ss.index = extra_ss.pl_name
    cut.index = cut.pl_name
    cut['pl_teq'] = 0.0
    if verbose:
        print "agumenting the table with the following values"

    for i_row,row in extra_ss.iterrows():
        for i_col,value in row.dropna().iteritems():
            if verbose:
                print i_row,i_col,value
            cut.loc[i_row,i_col] = value

    cut = add_cols(cut)
    
    # If certain values are nans, add_cols would decimate
    cols_derived = 'pl_teq pl_teqerr1 pl_teqerr2 pl_dens pl_denserr1 pl_denserr2'.split()
    for i_row,row in extra_ss[cols_derived].iterrows():
        for i_col,value in row.dropna().iteritems():
            if verbose:
                print i_row,i_col,value
            cut.loc[i_row,i_col] = value

    pl_denserr = 0.5*(cut.pl_denserr1 - cut.pl_denserr2)
    pl_denssig = cut.pl_dens / pl_denserr  

    cut = cut[pl_denssig > 2]

    col = """
    PL_NAME pl_letter pl_pnum 
    st_teff st_tefferr1 st_tefferr2
    st_metfe st_metfeerr1 st_metfeerr2
    st_rad st_raderr1 st_raderr2
    st_mass st_masserr1 st_masserr2
    pl_orbper 
    pl_masse pl_masseerr1 pl_masseerr2 pl_masselim 
    pl_rade pl_radeerr1 pl_radeerr2 
    pl_dens pl_denserr1 pl_denserr2 
    pl_orbeccen pl_orbeccenerr1 pl_orbeccenerr2 pl_orbeccenlim 
    pl_teq pl_teqerr1 pl_teqerr2
    pl_orbsmax 
    PL_DEF_REFLINK pl_massmeth latex_notes notes include
    """.lower().split()
    cut = cut[cut.include==1]
    return cut[col]

def gauss_samp(val, valerr1, valerr2, size=10000):
    valerr = 0.5 * (valerr1 - valerr2)
    val = np.random.normal(loc=val,scale=valerr,size=size)
    return val

def add_cols(df):
    df2 = df.copy()
    df2['pl_dens'] = 0.0
    for i,row in df.iterrows():
        pl_masse = gauss_samp(row.pl_masse, row.pl_masseerr1, row.pl_masseerr2)
        pl_rade = gauss_samp(row.pl_rade, row.pl_radeerr1, row.pl_radeerr2)
        st_mass = gauss_samp(row.st_mass, row.st_masserr1, row.st_masserr2)
        st_rad = gauss_samp(row.st_rad, row.st_raderr1, row.st_raderr2)
        st_teff = gauss_samp(row.st_teff, row.st_tefferr1, row.st_tefferr2)
        pl_orbper = gauss_samp(
            row.pl_orbper, 1e-6, -1e-6
        )

        Lstar = radvel.orbit.Lstar(st_rad, st_teff)
        st_mass = st_mass * u.Msun
        pl_orbper =  pl_orbper * u.d
        a = (c.G * st_mass * pl_orbper**2 / 4 / np.pi**2)**(1.0/3.0)
        a = a.to(u.AU).value
        Sinc = radvel.orbit.Sinc(Lstar, a)
        pl_teq = radvel.orbit.Teq(Sinc)

        # planet density in g/cc
        pl_dens = 5.51 * pl_masse * pl_rade**-3.0
        set_quantiles(df2, i, a, 'pl_orbsmax')
        set_quantiles(df2, i, pl_teq, 'pl_teq')
        set_quantiles(df2, i, pl_dens, 'pl_dens')

    return df2

def set_quantiles(df, i, val, key):
    df.ix[i,key] = np.percentile(val,50)
    df.ix[i,key+'err1'] = np.percentile(val,85) - np.percentile(val,50)
    df.ix[i,key+'err2'] = np.percentile(val,15) - np.percentile(val,50)

def df_to_rv_table(df, tablefn,):
    with open(tablefn, 'w') as f:
        f.write('% name radius mass density \n')
        for i, row in df.iterrows():
            s = (
                r"{pl_name:s}"
                +r" & {pl_pnum:.0f}"
                +r" & {pl_rade:.2f}^{{ +{pl_radeerr1:.2f} }}_{{ {pl_radeerr2:.2f} }}"
                +r" & {pl_masse:.2f}^{{ +{pl_masseerr1:.2f} }}_{{ {pl_masseerr2:.2f} }}"
                +r" & {pl_dens:.2f}^{{ +{pl_denserr1:.2f} }}_{{ {pl_denserr2:.2f} }}"
                +r" & {pl_teq:.0f}"
                +r" & {latex_notes:s}"
                +r"\\"
            )
            s = s.format(**row)
            s += "\n"
            print s
            f.write(s)

