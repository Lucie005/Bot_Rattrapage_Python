import atexit
from main import start, save_all

if __name__ == "__main__":
    atexit.register(save_all)

    start()