def f():
  pass

class C:
  pass

variable = f if random.choice( [ 0, 1 ] ) else C
