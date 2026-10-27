import numpy as np


def nash(s0, s1):
    return s0 * s1


def utilitarian(s0, s1):
    return s0 + s1


def egalitarian(s0, s1):
    return np.minimum(s0, s1)


WELFARES = {"nash": nash, "utilitarian": utilitarian, "egalitarian": egalitarian}
