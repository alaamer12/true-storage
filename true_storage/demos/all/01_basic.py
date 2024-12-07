import time

# Data with duplicates
data = [i for i in range(20000)] * 2

# Measure list comprehension time
start = time.time()
list_result = [x for x in data]
list_time = time.time() - start

# Measure set comprehension time
start = time.time()
set_result = {x for x in data}
set_time = time.time() - start

print(f"List comprehension took: {list_time:.6f} seconds")
print(f"Set comprehension took: {set_time:.6f} seconds")
