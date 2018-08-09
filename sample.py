import numpy as np
from twisted.internet import reactor, protocol

class H5Slice(protocol.Protocol):
    def dataReceived(self, data):
        self.transport.write(np.eye(224, dtype='f4').tobytes())
        self.transport.loseConnection()

def main():
    factory = protocol.ServerFactory()
    factory.protocol = H5Slice
    reactor.listenTCP(8000, factory)
    reactor.run()

if __name__ == '__main__':
    main()
