nplanets = 3
{% include 'epic205071984_data.py' %}
{% include 'epic205071984_three-planet-pars.py' %}
import subsaturn.rv
data = subsaturn.rv.read_subsat2()
instnames = ['hires','pfs','harps']
data = data[
    (data.starname=='K2-32') & data.tel.isin(instnames)
]
starname = 'epic205071984_hires+pfs+harps'
ntels = len(instnames)
fitting_basis = 'per tc secosw sesinw k'
params['gamma_hires'] = 1.0  
params['jit_hires'] = 0   
params['gamma_harps'] = 1.0  
params['jit_harps'] = 0   
params['gamma_pfs'] = 1.0    
params['jit_pfs'] = 0     

vary = dict(
    dvdt = True,
    curv = True,
    secosw1 = False,
    sesinw1 = False,
    secosw2 = False,
    sesinw2 = False,
    secosw3 = False,
    sesinw3 = False,
    per1 = False,
    tc1 = False,
    per2 = False,
    tc2 = False,
    per3 = False,
    tc3 = False,
    jit_hires = True,
    jit_harps = True,
    jit_pfs =  True,
)

time_base = np.mean([np.min(data.time), np.max(data.time)])
