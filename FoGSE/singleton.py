
class Singleton(type):
    """
    Metaclass for defining singleton classes. Stolen from here: https://stackoverflow.com/a/6798042.

    Use like this:
    ```
        class MyClass(metaclass=Singleton):
            def __init__():
                pass
            #...
    ```
    """
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]