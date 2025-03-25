import time

# Прямое вычисление
start = time.time()
for _ in range(1000000):
    offset = (max(10, 1) - 1) * 20
print("Direct calculation:", time.time() - start)


# Вызов функции
def get_offset_from_pagination(pagination):
    return (max(10, 1) - 1) * 20


start = time.time()
for _ in range(1000000):
    offset = get_offset_from_pagination({"page": 10, "page_size": 20})
print("Function call:", time.time() - start)
