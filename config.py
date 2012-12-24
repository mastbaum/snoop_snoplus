# configuration for snoop, snoplus edition

# sample period in seconds
sample_period = 60

# python paths to processors
processor_paths = [
    ('snoop_snoplus.processors', ['snoop_snoplus'])
]

# keyword arguments
processor_kwargs = {
    'count': {'interval': 2000},
    'reconstruction': {'rat_servers': [('localhost', 7770)]}
}

# Writer to handle output
from snoop.writer import PrintWriter
writer = PrintWriter()

# Reader from which to get events
#from snoop_snoplus.reader import AirfillReader
#reader = AirfillReader('./sample_data/file.root')
from snoop.reader import DispatchReader
reader = DispatchReader('localhost')

