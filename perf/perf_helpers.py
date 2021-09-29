from time import monotonic_ns as now
import statistics as st
from collections import namedtuple

stats_result = namedtuple(
    "stats_result", ("center", "spread_upper", "spread_lower", "N")
)


def runtime(fun, runtime=1, divisor=1, *args, **kwargs):
    """Call and time fun() repeatedly for 'runtime' seconds"""
    rt = runtime * 1e9  # convert to ns
    T = []
    t0 = t2 = now()
    while (t2 - t0) < rt:
        t1 = now()
        fun(*args, **kwargs)
        t2 = now()
        T.append(t2 - t1)
    return [t / divisor for t in T]


def ncalls(fun, ncalls=1000, divisor=1, *args, **kwargs):
    """Call and time fun() repeatedly 'ncalls' times"""
    T = []
    for _ in range(ncalls):
        t1 = now()
        fun(*args, **kwargs)
        t2 = now()
        T.append(t2 - t1)
    return [t / divisor for t in T]


def rms(X):
    """Root mean square"""
    return st.sqrt(st.mean([x * x for x in X]))


def stats(T, center_fun=st.median, spread_fun=rms, remove_outliers=True):
    """Calculate the central tendency, and upper/lower spread of the timing data"""

    if remove_outliers:
        # https://doi.org/10.1016/j.jesp.2013.03.013
        center = st.median(T)
        mad = (1.4826) * st.median(abs(t - center) for t in T)
        T = [t for t in T if abs((t - center) / mad) < 3]

    center = center_fun(T)
    Tu = [t - center for t in T if t > center]
    Tl = [t - center for t in T if t <= center]
    spread_upper = spread_fun(Tu) if Tu else 0
    spread_lower = spread_fun(Tl) if Tl else 0
    return stats_result(center, spread_upper, spread_lower, len(T))
