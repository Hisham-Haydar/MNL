from gamspy import Container, Variable
c = Container()
try:
    Variable(c, 'x', type='free', lb=-1, ub=1)
    print('lb/ub ok')
except Exception as exc:
    print('lb/ub error', exc)
try:
    Variable(c, 'y', type='free', lo=-1, up=1)
    print('lo/up ok')
except Exception as exc:
    print('lo/up error', exc)

