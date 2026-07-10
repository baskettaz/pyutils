# **************************************************************** #
#                     STANDARD LIBRARY IMPORTS                     #
# **************************************************************** #
from os import makedirs, listdir
from os.path import join
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

# **************************************************************** #
#                          OTHER LIBRARIES                         #
# **************************************************************** #
from utils import con_delete
from test_files_creation import generate_file_data
from MODULES.benchmarking.benchmarking_time import ClassicalTimer, AsyncTimer

# **************************************************************** #
#                        MODULE VARIABLES                          #
# **************************************************************** #
module_timer = ClassicalTimer(name="read_comparisons")

NUM_LINE_NODES = 10
NUM_LINES = 5000

DATA = generate_file_data(num_line_nodes=NUM_LINE_NODES, num_lines=NUM_LINES)
NUM_FILES_TO_CREATE = 5000
WORKERS = 150
CPUs = 4
# **************************************************************** #


def mod_decorator(func):
    def wrapper(*args, **kwargs):
        f = module_timer(func)
        f(*args, **kwargs)
        con_delete(listdir("tmp"), "tmp")
        return lambda: None

    return wrapper


def save_file(filepath, data):
    with open(filepath, "w") as handle:
        handle.write(data)
        # print(f".saved {filepath}")


def generate_and_save(path, identifier):
    data = DATA
    filepath = join(path, f"data-{identifier:04d}.csv")
    save_file(filepath, data)


def multi_generate_and_save(path, identifiers):
    for identifier in identifiers:
        generate_and_save(path, identifier)


def threaded_multi_generate_and_save(path, identifiers, workers=WORKERS):
    with ThreadPoolExecutor(workers) as exe:
        for identifier in identifiers:
            _ = exe.submit(generate_and_save, path, identifier)


@mod_decorator
def sequential_write(path="tmp", num_files=NUM_FILES_TO_CREATE):
    makedirs(path, exist_ok=True)

    for i in range(num_files):
        generate_and_save(path, i)


@mod_decorator
def ThreadPoolExecutor_write(
    path="tmp", num_files=NUM_FILES_TO_CREATE, workers=WORKERS
):
    makedirs(path, exist_ok=True)

    with ThreadPoolExecutor(workers) as exe:
        _ = [exe.submit(generate_and_save, path, i) for i in range(num_files)]


@mod_decorator
def ProcessPoolExecutor_write(path="tmp", num_files=NUM_FILES_TO_CREATE, cpus=CPUs):
    makedirs(path, exist_ok=True)

    with ProcessPoolExecutor(cpus) as exe:
        _ = [exe.submit(generate_and_save, path, i) for i in range(num_files)]


@mod_decorator
def ProcessPoolExecutorInBatch_write(
    path="tmp", num_files=NUM_FILES_TO_CREATE, cpus=CPUs
):
    makedirs(path, exist_ok=True)

    identifiers = [i for i in range(num_files)]

    if (val := num_files // cpus) > 0:
        chunksize = val
    else:
        chunksize = num_files

    with ProcessPoolExecutor(cpus) as exe:
        for i in range(0, num_files, chunksize):
            ids = identifiers[i : (i + chunksize)]
            _ = [exe.submit(multi_generate_and_save, path, ids)]


@mod_decorator
def ProcessPoolExecutorInBatchThreaded_write(
    path="tmp", num_files=NUM_FILES_TO_CREATE, cpus=CPUs
):
    makedirs(path, exist_ok=True)

    identifiers = [i for i in range(num_files)]

    if (val := num_files // cpus) > 0:
        chunksize = val
    else:
        chunksize = num_files

    with ProcessPoolExecutor(cpus) as exe:
        for i in range(0, num_files, chunksize):
            ids = identifiers[i : (i + chunksize)]
            _ = [exe.submit(threaded_multi_generate_and_save, path, ids)]


if __name__ == "__main__":
    sequential_write()
    ThreadPoolExecutor_write()
    ProcessPoolExecutor_write()
    ProcessPoolExecutorInBatch_write()
    ProcessPoolExecutorInBatchThreaded_write()  # <--- WINNER !

    # Summary:
    # --------
    module_timer.get_all_timed()
