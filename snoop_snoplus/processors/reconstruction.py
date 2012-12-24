from collections import deque
import numpy as np
from snoop.processor import Processor, ProcessorAbort
from rat import ROOT
from snoop_snoplus.netrat import NetRAT

class Reconstruction(Processor):
    '''Gather statistics on event reconstruction performance.

    Sends events to a RAT server (running InNetProducer) to processing.

    In ``rat_servers``, "portspec" means an int, list, or string range like
    '1234-1237'.

    :param rat_servers: List of RAT server addresses which will reconstruct
                        events as (host, portspec) tuples
    :param history: Histogram the previous `history` events
    '''
    name = 'reconstruction'
    def __init__(self, rat_servers, fitter='fit', history=100):
        self.fitter = fitter
        self.history = history

        # connect to rat server(s)
        self.netrat = NetRAT(check_version=False)
        for server, port in rat_servers:
            self.netrat.add_host(server, port)

        # initialize ring buffer storage
        self.x = deque([], self.history)
        self.y = deque([], self.history)
        self.z = deque([], self.history)
        self.nhits = deque([], self.history)
        self.failed = 0

        Processor.__init__(self)

    def event(self, event):
        if not isinstance(event, ROOT.RAT.DS.Root):
            raise ProcessorAbort('unknown event type')

        #if event.GetRunID() == 0:
        #    event.SetRunID(100000)
        event.SetRunID(100000)

        # send to rat server for processing
        event = self.netrat.process(event)

        try:
            fit = event.GetEV(0).GetFitResult('fit')
        except Exception:
            self.failed += 1
            print 'fit unavailable'
            return

        if fit.GetValid():
            pos = fit.GetVertex(0).GetPosition()
            self.x.append(pos.X())
            self.y.append(pos.Y())
            self.z.append(pos.Z())
            self.nhits.append(event.GetEV(0).nhits)
        else:
            self.failed += 1
            print 'fit not valid'

    def sample(self):
        doc = {
            'x': self.x,
            'y': self.y,
            'z': self.z,
            'nhits': self.nhits,
            'failed': self.failed,
        }

        return doc

    def load(self, p):
        self.x = p.x
        self.y = p.y
        self.z = p.z
        self.nhits = p.nhits
        self.fitter = p.fitter
        self.history = p.history
        self.failed = p.failed
        self.netrat = p.netrat

