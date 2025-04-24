import time
from multiprocessing import Pool
import multiprocessing
import math
import psutil


# Количество физических ядер
physical_cores = psutil.cpu_count(logical=False)

# Количество ядер (включая логические потоки Hyper-Threading)
logical_cores1 = psutil.cpu_count(logical=True)
logical_cores2 = multiprocessing.cpu_count()

def compute_factorial(x):
    return math.factorial(x)

if __name__ == '__main__':
    numbers = [10000, 20000, 30000, 40000]

    start_time = time.time()
    with Pool(physical_cores) as p:
        results = p.map(compute_factorial, numbers)
    print(f"physical_cores: {physical_cores}, Time: {time.time() - start_time}")

    print("==============================")

    for pool_size in [4, 6, 8, 12, physical_cores]:
        start_time = time.time()
        with Pool(pool_size) as p:
            results = p.map(compute_factorial, numbers)
        print(f"Pool size: {pool_size}, Time: {time.time() - start_time}")


