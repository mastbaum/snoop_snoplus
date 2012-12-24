'''Utilities for talking to RAT over the network.

Basically a Python reimplementation of OutNetProc. Please replace this with the
actual processor once we create a shared library for all of RAT.
'''

import array
from rat import ROOT

class NetRAT(object):
    '''A connection to a RAT server.

    Based on RAT's OutNetProc by Stan.

    :param retries: Attempt to process an event this many times
    :param check_version: Verify that the client and server are running
                          identical RAT versions
    '''
    def __init__(self, retries=5, check_version=True):
        self.socket = None
        self.host_list = []
        self.retries = retries
        self.check_version = check_version

    def process(self, ds):
        '''Send an event to RAT for processing.

        :param ds: A RAT.DS.Root object to process
        :returns: A processed RAT.DS.Root
        '''
        git_revision = ds.GetRatRevision()

        for i in range(self.retries):
            if self.socket is None:
                self._pick_server(git_revision)

            send_result = self.socket.SendObject(ds)

            if send_result == -1:
                print 'error sending event'
                self.socket = None
                continue

            message = ROOT.TMessage()
            read_result = self.socket.Recv(message)

            if read_result < 0:
                if read_result == 0:
                    print 'rat server closed connection'
                if read_result == -1:
                    print 'read error receiving processed event'
                if read_result == -4:
                    print 'socket has no data'

                self.socket = None
                continue

            new_ds = message.ReadObject(ROOT.RAT.DS.Root.Class())

            if not new_ds:
                print 'unable to read processed ds'
                self.socket = None
                continue

            ds = ROOT.RAT.DS.Root(new_ds)

            return ds

    def add_host(self, host, port):
        '''Add a host to the server pool.

        :param host: Server hostname
        :param port: Server port: int, list, or string range '1234-1235'
        '''
        if '-' in str(port):
            port_string = str(port)
            min_port, max_port = map(int, port_string.split('-'))
            port = xrange(min_port, max_port+1)

        if not hasattr(port, '__iter__'):
            port = [port]

        self.host_list.append((host, port))

    def _pick_server(self, client_git_revision):
        '''Choose a server from the host list.

        :param client_git_version: Local git revision, must match that of
                                   server if check is enabled.
        :returns: ROOT.TSocket connected to chosen server
        '''
        if self.socket is not None:
            self.socket.Close()

        min_load = 1e9
        min_load_socket = None
        min_load_git_revision = None

        for host, ports in self.host_list:
            for port in ports:
                socket, load, git_revision = self._connect(host, port)

                if self.check_version and (client_git_revision != git_revision):
                    print 'server/client rat version mismatch'
                    print 'client:', client_git_revision, type(client_git_revision)
                    print 'server:', git_revision, type(git_revision)
                    socket.Close()
                    continue

                if socket and (min_load_socket is None or load < min_load):
                    min_load = load
                    min_load_git_revision = git_revision
                    min_load_socket = socket

        self.socket = socket

    def _connect(self, host, port):
        '''Establish a server connection.

        :param hostname: Hostname of server
        :param port: Server port
        :returns: (TSocket, load_average, git_rev) tuple
        '''
        socket = ROOT.TSocket(host, port)

        if not socket.IsValid():
            print 'could not connect to %s:%i' % (host, port)
            return None, None, None

        message = ROOT.TMessage()
        read_result = socket.Recv(message)

        if read_result == 0:
            print 'Host bailed reading header'
            return None, None, None

        elif read_result == -1:
            print 'Socket read error on', socket
            return None, None, None

        elif read_result == -4:
            print 'Empty header from', socket
            return None, None, None

        else:
            # when asked for n bytes, root gives us n-1 then a \0
            server_git_version = array.array('c', ['0'] * 41)
            message.ReadString(server_git_version, 41)
            load = ROOT.Double(0)
            message.ReadDouble(load)

            return socket, float(load), server_git_version.tostring()[:-1]

