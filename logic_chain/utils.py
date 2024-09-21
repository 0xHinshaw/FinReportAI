import time
import json

def timeit(method):
    def wrapper(*args, **kw):
        start_time = time.time()
        result = method(*args, **kw)
        end_time = time.time()
        print(f'{method.__name__} Execution time: {end_time - start_time}')
        return result
    return wrapper
    
def write_json(path, value):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(value, f, ensure_ascii=False, indent=4)