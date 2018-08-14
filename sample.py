import os, sys, re
import h5py, gzip
import numpy as np
from twisted.internet import reactor, protocol

# with h5py.File('/home/alex/datasets/ucm-sample.h5') as f:
# 	imtest = f['source/images'][12].astype('f4')
# 	print(imtest.dtype, imtest.shape)
# 	print(np.min(imtest), np.max(imtest))

def get_h5slice(fname, h5path, idx, as_type):
    with h5py.File(fname) as f:
	    return f[h5path][idx].astype(as_type)

class H5Slice(protocol.Protocol):
    def dataReceived(self, data):
        fname, h5path, idx, as_type = data.decode("ascii").split('\t')
        idx = int(idx)
        as_type = as_type.strip()
        imtest = get_h5slice(fname, h5path, idx, as_type)
        self.transport.write(gzip.compress(imtest.tobytes(), 3))
        self.transport.loseConnection()

def main():
    factory = protocol.ServerFactory()
    factory.protocol = H5Slice
    reactor.listenTCP(8000, factory)
    reactor.run()

if __name__ == '__main__':
    main()
