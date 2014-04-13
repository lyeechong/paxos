import time

currentTimeMillis = lambda: int(round(time.time() * 1000))

test = currentTimeMillis() 
print test
time.sleep(1)
print currentTimeMillis()
