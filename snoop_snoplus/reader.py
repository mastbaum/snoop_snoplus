from snoop.reader import ROOTFileReader
from rat import ROOT

class PackedReader(ROOTFileReader):
    '''Read packed records from the `PackRec` branch of the `PackT` tree in a
    packed ROOT file.
    '''
    def __init__(self, filenames):
        tree_name = 'PackT'
        branch_name = 'PackRec'
        obj = ROOT.RAT.DS.PackedRec()
        ROOTFileReader.__init__(self, filenames, tree_name, branch_name, obj)

class AirfillReader(ROOTFileReader):
    '''Read packed events from the `PackEv` branch of the `PackT` tree in an
    air fill-format packed ROOT file.
    '''
    def __init__(self, filenames):
        tree_name = 'PackT'
        branch_name = 'PackEv'
        obj = ROOT.RAT.DS.PackedEvent()
        ROOTFileReader.__init__(self, filenames, tree_name, branch_name, obj)

class RATReader(ROOTFileReader):
    '''Read RAT DSes from the `ds` branch of the `T` tree in a normal
    (unpacked) RAT ROOT file.
    '''
    def __init__(self, filenames):
        tree_name = 'T'
        branch_name = 'ds'
        obj = ROOT.RAT.DS.Root()
        ROOTFileReader.__init__(self, filenames, tree_name, branch_name, obj)

