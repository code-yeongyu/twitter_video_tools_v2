from multiprocessing.dummy import Pool
from typing import Any, Callable, Iterable

from .istarmap import istarmap as _  # noqa


def execute_parallel(
    func: Callable[..., Any],
    args: Iterable[tuple[Any, ...]],
):
    pool = Pool()
    results = pool.istarmap(func, args)
    for result in results:
        yield result
