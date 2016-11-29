from matplotlib.pylab import *
import matplotlib.patheffects as PathEffects # needed for Oreo font
import seaborn as sns
sns.set()
sns.set(font='Helvetica')
sns.set_style("whitegrid")
sns.set_color_codes()
import numpy as np
import subsaturn.literature
import subsaturn.lopez
import pandas as pd

ECC_THRESH = 0.1

def read_ss():
    ss = pd.read_excel(subsaturn.lopez.sscmffn,index_col=0)
    ss = ss.rename(columns={'pl_name.1':'pl_name'})
    ss['pl_fenv'] = 1 - ss['pl_cmf']
    ss['pl_fenverr1'] = -1.0 * ss['pl_cmferr2']
    ss['pl_fenverr2'] = -1.0 * ss['pl_cmferr1']
    ss = eccenbin(ss, ECC_THRESH)
    return ss 

def errorbar_pnum(ss0, yk, **kwargs):
    ss = ss0.copy()
    for pnum in ss.pl_pnum.drop_duplicates():
        idx = ss[ss.pl_pnum==pnum].index
        ss.ix[idx,'pl_pnum'] += linspace(-0.15, 0.15, len(idx))
    errorbar_ecc(ss, 'pl_pnum', yk, yerr=True,  **kwargs)

def errorbar_ecc(ss, xk, yk, xerr=None, yerr=None, **kwargs):
    """Makes errorbar plots against number of planets"""
    ss_highecc = ss[ss.pl_highecc==True]
    ss_lowecc = ss[ss.pl_highecc==False]
    ss_nanecc = ss[ss.pl_highecc.isnull()]
    labelL = ['e > 0.1', 'e < 0.1','e uncertain']
    colorL = ['r', 'b','g']
    ssL = [ss_highecc, ss_lowecc, ss_nanecc]

    for i in range(3):
        ss = ssL[i]
        label = labelL[i]
        ss = ssL[i]
        color = colorL[i]

        if xerr:
            x, _xerr = err_errorbar(ss, xk)
        else:
            x = ss[xk]
            _xerr = None

        if yerr:
            y, _yerr = err_errorbar(ss, yk)
        else: 
            y = ss[yk]
            _yerr = None

        errorbar(x, y, xerr=_xerr,yerr=_yerr,label=label,color=color, **kwargs)

def eccenbin(df, thresh):
    """
    Put planets into different eccentricity bins

    Args:
        df (pandas.DataFrame): containing the following keys
            - pl_orbeccen: eccentricity
            - pl_orbeccenerr1: upper errorbar on eccentricity
            - pl_orbeccenerr2: lower errorbar (negative)
        thresh (float): threshold value of eccentricity
    """
    col = 'pl_highecc'
    df[col] = None
    for i, row in df.iterrows():
        if row.pl_orbeccen + row.pl_orbeccenerr1 < thresh:
            df.ix[i,col] = False
        if row.pl_orbeccen + row.pl_orbeccenerr2 > thresh:
            df.ix[i,col] = True
    return df


def format_st_metfe(func):
    """Format X-axis for metallicity"""
    def func_wrapper():
        func()
        xlabel('[Fe/H]')
        xlim(-0.3,0.5)
        gcf().set_tight_layout(True)
    return func_wrapper

def format_teq(func):
    """Foramt X-axis for Teq"""
    def func_wrapper():
        func()
        xlabel('Equilibrium Temp (K)')
        gcf().set_tight_layout(True)
    return func_wrapper

def format_pnum(func):
    """Format X-axis for planet number"""
    def func_wrapper():
        func()
        xlabel('Number of Planets')
        xlim(0,7)
        gcf().set_tight_layout(True)
    return func_wrapper

def format_cmf(func):
    """Format Y-axis for core mass fraction"""
    def func_wrapper():
        func()
        ylabel(tex_cmf)
        ylim(0,1)
        gcf().set_tight_layout(True)
    return func_wrapper

def format_masse(func):
    """Format Y-axis for mass"""
    def func_wrapper():
        func()
        yt = [0.3,1,3,10,30,100]
        yticks(yt,yt)
        ylim(yt[0],yt[-1])
        gcf().set_tight_layout(True)
    return func_wrapper


def err_errorbar(df, key):
    """Turn val, valerr1, valerr2 into a format that MPL understands"""
    val = df[key]
    valerr = np.vstack([-1.0*df[key+'err2'],df[key+'err1']])
    return val, valerr


def plot_ttv_rv_teq(df, xk, yk, mode='rp-rho', fig0=None, ax0=None, 
                    offsets=None, ann_kw={}, scat_kw={}):
    """Plot planet density againts planet radius

    Args:
        df (pandas DataFrame): must contain the following keys:
            - pl_rade
            - pl_dens
            - URp
            - Upl_dens
            - pl_name
        offsets (pandas DataFrame, optional): offsets in points, must contain:
            - pl_name
            - x
            - y 
    """
    rc('font',size=10)
    zerrorbar = 5
    ztext = 5.5
    zpoints = 6
    size = 100
    vmin = 300 # must define hard limits for the color scale
    vmax = 1800 

    # Provision Figure
    if fig0 is None:
        fig, ax = subplots(figsize=(6, 4))
    else:
        fig = fig0
        ax = ax0

    x, xerr = err_errorbar(df, xk)
    y, yerr = err_errorbar(df, yk)
    path_effects = [PathEffects.withStroke(linewidth=2,foreground="w")]
    def ann(row):
        txt = ax.annotate(
            row.pl_name, xy=(x.ix[row.pl_name],y.ix[row.pl_name]), 
            xycoords='data', xytext=(row.x_offset,row.y_offset), 
            textcoords='offset points', path_effects=path_effects, 
            zorder=zpoints, **ann_kw
        )

    df.apply(ann, axis=1)

    # Plot error bar (no symbols)
    errorbar(
        x, y, yerr=yerr, xerr=xerr, fmt='.', zorder=zerrorbar, mew=0, lw=1, 
        color='0.4'
    )

    marker_dict = {'RV':'^','TTV':'v','RV+TTV':'d'}
    pl_massmeth = df.pl_massmeth.drop_duplicates()
    for meth in pl_massmeth :
        marker = marker_dict[meth]
        idx = df[df.pl_massmeth==meth].index
        _x = x.ix[idx]
        _y = y.ix[idx]
        _c = df.ix[idx,'pl_teq']
        col = scatter(
            _x, _y, c=_c, linewidth=1, cmap=cm.nipy_spectral,  
            vmin=vmin, vmax=vmax, marker=marker, zorder=zpoints, label=meth,
            **scat_kw
        )
        col.set_edgecolors('w')

    right = 0.75
    cax_pos = [right+0.05, 0.15, 0.02, 0.5]
    if (fig0 is None) and (mode=='rp-rho') :
#        cbar = colorbar(fraction=0.03)
        semilogy()
        xlabel('Planet Size (Earth-radii)')
        ylabel('Density (g/cc)')
        yt = [0.05, 0.07, 0.1, 0.2, 0.3, 0.4, 0.5, 0.7, 1, 2, 3]
        yticks(yt,yt)
        grid(which='minor')#,linestyle=':',linewidth=0.5,alpha=0.5)
        fig.subplots_adjust(right=right)
        ylim(0.05,6)
        xlim(3.5,8.5)
        cax = fig.add_axes(cax_pos) # setup colorbar axes
        cbar = colorbar(cax=cax)
        cbar.set_label('Equilibrium Temp (K)')
        plt.sca(ax)

    if (fig0 is None) and (mode=='mp-rp') :
#        cbar = colorbar(fraction=0.03)
        semilogx()
        xlabel('Planet Mass (Earth-masses)')
        ylabel('Planet Radii (Earth-radii)')
        grid(which='minor')#,linestyle=':',linewidth=0.5,alpha=0.5)
        fig.subplots_adjust(right=right)
        xt = [1,3,10,30,100,300]
        xticks(xt,xt)
        xlim(1,300)
        cax = fig.add_axes(cax_pos) # setup colorbar axes. 
        cbar = colorbar(cax=cax)
        cbar.set_label('Equilibrium Temp (K)')
        plt.sca(ax)

    return fig, ax

def subsat2_rp_rhop(label_all=False):
    ss = subsaturn.literature.load_ss()
    ss['x_offset'] = 5
    ss['y_offset'] = 5
    ss['pl_name'] = ss.pl_name.replace('EPIC-211736671 b','EPIC-2117 b')
    ss.index = ss.pl_name
    b_thiswork = ss.pl_name.str.contains('K2-39|K2-27|K2-32|EPIC-2117')
    ss_thiswork = ss[b_thiswork]
    ss_lit = ss[~b_thiswork]

    all_fontsize = 0 
    if label_all:
        all_fontsize = 10

    fig,ax = plot_ttv_rv_teq(
        ss_lit, 'pl_rade', 'pl_dens', 
        ann_kw=dict(fontsize=all_fontsize),
        scat_kw=dict(s=100)
    )
    ax.legend(bbox_to_anchor=(1.03, 1), loc=2, borderaxespad=0.)

    plot_ttv_rv_teq(
        ss_thiswork, 'pl_rade', 'pl_dens', fig0=fig,ax0=ax,
        ann_kw=dict(fontsize=10,fontweight='bold'),
        scat_kw=dict(s=200)
    )

def subsat2_mp_rp(label_all=False):
    ss = subsaturn.literature.load_ss()
    ss['x_offset'] = 5
    ss['y_offset'] = 5
    ss['pl_name'] = ss.pl_name.replace('EPIC-211736671 b','EPIC-2117 b')
    ss.index = ss.pl_name
    b_thiswork = ss.pl_name.str.contains('K2-39|K2-27|K2-32|EPIC-2117')
    ss_thiswork = ss[b_thiswork]
    ss_lit = ss[~b_thiswork]

    all_fontsize = 0 
    if label_all:
        all_fontsize = 10

    fig,ax = plot_ttv_rv_teq(
        ss_lit, 'pl_masse', 'pl_rade', mode='mp-rp',
        ann_kw=dict(fontsize=all_fontsize),
        scat_kw=dict(s=100)
    )
    ax.legend(bbox_to_anchor=(1.03, 1), loc=2, borderaxespad=0.)

    plot_ttv_rv_teq(
        ss_thiswork, 'pl_masse', 'pl_rade', mode='mp-rp',fig0=fig,ax0=ax,
        ann_kw=dict(fontsize=10,fontweight='bold'),
        scat_kw=dict(s=200)
    )

tex_cmf = '$M_{\mathregular{core}}$ /$M_{\mathregular{P}}$'
tex_mcore = '$M_{\mathregular{core}}$ (Earth-masses)'
tex_menv = '$M_{\mathregular{env}}$ (Earth-masses)'
tex_mp = '$M_{\mathregular{P}}$ (Earth-masses)'

@format_cmf
@format_teq
def subsat2_teq_cmf():
    ss = read_ss()
    errorbar_ecc(ss, 'pl_teq', 'pl_cmf', xerr=True, yerr=True,fmt='.')    

@format_masse
@format_teq
def subsat2_teq_mp():
    ss = read_ss()
    semilogy()
    errorbar_ecc(ss, 'pl_teq', 'pl_masse', xerr=True, yerr=True,fmt='.')    
    ylabel(tex_mp)

@format_masse
@format_teq
def subsat2_teq_menv():
    ss = read_ss()
    semilogy()
    errorbar_ecc(ss, 'pl_teq', 'pl_menv', xerr=True, yerr=True,fmt='.')    
    ylabel(tex_menv)

@format_masse
@format_teq
def subsat2_teq_mcore():
    ss = read_ss()
    semilogy()
    errorbar_ecc(ss, 'pl_teq', 'pl_mcore', xerr=True, yerr=True,fmt='.')    
    ylabel(tex_mcore)

@format_masse
@format_pnum
def subsat2_pnum_mp():
    ss = read_ss()
    semilogy()
    errorbar_pnum(ss, 'pl_masse', fmt='.')    
    ylabel(tex_mp)
    legend(loc='lower left')

@format_cmf
@format_pnum
def subsat2_pnum_cmf():
    ss = read_ss()
    errorbar_pnum(ss, 'pl_cmf', fmt='.')    
    ylabel(tex_cmf)

@format_masse
@format_pnum
def subsat2_pnum_mcore():
    ss = read_ss()
    semilogy()
    errorbar_pnum(ss, 'pl_mcore', fmt='.')    
    ylabel(tex_mcore)

@format_masse
@format_pnum
def subsat2_pnum_menv():
    ss = read_ss()
    semilogy()
    errorbar_pnum(ss, 'pl_menv', fmt='.')    
    ylabel(tex_menv)
    
@format_masse
@format_st_metfe
def subsat2_st_metfe_pl_mp():
    ss = read_ss()
    ss = ss.drop(['Kepler-413 b','GJ 436 b'])
    semilogy()
    errorbar_ecc(ss, 'st_metfe', 'pl_masse', xerr=True, yerr=True,fmt='.')    
    ylabel(tex_mp)
    gcf().set_tight_layout(True)

@format_masse
@format_st_metfe
def subsat2_st_metfe_pl_mcore():
    ss = read_ss()
    ss = ss.drop(['Kepler-413 b','GJ 436 b'])
    semilogy()
    errorbar_ecc(ss, 'st_metfe', 'pl_mcore', xerr=True, yerr=True,fmt='.')    
    ylabel(tex_mcore)
    yt = [1,3,10,30,100]
    yticks(yt,yt)
    xlim(-0.3,0.5)
    gcf().set_tight_layout(True)

@format_masse
@format_st_metfe
def subsat2_st_metfe_pl_menv():
    ss = read_ss()
    ss = ss.drop(['Kepler-413 b','GJ 436 b'])
    semilogy()
    errorbar_ecc(ss, 'st_metfe', 'pl_menv', xerr=True, yerr=True,fmt='.')    
    ylabel(tex_menv)

@format_cmf
@format_st_metfe
def subsat2_st_metfe_pl_cmf():
    ss = read_ss()
    ss = ss.drop(['Kepler-413 b','GJ 436 b'])
    errorbar_ecc(ss, 'st_metfe', 'pl_cmf', xerr=True, yerr=True,fmt='.')    
    ylabel(tex_cmf)
    gcf().set_tight_layout(True)
