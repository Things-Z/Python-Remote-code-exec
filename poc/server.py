from multiprocessing.managers import BaseManager

class Q():
    pass

class QManager(BaseManager):
    pass

q = Q()
def get_q():
    return q

QManager.register('get_q', callable=get_q)
m = QManager(address=('', 8500), authkey=b'')

s = m.get_server()
s.serve_forever()