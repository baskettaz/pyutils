from typing import Union, Iterable
from functools import partial
from shutil import copy
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, Future

__all__ = [
    "copy_files",
    "copy_with_ThreadPool",
    "copy_with_ThreadPool_in_batch",
    "copy_with_ProcessPool",
    "copy_with_ProcessPool_in_batch",
    "conc_copy",
]


def copy_files(files: Iterable, destination: Path) -> None:
    destination.mkdir(exist_ok=True)
    _ = [copy(file, destination) for file in files]


def copy_with_ThreadPool(files: Iterable, destination: Path, workers=10) -> None:
    destination.mkdir(exist_ok=True)

    with ThreadPoolExecutor(workers) as exe:
        _ = [exe.submit(copy, file, destination) for file in files]


def exe_in_chunks(
    files: Iterable,
    chunksize: int,
    executor: Union[ProcessPoolExecutor, ThreadPoolExecutor],
    destination: Path,
    workers: int,
):
    with executor(workers) as exe:
        for i in range(0, len(files), chunksize):
            chunk_files = files[i : (i + chunksize)]

            exe.submit(copy_files, chunk_files, destination)


def copy_with_ThreadPool_in_batch(
    files: Iterable, destination: Path, workers=10
) -> None:
    destination.mkdir(exist_ok=True)

    if chunksize := round(len(files) / workers) > 1:
        exe_in_chunks(files, chunksize, ThreadPoolExecutor, destination, workers)
    else:
        copy_with_ThreadPool(files, destination, workers)


def copy_with_ProcessPool(files: Iterable, destination: Path, workers=4) -> None:
    destination.mkdir(exist_ok=True)

    with ProcessPoolExecutor(workers) as exe:
        _ = [exe.submit(copy, file, destination) for file in files]


def copy_with_ProcessPool_in_batch(
    files: Iterable, destination: Path, workers: int = 4
) -> None:
    destination.mkdir(exist_ok=True)

    if chunksize := round(len(files) / workers) > 1:
        exe_in_chunks(files, chunksize, ProcessPoolExecutor, destination, workers)
    else:
        copy_with_ProcessPool(files, destination, workers)


# ALIAS
conc_copy = partial(copy_with_ThreadPool, workers=150)

if __name__ == "__main__":
    pass
