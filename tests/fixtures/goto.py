def f():
  pass

class C:
  pass

variable = f if random.choice( [ 0, 1 ] ) else C


def foo():
  print 'foo'

alias = foo
_list = [ 1, None, alias ]
inception = _list[ 2 ]

inception()
