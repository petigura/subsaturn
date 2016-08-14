# Module for computing stellar properties
from argparse import ArgumentParser
import isochrones
from isochrones import StarModel
from isochrones.dartmouth import Dartmouth_Isochrone
import os 
import pandas as pd
import numpy as np
OUTPUTDIR = '/Users/petigura/Research/subsaturn/subsaturn/data/stellar/'
excelfn = os.path.join(OUTPUTDIR,'spectroscopic_parameters.xlsx')

def parameters(id):
    df = pd.read_excel(excelfn)
    df.index = df.id
    star = df.ix[id]
    Teff = (star.teff, star.teff_err)
    logg = (star.logg, star.logg_err)
    feh = (star.fe, star.fe_err)
    vmag = (star.vmag, star.vmag_err)
    vsini = None
    return Teff, logg, feh, vsini, vmag

def isochrones(name):
    dar = Dartmouth_Isochrone()
    Teff, logg, feh, vsini, vmag = parameters(name)
    model  = StarModel(dar, Teff=Teff, feh=feh, logg=logg, V=vmag, )
    outfn = os.path.join(OUTPUTDIR,'{}_isochrones.hdf'.format(name))
    print "performing isochrones analysis on {}".format(name)
    model.fit(overwrite=True)
    columns = 'Teff logg feh mass radius age distance'.split()
    print "performing isochrones analysis on {}".format(name)
    print model.samples[columns].quantile([0.15,0.5,0.85]).T.to_string()
    model.save_hdf(outfn)

def torres(name):
    samples = 1000
    Teff, logg, feh, vsini, vmag = parameters(name)

    b1 = 2.4427 # +/- 0.038
    b2 = 0.6679 # +/- 0.016
    b3 = 0.1771 # +/- 0.027
    b4 = 0.705 # +/- 0.13
    b5 = -0.21415 # +/- 0.0075
    b6 = 0.02306 # +/- 0.0013
    b7 = 0.04173 # +/- 0.0082

    Teff = Teff[0] + np.random.randn(samples)*Teff[1]
    logg = logg[0] + np.random.randn(samples)*logg[1]
    feh = feh[0] + np.random.randn(samples)*feh[1]

    X = np.log10(Teff) - 4.1 
    logRstar = (
        b1 + b2*X + b3*X**2 + b4*X**3 + b5*logg**2 + b6*logg**3 + b7*feh
        )

    
    Rstar = 10**logRstar
    print "{} Radii from Torres 2010 empircial relations".format(name)
    print pd.DataFrame(Rstar).quantile([0.15,0.50,0.85])

if __name__=='__main__':
    psr = ArgumentParser()
    subpsr = psr.add_subparsers(title="subcommands",dest="subparser_name")

    # Run sub parser command
    psr_fit = subpsr.add_parser("isochrones")
    psr_fit.add_argument('name',type=str)

    psr_fit = subpsr.add_parser("torres")
    psr_fit.add_argument('name',type=str)

    psr_table = subpsr.add_parser("table")
    args = psr.parse_args()

    if args.subparser_name=="isochrones":
        name = args.name
        isochrones(name)

    if args.subparser_name=="torres":
        name = args.name
        torres(name)

    if args.subparser_name=="table":
        names = 'epic201546283 epic205071984 epic206247743_brewer'.split()
        def loopspec(func):
           def func_wrapper():
               s =r" & ".join( [func(name) for name in names])
               s+=r" & prov \\"
               return s
           return func_wrapper

        @loopspec
        def teff(name):
            Teff, logg, feh, vsini, vmag = parameters(name)
            return "%i$\pm$%i" % Teff

        @loopspec
        def logg(name):
            Teff, logg, feh, vsini, vmag = parameters(name)
            return "%.2f$\pm$%.2f" % logg

        @loopspec
        def feh(name):
            Teff, logg, feh, vsini, vmag = parameters(name)
            return "%.2f$\pm$%.2f" % feh

        @loopspec
        def mass(name):
            outfn = os.path.join(OUTPUTDIR,'{}_isochrones.hdf'.format(name))
            model = StarModel.load_hdf(outfn)
            p15, p50, p85 = model.samples['mass'].quantile([0.15,0.5,0.85])
            return "${%.2f}^{%+.2f}_{%+.2f}$" % (p50, p85-p50, p15-p50)

        @loopspec
        def radius(name):
            outfn = os.path.join(OUTPUTDIR,'{}_isochrones.hdf'.format(name))
            model = StarModel.load_hdf(outfn)
            p15, p50, p85 = model.samples['radius'].quantile([0.15,0.5,0.85])
            return "${%.2f}^{%+.2f}_{%+.2f}$" % (p50, p85-p50, p15-p50)

        @loopspec
        def age(name):
            outfn = os.path.join(OUTPUTDIR,'{}_isochrones.hdf'.format(name))
            model = StarModel.load_hdf(outfn)
            age = model.samples['age']
            age = 10**age / 1e9
            p15, p50, p85 = age.quantile([0.15,0.5,0.85])
            return "${%.1f}^{%+.1f}_{%+.1f}$" % (p50, p85-p50, p15-p50)

        print r"name & & " + " & ".join(names) + r" &  \\ "
        print r"\teff & K &" + teff()  
        print r"\logg & dex & " + logg()
        print r"\fe & dex & " + feh()
        print r"\Mstar & \Msun & " + mass()
        print r"\Rstar & \Rsun & " + radius()
        print r"Age & Gyr & " + age()

