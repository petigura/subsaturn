from matplotlib.pylab import *
import matplotlib.patheffects as PathEffects # needed for Oreo font
import seaborn as sns
sns.set(font='Helvetica')
sns.set_style("whitegrid")
import numpy as np
import subsaturn.literature
import subsaturn.lopez
import pandas as pd

def err_errorbar(df, key):
    val = df[key]
    valerr = np.vstack([-1.0*df[key+'err2'],df[key+'err1']])
    return val, valerr

def read_ss():
    ss = pd.read_excel(subsaturn.lopez.sscmffn,index_col=0)
    return ss 


def plot_rhop_rp(df, fig0=None, ax0=None, offsets=None, ann_kw={}, scat_kw={}):
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
        fig, ax = subplots(figsize=(6, 5))
    else:
        fig = fig0
        ax = ax0

    x, xerr = err_errorbar(df, 'pl_rade')
    y, yerr = err_errorbar(df, 'pl_dens')

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

    if fig0 is None:
#        cbar = colorbar(fraction=0.03)
        semilogy()
        
        xlabel('Planet Size (Earth-radii)')
        ylabel('Density (g/cc)')
        yt = [0.05, 0.07, 0.1, 0.2, 0.3, 0.4, 0.5, 0.7, 1, 2, 3]
        yticks(yt,yt)
        grid(which='minor')#,linestyle=':',linewidth=0.5,alpha=0.5)
        fig.subplots_adjust(right=0.85)
        ylim(0.05,6)
        xlim(3.5,8.5)

        cax = fig.add_axes([0.9, 0.15, 0.02, 0.5]) # setup colorbar axes. 
        cbar = colorbar(cax=cax)
        cbar.set_label('Equilibrium Temp (K)')
        plt.sca(ax)

    return fig, ax

def subsat2_rp_rhop(label_all=False):
    ss = subsaturn.literature.load_ss()
    ss['x_offset'] = 5
    ss['y_offset'] = 5
    ss.ix['Kepler-18 c','x_offset'] = -30 
    ss.ix['Kepler-18 c','y_offset'] = -10

    b_thiswork = ss.pl_name.str.contains('K2-39|K2-27|K2-32|EPIC-2117')
    ss_thiswork = ss[b_thiswork]
    ss_lit = ss[~b_thiswork]

    all_fontsize = 0 
    if label_all:
        all_fontsize = 10

    fig,ax = plot_rhop_rp(
        ss_lit,ann_kw=dict(fontsize=all_fontsize),scat_kw=dict(s=100)
    )
    ax.legend(bbox_to_anchor=(1.03, 1), loc=2, borderaxespad=0.)

    plot_rhop_rp(
        ss_thiswork,fig0=fig,ax0=ax,
        ann_kw=dict(fontsize=10,fontweight='bold'),
        scat_kw=dict(s=200)
    )


tex_cmf = '$M_{\mathregular{core}}$ /$M_{\mathregular{P}}$'
tex_mcore = '$M_{\mathregular{core}}$ (Earth-masses)'
tex_menv = '$M_{\mathregular{env}}$ (Earth-masses)'
tex_mp = '$M_{\mathregular{P}}$ (Earth-masses)'

def subsat2_teq_cmf():
    ss = read_ss()
    x, xerr = err_errorbar(ss, 'pl_teq')
    y, yerr = err_errorbar(ss, 'pl_cmf')
    errorbar(x, y, xerr=xerr, yerr=yerr, fmt='.')    
    xlabel('Equilibrium Temp (K)')
    ylabel(tex_cmf)
    ylim(0,1)

def subsat2_pnum_cmf():
    ss = read_ss()
    x = ss.pl_pnum
    x += linspace(-0.1,0.1,len(x))
    y, yerr = err_errorbar(ss, 'pl_cmf')
    errorbar(x, y, yerr=yerr, fmt='.')    
    xlabel('Number of Planets')
    ylabel(tex_cmf)
    ylim(0,1)
    xlim(0,7)

def subsat2_pnum_mcore():
    ss = read_ss()
    x = ss.pl_pnum
    x += linspace(-0.1,0.1,len(x))
    y, yerr = err_errorbar(ss, 'pl_mcore')
    semilogy()
    errorbar(x, y, yerr=yerr, fmt='.')    
    xlabel('Number of Planets')
    ylabel(tex_mcore)
    xlim(0,7)
    yt = [1,3,10,30,100]
    yticks(yt,yt)

def subsat2_pnum_menv():
    ss = read_ss()
    x = ss.pl_pnum
    x += linspace(-0.1,0.1,len(x))
    y, yerr = err_errorbar(ss, 'pl_menv')
    semilogy()
    errorbar(x, y, yerr=yerr, fmt='.')    
    xlabel('Number of Planets')
    ylabel(tex_menv)
    xlim(0,7)
    yt = [1,3,10,30,100]
    yticks(yt,yt)

def subsat2_pnum_mp():
    ss = read_ss()
    x = ss.pl_pnum
    x += linspace(-0.1,0.1,len(x))
    y, yerr = err_errorbar(ss, 'pl_masse')
    semilogy()
    errorbar(x, y, yerr=yerr, fmt='.')    
    xlabel('Number of Planets')
    ylabel(tex_mp)
    xlim(0,7)
    yt = [1,3,10,30,100]
    yticks(yt,yt)

def subsat2_st_metfe_pl_masse():
    ss = read_ss()
    ss = ss.drop('Kepler-413 b')

    x, xerr = err_errorbar(ss, 'st_metfe')
    y, yerr = err_errorbar(ss, 'pl_masse')
    semilogy()
    errorbar(x, y, yerr=yerr, fmt='.')    
    xlabel('[Fe/H]')
    ylabel(tex_mp)
    yt = [1,3,10,30,100]
    yticks(yt,yt)
    xlim(-0.3,0.5)

def subsat2_st_metfe_pl_mcore():
    ss = read_ss()
    ss = ss.drop('Kepler-413 b')
    x, xerr = err_errorbar(ss, 'st_metfe')
    y, yerr = err_errorbar(ss, 'pl_mcore')
    semilogy()
    errorbar(x, y, yerr=yerr, fmt='.')    
    xlabel('[Fe/H]')
    ylabel(tex_mcore)
    yt = [1,3,10,30,100]
    yticks(yt,yt)
    xlim(-0.3,0.5)

def subsat2_st_metfe_pl_menv():
    ss = read_ss()
    ss = ss.drop('Kepler-413 b')
    x, xerr = err_errorbar(ss, 'st_metfe')
    y, yerr = err_errorbar(ss, 'pl_menv')
    semilogy()
    errorbar(x, y, yerr=yerr, fmt='.')    
    xlabel('[Fe/H]')
    ylabel(tex_menv)
    yt = [1,3,10,30,100]
    yticks(yt,yt)

st_metfmlim = (-0.3,0.5)

def subsat2_st_metfe_pl_cmf():
    ss = read_ss()
    ss = ss.drop('Kepler-413 b')
    x, xerr = err_errorbar(ss, 'st_metfe')
    y, yerr = err_errorbar(ss, 'pl_cmf')
    errorbar(x, y, yerr=yerr, fmt='.')    
    xlabel('[Fe/H]')
    ylabel(tex_cmf)
    ylim(0,1)
    xlim(*st_metfmlim)
