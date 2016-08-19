{% include 'imports.py' %}

isochrones_file = '/Users/petigura/Research/subsaturn/subsaturn/data/stellar/epic205071984_isochrones.hdf'

lightcurvefn = '/Users/petigura/Research/subsaturn/subsaturn/data/lightcurve.xlsx'

df = pd.read_excel(lightcurvefn)
df.index=df.id

planet = dict(
    rp_on_rstar1 = df.ix['epic205071984b','rp_on_rstar'],
    rp_on_rstar_err1 = 0.5*(
        abs(df.ix['epic205071984b','rp_on_rstar_err1']) + 
        df.ix['epic205071984b','rp_on_rstar_err2']
    ),
    rp_on_rstar2 = df.ix['epic205071984c','rp_on_rstar'],
    rp_on_rstar_err2 = 0.5*(
        abs(df.ix['epic205071984c','rp_on_rstar_err1']) + 
        df.ix['epic205071984c','rp_on_rstar_err2']
    ),
    rp_on_rstar3 = df.ix['epic205071984d','rp_on_rstar'],
    rp_on_rstar_err3 = 0.5*(
        abs(df.ix['epic205071984d','rp_on_rstar_err1']) + 
        df.ix['epic205071984d','rp_on_rstar_err2']
    
    ),
)

{% include 'planet_radius+stellar_mass.py' %}





