import pstats
from pstats import SortKey

pstats.Stats('result').strip_dirs().sort_stats(SortKey.TIME).print_stats(10)
