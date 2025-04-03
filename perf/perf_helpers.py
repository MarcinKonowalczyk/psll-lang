import math
import statistics as st
from collections import namedtuple
from time import perf_counter as now
from typing import Any, Callable

stats_result = namedtuple("stats_result", ("center", "spread_upper", "spread_lower", "N"))


def runtime(fun: Callable, runtime: float = 1.0, divisor: int = 1, *args: Any, **kwargs: Any) -> list:
    """Call and time fun() repeatedly for 'runtime' seconds"""
    T = []
    t0 = t2 = now()
    while (t2 - t0) < runtime:
        t1 = now()
        fun(*args, **kwargs)
        t2 = now()
        T.append(t2 - t1)
    return [t / divisor for t in T]


def ncalls(fun: Callable, ncalls: int = 1000, divisor: int = 1, *args: Any, **kwargs: Any) -> list:
    """Call and time fun() repeatedly 'ncalls' times"""
    T = []
    for _ in range(ncalls):
        t1 = now()
        fun(*args, **kwargs)
        t2 = now()
        T.append(t2 - t1)
    return [t / divisor for t in T]


def rms(X: list) -> float:
    """Root mean square"""
    return math.sqrt(st.mean([x * x for x in X]))


def stats(
    T: list,
    center_fun: Callable[[list], float] = st.median,
    spread_fun: Callable[[list], float] = rms,
    remove_outliers: bool = True,
) -> stats_result:
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
