import pandas as pd
import os
import subsaturn

LITDIR = os.path.join(
    os.path.dirname(subsaturn.__file__),'data/rv/literature/'
)

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

def read_vaneylen16a():
    basedir = os.path.join(LITDIR, 'VanEylen16a/')
    fn = os.path.join(basedir,'esprint2_final_rv_all.tex')
    df = pd.read_table(
        fn, sep='&', prefix='x', header=None, skiprows=1,
        names='starname t mnvel errvel tel'.split()
    )
    df.tel = df.tel.str.replace('HARPS','harps').str.replace('FIES','fies'). \
             str.replace('PFS','pfs').str.replace('harps-N','harps-n').\
             str.strip()

    df.starname = df.starname.str.replace('epic201546283','K2-27').str.strip()
    return df

def read_lit():
    df = []
    df.append(read_dai())
    df.append(read_vaneylen16b())
    df.append(read_vaneylen16a())
    df = pd.concat(df,ignore_index=True)
    df = df['t mnvel errvel tel starname'.split()]
    return df
    
