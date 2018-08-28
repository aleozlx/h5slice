import os, sys, re, subprocess
import h5py, gzip
import numpy as np
from twisted.internet import reactor, protocol

def get_h5slice(fname, h5path, idx, as_type):
    with h5py.File(fname) as f:
        return f[h5path][idx].astype(as_type)

def get_h5ls(fname):
    if os.path.exists(fname) and os.path.splitext(fname)[1] == '.h5':
        return subprocess.run(['h5ls', '-r', fname], stdout=subprocess.PIPE).stdout

def query_to_slice(query):
    try:
        return slice(*tuple(map(int, query.split(':')))) if ':' in query else int(query)
    except:
        pass

def postprocess(im):
    if len(im.shape) in [4, 3]:
        mean = [103.939, 116.779, 123.68]
        bands = im.shape[-1]
        if bands == 1:
            imout = (im[..., 0] + max(mean))
        elif bands == 3:
            imout = im[..., ::-1].copy()
            imout[..., 0] += mean[0]
            imout[..., 1] += mean[1]
            imout[..., 2] += mean[2]
        elif bands >=4:
            # flatten bands into batch
            
        imout /= 255.0
        np.clip(imout, 0.0, 1.0, out = imout)
        return imout
    else:
        return im

def process_query(request, transport):
    fname, h5path, query, as_type = request.split('\t')
    print('In', fname, h5path, query, as_type)
    if query == 'h5ls':
        transport.write(get_h5ls(fname))
        return

    idx = query_to_slice(query)
    as_type = as_type.strip()
    if idx and as_type in ('i4', 'f4'):
        imtest = postprocess(get_h5slice(fname, h5path, idx, as_type))
        print('Out', imtest.shape, imtest.dtype, np.min(imtest), np.max(imtest))
        transport.write(gzip.compress(imtest.tobytes(), 3))

class H5Slice(protocol.Protocol):
    def dataReceived(self, data):
        process_query(data.decode("ascii"), self.transport)
        self.transport.loseConnection()

def main():
    factory = protocol.ServerFactory()
    factory.protocol = H5Slice
    reactor.listenTCP(8000, factory, interface='0.0.0.0')
    reactor.run()

if __name__ == '__main__':
    main()
