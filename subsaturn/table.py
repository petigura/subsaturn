import pandas as pd
from numpy import *
import radvel
import numpy as np
import re
from isochrones import StarModel

def fmt_chain(df):
    quant = df.quantile([0.14,0.50,0.86])
    err = 0.5*(quant.ix[0.86] - quant.ix[0.14])
    med = quant.ix[0.50]
    err2 = quant.ix[0.86] - quant.ix[0.50]
    err1 = quant.ix[0.50] - quant.ix[0.14] 
    df = pd.DataFrame([med,err,err1,err2],index=['med err err1 err2'.split()]).T
    df['fmt'] = ''
    for i, row in df.iterrows():
        def prec(logerr):
            return max(int(logerr-2)*-1 ,0)
        
        if row.err==0:
            continue 
        asym = abs(row.err1-row.err)/row.err
        if asym > 0.1:
            minlogerr = min(log10(row.err1),log10(row.err2))
            _prec = prec(minlogerr)
            s ="{med:.{prec:}f}_{{ -{err1:.{prec:}f} }}^{{+{err2:.{prec:}f}}}".format(prec=_prec,**row)
        else:
            logerr = log10(row.err)
            dec = int(logerr-2)*-1 
            _prec = prec(logerr)
            s = "{med:.{prec:}f} \pm {err:.{prec:}f} ".format(prec=_prec,**row)
        df.ix[i,'fmt'] = s
    return df

def print_fmt_chain(df):
    for i,row in df.iterrows():
        line = "{{{:s}}}{{ {:s} }}%".format(i,row.fmt)
        print line 

def saveparams(df,fn):
    with open(fn,'w') as f:
        for i,row in df.iterrows():
            line = "{{{:s}}}{{ {:s} }}%".format(i,row.fmt)
            f.write(line+'\n')

def augment_chain(chain, isochrones_file, lpar_list):
    model = StarModel.load_hdf(isochrones_file)
    chain_star = model.samples
    chain_star['agegyr'] = 10**chain_star['age'] / 1e9
    chain_star = chain_star['Teff mass radius agegyr'.split()]

    nchain = len(chain)
    chain_star = chain_star.sample(n=nchain,replace=True)
    chain_star.index = chain.index
    chain = pd.concat([chain_star,chain],axis=1)

    i_planet = 1 
    for lpar in lpar_list:
        e = chain['e%i' % i_planet]
        k = chain['k%i' % i_planet]
        RpRstar = np.random.normal(
            loc=lpar.RpRstar,scale=lpar.RpRstar_err,size=nchain
        ) * 1e-2
        P = np.random.normal(
            loc=lpar.P,scale=lpar.P_err,size=nchain
        )
        T0 = np.random.normal(
            loc=lpar.T0,scale=lpar.T0_err,size=nchain
        )

        Rp = chain.radius * 109.045 * RpRstar

        Mpsini = radvel.orbit.Msini(k, P, chain['mass'], e, Msini_units='earth')
        rhop = radvel.orbit.density(Mpsini,Rp)
        
        chain['P%i' % i_planet] = P
        chain['T0%i' % i_planet] = T0
        chain['RpRstar%i' % i_planet] = RpRstar
        chain['Rp%i' % i_planet] = Rp
        chain['Mpsini%i' % i_planet] = Mpsini
        chain['rhop%i' % i_planet] = rhop
        i_planet +=1

    print_fmt_chain(fmt_chain(chain))

    return chain


def read_crossfield16():
    cols = 'other epic P T0 T14 RpRstar a Rp Sinc FFP Disp'.split()
    df = pd.read_table(
        '/Users/petigura/Research/subsaturn/arxiv/crossfield16/' 
        + 'candidate_results_v8.tex',
        skiprows=6,header=None,sep='&',names=cols)
    df = df.dropna()

    def parse_str(x):
        val, err = x.split('(')
        err = err[:-2]
        nerr = len(err)
        err2 = re.sub(r'\d', '0', val)
        err2 = err2[:-nerr] + err
        return val, err2

    for col in 'P T0 T14 RpRstar a Rp Sinc'.split():
        val = df[col].apply(lambda x : parse_str(x)[0])
        err = df[col].apply(lambda x : parse_str(x)[1])
        df[col] = val
        df[col+'_err'] = err

    df = df.convert_objects(convert_numeric=True)
    df['other'] = df.other.str.strip()
    return df
