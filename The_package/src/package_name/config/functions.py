"""
    The functions used in the default values of settings.py
"""

from scipy.stats import qmc


def PoissonDiskDistribution(lower_x, upper_x, lower_y, upper_y, radius=100,
                         ncanidates=7, optimization=None):
    engine = qmc.PoissonDisk(d=2, radius=radius,
                             ncandidates=ncanidates, optimization=optimization,
                             l_bounds=[lower_x, lower_y], u_bounds=[upper_x, upper_y])
    return engine.fill_space()
