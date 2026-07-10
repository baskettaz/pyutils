# **************************************************************** #
#                     STANDARD LIBRARY IMPORTS                     #
# **************************************************************** #
from os import makedirs, listdir
from shutil import move
from os.path import join
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

# **************************************************************** #
#                          OTHER LIBRARIES                         #
# **************************************************************** #
from test_files_creation import generate_all_files
from MODULES.benchmarking.benchmarking_time import ClassicalTimer
from utils import con_delete

# **************************************************************** #
#                        MODULE VARIABLES                          #
# **************************************************************** #
module_timer = ClassicalTimer(name="move_comparisons")

NUM_FILES_TO_CREATE = 100
WORKERS = 150
CPUs = 4


# **************************************************************** #
def mod_decorator(func):
    def wrapper(*args, **kwargs):
        generate_all_files(num_files=NUM_FILES_TO_CREATE)  # decorate ...
        # print(f"Before   mv: {len(listdir('tmp'))}")
        f = module_timer(func)
        f(*args, **kwargs)
        # print(f"After    mv: {len(listdir('tmp'))}")
        con_delete(listdir(path="tmp2"), "tmp2", workers=WORKERS)  # undecorate ...
        # print(f"tmp2 clean?: {len(listdir('tmp2'))}")
        # print("-"*50)
        return None

    return wrapper


def move_file(filename, src, dest):
    src_path = join(src, filename)
    dest_path = join(dest, filename)
    move(src_path, dest_path)


def move_files(filenames, src, dest):
    for filename in filenames:
        move_file(filename, src, dest)


@mod_decorator
def sequential_move(src="tmp", dest="tmp2"):
    makedirs(dest, exist_ok=True)

    for filename in listdir(src):
        src_path = join(src, filename)
        dest_path = join(dest, filename)
        move(src_path, dest_path)


@mod_decorator
def ThreadPoolExecutor_move(src="tmp", dest="tmp2", workers=WORKERS):
    makedirs(dest, exist_ok=True)

    with ThreadPoolExecutor(workers) as exe:
        _ = [exe.submit(move_file, name, src, dest) for name in listdir(src)]


@mod_decorator
def ThreadPoolExecutorInBatch_move(src="tmp", dest="tmp2", workers=WORKERS):
    makedirs(dest, exist_ok=True)
    files = listdir(src)

    if (val := len(files) // workers) > 0:
        chunksize = val
    else:
        chunksize = len(files)

    with ThreadPoolExecutor(workers) as exe:
        for i in range(0, len(files), chunksize):
            filenames = files[i : (i + chunksize)]
            _ = exe.submit(move_files, filenames, src, dest)


@mod_decorator
def ProcessPoolExecutor_move(src="tmp", dest="tmp2", cpus=CPUs):
    makedirs(dest, exist_ok=True)

    with ProcessPoolExecutor(cpus) as exe:
        _ = [exe.submit(move_file, name, src, dest) for name in listdir(src)]


@mod_decorator
def ProcessPoolExecutorInBatch_move(src="tmp", dest="tmp2", workers=CPUs):
    makedirs(dest, exist_ok=True)
    files = listdir(src)
    if (val := len(files) // workers) > 0:
        chunksize = val
    else:
        chunksize = len(files)

    with ProcessPoolExecutor(workers) as exe:
        for i in range(0, len(files), chunksize):
            filenames = files[i : (i + chunksize)]
            _ = exe.submit(move_files, filenames, src, dest)


if __name__ == "__main__":
    sequential_move()
    ThreadPoolExecutor_move()
    ThreadPoolExecutorInBatch_move()
    ProcessPoolExecutor_move()
    ProcessPoolExecutorInBatch_move()

    # Summary:
    # --------
    module_timer.get_all_timed()
