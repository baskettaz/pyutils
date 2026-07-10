from typing import Iterable, Union
from functools import partial
from pathlib import Path
from os import remove
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor


__all__ = [
    "sequential_del",
    "ThreadPoolExecutor_del",
    "ProcessPoolExecutor_del",
    "ThreadPoolExecutorInBatch_del",
    "ProcessPoolExecutorInBatch_del",
]


def sequential_del(files: list[Path]) -> None:
    _ = [remove(file) for file in files]


def execute_with_pool(
    files: list[Path],
    workers: int,
    executor: Union[ProcessPoolExecutor, ThreadPoolExecutor],
) -> None:
    with executor(workers) as exe:
        exe.submit(sequential_del, files)

        # exe.shutdown(wait=True)


def ThreadPoolExecutor_del(files: list[Path], workers: int):
    func = partial(execute_with_pool, executor=ThreadPoolExecutor)
    return func(files, workers)


def ProcessPoolExecutor_del(files: list[Path], workers: int):
    func = partial(execute_with_pool, executor=ProcessPoolExecutor)
    return func(files, workers)


def exe_in_chunks(
    files: Iterable,
    chunksize: int,
    executor: Union[ProcessPoolExecutor, ThreadPoolExecutor],
    workers: int,
) -> None:
    with executor(workers) as exe:
        for i in range(0, len(files), chunksize):
            chunk_files = files[i : (i + chunksize)]

            exe.submit(sequential_del, chunk_files)

        # exe.shutdown(wait=True)


def execute_with_pool_batch(
    files: list[Path],
    workers: int,
    executor: Union[ProcessPoolExecutor, ThreadPoolExecutor],
) -> None:
    if chunksize := round(len(files) / workers) > 1:
        exe_in_chunks(files, chunksize, executor, workers)
    else:
        execute_with_pool(files, workers, executor)


def ThreadPoolExecutorInBatch_del(files: list[Path], workers: int):
    func = partial(execute_with_pool_batch, executor=ThreadPoolExecutor)
    return func(files, workers)


def ProcessPoolExecutorInBatch_del(files: list[Path], workers: int):
    func = partial(execute_with_pool_batch, executor=ProcessPoolExecutor)
    return func(files, workers)


if __name__ == "__main__":
    pass
