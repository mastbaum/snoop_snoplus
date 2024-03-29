from snoop.processor import Processor, ProcessorAbort
from rat import ROOT

class NHITStatistics(Processor):
    '''Compute some basic statistics on the number of hit channels per event'''
    name = 'nhit_statistics'
    def __init__(self):
        Processor.__init__(self)
        self.count = 0
        self.mean_nhit = 0.0
        self.count_lt_30 = 0
        self.count_gte_30 = 0

    def process(self, nhit):
        '''Process a single event. May be called several times per `event` if
        the data structure contains multiple detector events (like a
        RAT::DS::Root does).
        '''
        self.count += 1

        try:
            self.mean_nhit = self.mean_nhit + (nhit - self.mean_nhit) / self.count

            if nhit < 30:
                self.count_lt_30 += 1
            else:
                self.count_gte_30 += 1

        except ZeroDivisionError:
            pass

    def event(self, event):
        if isinstance(event, ROOT.RAT.DS.PackedEvent):
            self.process(event.NHits)
        elif isinstance(event, ROOT.RAT.DS.Root):
            for iev in range(event.GetEVCount()):
                self.process(event.GetEV(iev).GetNhits())
        else:
            raise ProcessorAbort('unknown event type')

    def sample(self):
        doc = {
            'mean': self.mean_nhit,
            'count_lt_30': self.count_lt_30,
            'count_gte_30': self.count_gte_30
        }

        # reset state
        self.__init__()

        return doc

    def load(self, p):
        self.count = p.count
        self.mean_nhit = p.mean_nhit
        self.count_lt_30 = p.count_lt_30
        self.count_gte_30 = p.count_gte_30

