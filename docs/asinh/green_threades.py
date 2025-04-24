import gevent
from gevent import monkey


# Патчим стандартные библиотеки для совместимости с gevent
monkey.patch_all()

def task(name, delay):
    for i in range(5):
        print(f"{name}: {i}")
        gevent.sleep(delay)

# Создаём зелёные потоки
g1 = gevent.spawn(task, "Task 1", 1)
g2 = gevent.spawn(task, "Task 2", 2)

# Ждём завершения потоков
gevent.joinall([g1, g2])