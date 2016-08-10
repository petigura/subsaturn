# Module for computing stellar properties
from argparse import ArgumentParser
import isochrones
from isochrones import StarModel
from isochrones.dartmouth import Dartmouth_Isochrone
import os 
OUTPUTDIR = '/Users/petigura/Research/subsaturn/subsaturn/data/stellar/'

def parameters(name):
    if name=='epic201546283':
        Teff = (5231.8, 60) # Brewer 2016 
        logg = (4.4495, 0.05) # Brewer
        feh = (0.1484, 0.04) # Brewer 2016, more realistic 
        vsini = 2.29
        V = (12.644, 0.020) # EPIC

    if name=='epic205071984':
        Teff = (5274.6, 60) # Brewer 2016, gives precision of 25 K, but 60
        # is more realistic
        logg = (4.4902, 0.05)
        feh = (-0.0186, 0.04)
        vsini = 0.66
        V = (12.307, 0.030) # EPIC
        prov = 'brewer'

    if name=='epic206247743':
        Teff = (4911.6, 60) # Brewer 2016
        logg = (3.5779, 0.05) # Brewer
        feh = (0.4292, 0.04) # Brewer
        V = (10.832, 0.075) # EPIC
        vsini = 0.1

    if name=='epic206247743_vanEylen':
        logg = (3.44, 0.07) # van Eylen 0.13 lower than brewer
        feh = (0.4292, 0.04) # brewer
        V = (10.832, 0.075) # EPIC

    if name=='epic206247743_specmatch':
        Teff = (5012, 60)
        logg = (3.67, 0.07) # SpecMatch 0.09 dex higher than brewer
        feh = (0.37, 0.04)


    return Teff, logg, feh, vsini, V

if __name__=='__main__':
    psr = ArgumentParser()
    subpsr = psr.add_subparsers(title="subcommands",dest="subparser_name")

    # Run sub parser command
    psr_fit = subpsr.add_parser("fit")
    psr_fit.add_argument('name',type=str)

    psr_table = subpsr.add_parser("table")
    args = psr.parse_args()

    if args.subparser_name=="fit":
        dar = Dartmouth_Isochrone()
        name = args.name
        Teff, logg, feh, vsini, V = parameters(name)

        model  = StarModel(dar, Teff=Teff, feh=feh, logg=logg, V=V, )
        outfn = os.path.join(OUTPUTDIR,'{}_isochrones.hdf'.format(name))

        print "performing isochrones analysis on {}".format(name)
        model.fit(overwrite=True)
        columns = 'Teff logg feh mass radius age distance'.split()
        print "performing isochrones analysis on {}".format(name)
        print model.samples[columns].quantile([0.15,0.5,0.85]).T.to_string()
        model.save_hdf(outfn)

    if args.subparser_name=="table":    
        names = ['epic201546283', 'epic205071984', 'epic206247743']

        def loopspec(func):
           def func_wrapper():
               s =r" & ".join( [func(name) for name in names])
               s+=r" & prov \\"
               return s
           return func_wrapper

        @loopspec
        def teff(name):
            Teff, logg, feh, vsini, V = parameters(name)
            return "%i$\pm$%i" % Teff

        @loopspec
        def logg(name):
            Teff, logg, feh, vsini, V = parameters(name)
            return "%.2f$\pm$%.2f" % logg

        @loopspec
        def feh(name):
            Teff, logg, feh, vsini, V = parameters(name)
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

