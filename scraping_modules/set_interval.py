import threading

def set_interval(func, sec):
    def func_wrapper():
        set_interval(func, sec)
        func()
    t = threading.Timer(sec, func_wrapper)
    t.start()
    return t

if __name__ == '__main__':
    from autoScout24 import autoscout24
    #call autoscout24 initialement
    autoscout24()
    #call autoscout24 after 24 hours
    set_interval(autoscout24, 86400) #24h = 86400 seconde
