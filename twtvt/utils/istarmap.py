# type: ignore
import multiprocessing.pool
from typing import Any, Callable, Iterable


def istarmap(self: multiprocessing.pool.Pool, func: Callable[..., Any], iterable: Iterable[Any], chunk_size: int = 1):
    '''starmap-version of imap

    from: https://stackoverflow.com/questions/57354700/starmap-combined-with-tqdm
    '''
    self._check_running()
    if chunk_size < 1:
        raise ValueError("'chunk_size' must be 1 or larger")

    task_batches = multiprocessing.pool.Pool._get_tasks(func, iterable, chunk_size)
    result = multiprocessing.pool.IMapIterator(self)
    self._taskqueue.put((
        self._guarded_task_generation(result._job, multiprocessing.pool.starmapstar, task_batches),
        result._set_length,
    ))
    return (item for chunk in result for item in chunk)


multiprocessing.pool.Pool.istarmap = istarmap
