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

        paths_table = pd.read_csv(PATHS_CSV)
        from numpy import count_nonzero
        # agg = {'path': 'count', 'sizeMB': 'sum', 'exists': 'sum'}
        # agg = {'sizeMB': {'sizeMB':'sum'},
        #         'exists': {'exists': count_nonzero, 'missing': lambda x: count_nonzero(~x) },
        #        'path': {'total': 'count'}
        #         }
        missing = lambda x: count_nonzero(~x)

        agg = {'sizeMB': ['sum'],
               'exists': [count_nonzero, missing],
               'path': ['count']}
        st = paths_table.groupby(['pipelineId', 'pathKey']).agg(agg)
        st['sizeG'] = st['sizeMB'] / 1024.0
        # st.rename(columns={'path':'total'}, inplace=True)
        print(_heading('Pipeline Files'))
        # print(st.to_string(index=False))
        print(st.to_string())
        pipelineDiskUsage = paths_table['sizeMB'].sum() / 1024.0
        print("disk usage (G): {:.2f}".format(pipelineDiskUsage))

        du_table = pd.read_csv(DU_CSV)
        totalDiskUsage = du_table['diskUsageG'].iloc[0]
        print('')
        print(_heading("Project Directory"))
        print("disk usage (G): {:.2f}".format(totalDiskUsage))
