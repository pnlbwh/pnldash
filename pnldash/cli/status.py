import pandas as pd
from plumbum import cli, local, FG
from .. import make_extra
from ..config import *

def _heading(s):
    return s + '\n' + len(s) * '-'

class Status(cli.Application):
    """Prints a summary of the project disk usage."""

    def main(self):
        pd.options.display.float_format = '{:,.2f}'.format

        extra_table = make_extra()
        print('')
        print(_heading('Extra Image Files'))
        if not extra_table.empty:
            sizeMBsum = extra_table['sizeMB'].sum()
            print("{} unaccounted image file(s) found.".format(
                len(extra_table['path'])))
            print("disk usage (G): {:.2f}".format(sizeMBsum / 1024.0))
        else:
            print("No unaccounted files found.")
        print('')

        print(_heading('Pipeline Files'))
        paths_table = pd.read_csv(PATHS_CSV)
        agg = {
            'exists': {'completed': 'sum',
                       'missing': lambda x: (~x).sum(),
                       'total': 'size'},
            'sizeMB': {'size (G)': lambda x: x.sum()/1024}
        }

        # suppress pandas FutureWarning regarding nested dictionary aggregations until
        # a replacement solution is found
        import warnings
        warnings.simplefilter(action='ignore', category=FutureWarning)

        st = paths_table.groupby(['pipelineId', 'pathKey']).agg(agg)
        st.columns = st.columns.droplevel(0)
        st.reset_index()
        st['completed'] = st['completed'].astype(int)
        print(st)

        pipelineDiskUsage = paths_table['sizeMB'].sum() / 1024.0
        print("disk usage (G): {:.2f}".format(pipelineDiskUsage))

        du_table = pd.read_csv(DU_CSV)
        totalDiskUsage = du_table['diskUsageG'].iloc[0]
        print('')
        print(_heading("Project Directory"))
        print("disk usage (G): {:.2f}".format(totalDiskUsage))
