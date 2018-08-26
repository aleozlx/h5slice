import os, sys, re
import h5py, gzip
import numpy as np
from twisted.internet import reactor, protocol

def get_h5slice(fname, h5path, idx, as_type):
    with h5py.File(fname) as f:
	    return f[h5path][idx].astype(as_type)

def parse_query(query):
    try:
        return slice(*tuple(map(int, query.split(':')))) if ':' in query else int(query)
    except:
        pass

class H5Slice(protocol.Protocol):
    def dataReceived(self, data):
        fname, h5path, query, as_type = data.decode("ascii").split('\t')
        print('In', fname, h5path, query, as_type)
        idx = parse_query(query)
        as_type = as_type.strip()
        if idx and as_type in ('i4', 'f4'):
            imtest = get_h5slice(fname, h5path, idx, as_type)
            print('Out', imtest.shape, imtest.dtype, np.min(imtest), np.max(imtest))
            self.transport.write(gzip.compress(imtest.tobytes(), 3))
        self.transport.loseConnection()

def main():
    factory = protocol.ServerFactory()
    factory.protocol = H5Slice
    reactor.listenTCP(8000, factory)
    reactor.run()

if __name__ == '__main__':
    main()
