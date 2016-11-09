from astropy import units as u
from astropy import constants as c
import numpy as np

def tidal_circularization_timescale(Qp, P, Mp, Mstar, Rp, a=None):
    """
    Tidal circularization timescale

    How long does it take for a planet's eccentricity to damp away?

    Equation 9 from Rasio et al. 1996, rewrite of Goldreich and Soter 1966.

    Args:

        Q (float): tidal quality factor of planet. Very
            uncertain. Some points of reference:
            - Jupiter ~ 10^5 (Ioanno and Lindzen 1993)
            - Saturn 6-7 x 10^4 presence of moons (Goldreich and Soter 1966). 
            - Uranus > 7 x 10^4 presence of moons (Goldreich and Soter 1966). 
        P (float): Orbital period (d)
        Mp (float): mass of planet (Earth-masses)
        Mstar (float): mass of star (Solar-masses)
        Rp (float): radius of planet (Earth radii)
        a (float, optional): Semi-major axis of planet (AU). If not input, 
            it is calculated from Kepler's third law.

    tau_e = \frac{4}{63} \frac{Q}{n} \frac{Mp}{\Mstar} (\frac{a}{Rp})^5

    Returns:
         (float): circularization timescale (Gyr)
    """

    Mp = Mp * u.M_earth
    Mstar = Mstar * u.M_sun
    Rp = Rp * u.R_earth
    P = P * u.day
    n = 2 * np.pi / P

    if a is None:
        a = (c.G * Mstar * P**2 / 4 / np.pi**2 )**(1/3.0)
        a = a.to(u.AU)
        print a
    else:
        a = a * u.AU
        
    e_time_planet = (4.0/63.0) * (Qp/n) * (Mp/Mstar) * (a / Rp)**5
    e_time_planet = e_time_planet.to(u.Gyr).value
    return e_time_planet
    
