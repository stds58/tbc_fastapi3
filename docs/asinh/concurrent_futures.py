import concurrent.futures
import time

def task(name, delay):
    for i in range(5):
        time.sleep(delay)
        print(f"{name}: {i}")

# Используем ThreadPoolExecutor для управления потоками
with concurrent.futures.ThreadPoolExecutor() as executor:
    # Запускаем задачи в пуле потоков
    future1 = executor.submit(task, "Task 1", 1)  # Task 1 с задержкой 1 секунда
    future2 = executor.submit(task, "Task 2", 2)  # Task 2 с задержкой 2 секунды

    # Ждем завершения задач
    concurrent.futures.wait([future1, future2])

print("All tasks completed")


