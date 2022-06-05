from threading import Thread


def separated_thread(function):
    def wrapper(*args):
        return Thread(name=function.__name__, target=function, args=(*args,)).start()

    return wrapper
