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
    st_age st_ageerr1 st_ageerr2
    pl_orbsmax 
    PL_DEF_REFLINK pl_massmeth latex_notes notes 
    include include_pl_orbeccen include_st_metfe
    """.lower().split()
    cut = cut[cut.include==1]
    return cut[col]

def gauss_samp(val, valerr1, valerr2, size=10000, seed=None):
    if seed is not None:
        np.random.seed(seed) # Included for deterministic code
    valerr = 0.5 * (valerr1 - valerr2)
    val = np.random.normal(loc=val,scale=valerr,size=size)
    return val

def add_cols(df):
    df2 = df.copy()
    df2['pl_dens'] = 0.0
    for i,row in df.iterrows():
#        if row.pl_name=="K2-24 c": import pdb;pdb.set_trace()
        pl_masse = gauss_samp(
            row.pl_masse, row.pl_masseerr1, row.pl_masseerr2,seed=0
        )
        pl_rade = gauss_samp(
            row.pl_rade, row.pl_radeerr1, row.pl_radeerr2,seed=1
        )
        st_mass = gauss_samp(
            row.st_mass, row.st_masserr1, row.st_masserr2,seed=2
        )
        st_rad = gauss_samp(
            row.st_rad, row.st_raderr1, row.st_raderr2, seed=3
        )
        st_teff = gauss_samp(
            row.st_teff, row.st_tefferr1, row.st_tefferr2, seed=4
        )
        pl_orbper = gauss_samp(
            row.pl_orbper, 1e-6, -1e-6, seed=5
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
    s_notes = ""
    with open(tablefn, 'w') as f:
        f.write('% name radius mass density ecc teq cmf notes\n')
        df.pl_name = df.pl_name.replace('EPIC-211736671 b','EPIC-2117 b')
        for i, row in df.iterrows():
            s = row_to_string(row)
            f.write(s)

            if row.latex_notes!="":
                s_notes+="{}---{}; ".format(row.pl_name,row.latex_notes)

    print s_notes

def row_to_string(row):
    row['pl_cmfper'] = row['pl_cmf'] * 100 
    row['pl_cmfpererr1'] = row['pl_cmferr1'] * 100 
    row['pl_cmfpererr2'] = row['pl_cmferr2'] * 100 

    s = r""
    s+=r"{pl_name:s}"
    s+=r" & {pl_pnum:.0f}"
    s+=r" & {pl_rade:.2f}^{{ +{pl_radeerr1:.2f} }}_{{ {pl_radeerr2:.2f} }}"
    s+=r" & {pl_masse:.1f}^{{ +{pl_masseerr1:.1f} }}_{{ {pl_masseerr2:.1f} }}"
    s+=r" & {pl_dens:.2f}^{{ +{pl_denserr1:.2f} }}_{{ {pl_denserr2:.2f} }}"
    if row.include_pl_orbeccen:
        s+=r" & {pl_orbeccen:.4f}^{{ +{pl_orbeccenerr1:.4f} }}_{{ {pl_orbeccenerr2:.4f} }}"
    else:
        s+=r" & \nodata "
    
    s+=r" & {pl_teq:.0f}"
    s+=r" & {pl_cmfper:.1f}^{{ +{pl_cmfpererr1:.1f} }}_{{ {pl_cmfpererr2:.1f} }}"
    if row.include_st_metfe:
        s+=r" & {st_metfe:.2f}"
    else:
        s+=r" & \nodata "
    #s+=r" & {latex_notes:s}"
    s+=r"\\"
    s = s.format(**row)
    s = s.replace('nan','')
    s += "\n"
    return s
    
