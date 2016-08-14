"""
Module for loading the radial velocities
"""

import pandas as pd
import os
import subsaturn
import cpsutils.io

LITDIR = os.path.join(
    os.path.dirname(subsaturn.__file__),'data/rv/literature/'
)

def read_subsat2():
    dfall = []
    df = cpsutils.io.load_vst('epic205071984')
    df['tel'] = 'hires'
    df['starname'] = 'K2-32'
    dfall.append(df)

    df = cpsutils.io.load_vst('epic206247743')
    df['tel'] = 'hires'
    df['starname'] = 'K2-39'
    dfall.append(df)

    df = cpsutils.io.load_vst('epic201546283')
    df['tel'] = 'hires'
    df['starname'] = 'K2-27'
    dfall.append(df)
    dfall = pd.concat(dfall)
    dfall = dfall.rename(columns={'jd':'time'})
    dfall = dfall[['starname','tel','time','mnvel','errvel']]

    df = []    
    df.append(read_dai())
    df.append(read_vaneylen16b())
    df = pd.concat(df,ignore_index=True)
    df = df['starname tel t mnvel errvel'.split()]
    df = df.rename(columns={'t':'time'})
    dfall = pd.concat([dfall,df],ignore_index=True)
    return dfall

def read_dai():

    basedir = os.path.join(LITDIR, 'Dai16/')
    df = []
    for starname in 'K2-19 K2-24 K2-32'.split():
        fn = os.path.join(basedir,'{}.txt'.format(starname) )
        temp = pd.read_table(
            fn, sep='&', prefix='x', header=None, 
            names='t mnvel errvel bis tel'.split()
        )
        temp['starname'] = starname
        df.append(temp)
    df = pd.concat(df)
    df.tel = df.tel.replace(0,'pfs').replace(1,'harps')
    return df

def read_vaneylen16b():
    basedir = os.path.join(LITDIR, 'VanEylen16b/')
    fn = os.path.join(basedir,'K2-39.txt')
    df = pd.read_table(
        fn, sep='&', prefix='x', header=None, skiprows=1,
        names='t mnvel errvel fwhm bis tel'.split()
    )
    df['starname'] = 'K2-39'
    df.tel = df.tel.str.replace('HARPS','harps').str.replace('FIES','fies'). \
             str.replace('PFS','pfs').str.strip()

    return df

    
