import threading
import time


#lock = threading.Lock()

def task(name, delay):
    for i in range(5):
        time.sleep(delay)
        print(f"{name}: {i}")
        # with lock:
        #     print(f"{name}: {i}")

# Создаем потоки
thread1 = threading.Thread(target=task, args=("Task 1", 1))
thread2 = threading.Thread(target=task, args=("Task 2", 2))

# Запускаем потоки
thread1.start()
thread2.start()

# Ждем завершения потоков
thread1.join()
thread2.join()

print("All tasks completed")






