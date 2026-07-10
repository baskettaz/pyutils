# **************************************************************** #
#                     STANDARD LIBRARY IMPORTS                     #
# **************************************************************** #
import asyncio
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from os import listdir
from os.path import join

import aiofiles
from MODULES.benchmarking.benchmarking_time import AsyncTimer, ClassicalTimer

# **************************************************************** #
#                          OTHER LIBRARIES                         #
# **************************************************************** #
from test_files_creation import generate_all_files

# **************************************************************** #
#                        MODULE VARIABLES                          #
# **************************************************************** #
module_timer = ClassicalTimer(name="read_comparisons")
# async_module_timer = AsyncTimer(name = "read_comparisons",
#                                 print_timer=True)
async_module_timer = AsyncTimer()
async_module_timer.timers = module_timer.timers  # timers sync !

NUM_FILES_TO_CREATE = 1000
WORKERS = 150
CPUs = 4
SEMAPHOR_LIMIT = 200
# **************************************************************** #


def mod_decorator(func):
    def wrapper(*args, **kwargs):
        f = module_timer(func)
        return f(*args, **kwargs)

    return wrapper


def load_file(filepath):
    with open(filepath) as handle:
        return handle.read(), filepath


async def load_file_async(filepath, semaphore):
    async with semaphore:
        async with aiofiles.open(filepath) as handle:
            return (await handle.read(), filepath)


def load_files(filepaths):
    tmp = []
    ta = tmp.append

    for filepath in filepaths:
        with open(filepath) as handle:
            ta(handle.read())
    return tmp, filepaths


def load_files_conc(filepaths):
    with ThreadPoolExecutor(len(filepaths)) as exe:
        futures = [exe.submit(load_file, name) for name in filepaths]
        data_list = [future.result() for future in futures]
        return (data_list, filepaths)


@mod_decorator
def read_one_by_one(path="tmp"):
    paths = [join(path, filepath) for filepath in listdir(path)]

    for filepath in paths:
        data, filepath = load_file(filepath)
        print(f".loaded {filepath}")


@mod_decorator
def ThreadPoolExecutor_load(path="tmp", workers=WORKERS):
    paths = [join(path, filepath) for filepath in listdir(path)]

    with ThreadPoolExecutor(workers) as executor:
        futures = [executor.submit(load_file, p) for p in paths]

        for future in as_completed(futures):
            data, filepath = future.result()
            print(f".loaded{filepath}")


@mod_decorator
def ThreadPoolExecutorInBatch_load(path="tmp", workers=WORKERS):
    paths = [join(path, filepath) for filepath in listdir(path)]

    if (val := len(paths) // workers) > 0:
        chunksize = val
    else:
        chunksize = len(paths)

    with ThreadPoolExecutor(workers) as executor:
        futures = []
        fa = futures.append
        for i in range(0, len(paths), chunksize):
            filepaths = paths[i : (i + chunksize)]
            future = executor.submit(load_files, filepaths)
            fa(future)

        for future in as_completed(futures):
            _, filepaths = future.result()
            for filepath in filepaths:
                print(f".loaded{filepath}")


@mod_decorator
def ProcessPoolExecutor_load(path="tmp", cpus=CPUs):
    paths = [join(path, filepath) for filepath in listdir(path)]

    with ProcessPoolExecutor(cpus) as executor:
        futures = [executor.submit(load_file, p) for p in paths]

        for future in as_completed(futures):
            data, filepath = future.result()
            print(f".loaded{filepath}")


@mod_decorator
def ProcessPoolExecutorInBatch_load(path="tmp", cpus=CPUs):
    paths = [join(path, filepath) for filepath in listdir(path)]

    if (val := len(paths) // cpus) > 0:
        chunksize = val
    else:
        chunksize = len(paths)

    with ProcessPoolExecutor(cpus) as executor:
        futures = []
        fa = futures.append
        for i in range(0, len(paths), chunksize):
            filepaths = paths[i : (i + chunksize)]
            future = executor.submit(load_files, filepaths)
            fa(future)

        for future in as_completed(futures):
            _, filepaths = future.result()
            for filepath in filepaths:
                print(f".loaded{filepath}")


@mod_decorator
def ProcessPoolExecutorAndThreadsPool_load(path="tmp", cpus=CPUs):
    paths = [join(path, filepath) for filepath in listdir(path)]

    if (val := len(paths) // cpus) > 0:
        chunksize = val
    else:
        chunksize = len(paths)

    with ProcessPoolExecutor(cpus) as executor:
        futures = []
        fa = futures.append
        for i in range(0, len(paths), chunksize):
            filepaths = paths[i : (i + chunksize)]
            future = executor.submit(load_files_conc, filepaths)
            fa(future)

        for future in as_completed(futures):
            _, filepaths = future.result()
            for filepath in filepaths:
                print(f".loaded{filepath}")


# @mod_decorator
@async_module_timer
async def Async_load(path="tmp", sem_lim=SEMAPHOR_LIMIT):
    paths = [join(path, filepath) for filepath in listdir(path)]

    semaphore = asyncio.Semaphore(sem_lim)
    tasks = [load_file_async(filepath, semaphore) for filepath in paths]

    for task in asyncio.as_completed(tasks):
        data, filepath = await task
        print(f".loaded {filepath}")


if __name__ == "__main__":
    if not listdir("tmp"):
        generate_all_files(num_files=NUM_FILES_TO_CREATE)

    read_one_by_one()
    ThreadPoolExecutor_load()
    ThreadPoolExecutorInBatch_load()
    ProcessPoolExecutor_load()  # <--- exibits the best time
    ProcessPoolExecutorInBatch_load()
    ProcessPoolExecutorAndThreadsPool_load()

    asyncio.run(Async_load())

    # Summary:
    # --------
    module_timer.get_all_timed()
    # module_timer.plot_all_timed()
    # async_module_timer.get_all_timed()
