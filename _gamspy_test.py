from gamspy import Container, Variable
c = Container()
try:
    v = Variable(c, 'x', type='free', lower=-1, upper=1)
    print('ok')
except Exception as exc:
    print('error:', exc)

