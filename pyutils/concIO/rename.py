import asyncio
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from os import listdir, rename
from os.path import join, splitext

from MODULES.benchmarking.benchmarking_time import timedblock

# import aiofiles


def rename_one_by_one(src="tmp"):
    for filename in listdir(src):
        name, ext = splitext(filename)
        dest_filename = f"{name}-new{ext}"
        src_path = join(src, filename)
        dest_path = join(src, dest_filename)

        rename(src_path, dest_path)


def rename_one_by_one_for_batch(files, src="tmp"):
    for filename in files:
        name, ext = splitext(filename)
        dest_filename = f"{name}-new{ext}"
        src_path = join(src, filename)
        dest_path = join(src, dest_filename)

        rename(src_path, dest_path)


#        print(f".renamed {src_path} to {dest_path}")


async def rename_async_file(filename, src):
    name, ext = splitext(filename)
    dest_filename = f"{name}-new{ext}"
    src_path = join(src, filename)
    dest_path = join(src, dest_filename)

    # await rename(src_path, dest_path)
    rename(src_path, dest_path)


async def async_rename_files(src="tmp"):
    tasks = [rename_async_file(filename, src) for filename in listdir(src)]
    await asyncio.gather(*tasks)


def rename_with_TreadPoolExecutor(src="tmp", threads=10):
    with ThreadPoolExecutor(threads) as exe:
        _ = [exe.submit(rename_one_by_one, name, src) for name in listdir(src)]


def rename_with_TreadPoolExecutor_batch(src="tmp", threads=10):
    files = listdir(src)
    chunksize = val if (val := round(len(files) / threads)) else len(files)

    with ThreadPoolExecutor(threads) as exe:
        for i in range(0, len(files), chunksize):
            filenames = files[i : (i + chunksize)]
            _ = exe.submit(rename_one_by_one_for_batch, filenames, src)


def rename_with_ProcessPoolExecutor(src="tmp", workers=4):
    with ProcessPoolExecutor(workers) as exe:
        _ = [exe.submit(rename_one_by_one, name, src) for name in listdir(src)]


def rename_with_ProcessPoolExecutor_batch(src="tmp", workers=4):
    files = listdir(src)
    chunksize = val if (val := round(len(files) / workers)) else len(files)

    with ProcessPoolExecutor(workers) as exe:
        for i in range(0, len(files), chunksize):
            filenames = files[i : (i + chunksize)]
            _ = exe.submit(rename_one_by_one_for_batch, filenames, src)


if __name__ == "__main__":
    # the fastest solution from the cheked ones, is the
    # rename_with_TreadPoolExecutor, threads = 100       :0.00152 seconds
    # this function will be refactored and saved for later usage

    with timedblock("rename_one_by_one                                  "):
        rename_one_by_one()

    # with timedblock("rename_with_TreadPoolExecutor, threads = 10        "):
    #     rename_with_TreadPoolExecutor()

    with timedblock("rename_with_TreadPoolExecutor, threads = 100       "):
        rename_with_TreadPoolExecutor(threads=100)

    # with timedblock("rename_with_TreadPoolExecutor, threads = 200       "):
    #     rename_with_TreadPoolExecutor(threads=200)
    #
    # with timedblock("rename_with_TreadPoolExecutor_batch, threads=10    "):
    #     rename_with_TreadPoolExecutor_batch()
    #
    # with timedblock("rename_with_TreadPoolExecutor_batch, threads=100   "):
    #     rename_with_TreadPoolExecutor_batch(threads=100)
    #
    # with timedblock("rename_with_ProcessPoolExecutor, workers = 4       "):
    #     rename_with_ProcessPoolExecutor()
    #
    # with timedblock("rename_with_ProcessPoolExecutor_batch, workers = 4 "):
    #     rename_with_ProcessPoolExecutor_batch()
    #
    # with timedblock("async_rename_files                                 "):
    #     asyncio.run(async_rename_files())
