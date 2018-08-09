import h5py, gzip
import numpy as np
from twisted.internet import reactor, protocol

with h5py.File('/home/alex/datasets/ucm-sample.h5') as f:
	imtest = f['source/images'][12].astype('f4')
	print(imtest.dtype, imtest.shape)
	print(np.min(imtest), np.max(imtest))

class H5Slice(protocol.Protocol):
    def dataReceived(self, data):
        self.transport.write(gzip.compress(imtest.tobytes(), 3))
        self.transport.loseConnection()

def main():
    factory = protocol.ServerFactory()
    factory.protocol = H5Slice
    reactor.listenTCP(8000, factory)
    reactor.run()

if __name__ == '__main__':
    main()
