import threading

def worker():
    print("Worker thread is running")

# Создаем поток
thread = threading.Thread(target=worker)

# Запускаем поток
thread.start()

# Ждем завершения потока
thread.join()
