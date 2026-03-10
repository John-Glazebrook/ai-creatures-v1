import ctypes

x = ctypes.c_int(7)
x.value += 5
print(x.value)

y = ctypes.c_void_p(0)
