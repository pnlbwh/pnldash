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
        st = paths_table.groupby(['pipelineId', 'pathKey']).apply(
            lambda g: pd.Series({
                    'completed': g.exists.sum(),
                    'missing': (~g.exists).sum(),
                    'total': g.exists.size,
                    'size (G)': g.sizeMB.sum()/1024
                })
        ).reset_index()
        st['completed'] = st['completed'].astype(int)
        st['missing'] = st['missing'].astype(int)
        st['total'] = st['total'].astype(int)
        for pipelineId in st['pipelineId'].unique():
            print('')
            print("Pipeline #{}\n".format(pipelineId+1))
            # df = st[st.pipelineId == pipelineId].drop('pipelineId',1)
            df = st[st.pipelineId == pipelineId]
            print(df.to_string(index=False))
            pipelineDiskUsage = df['size (G)'].sum()
            print("disk usage (G): {:.2f}".format(pipelineDiskUsage))

        pipelineDiskUsage = paths_table.drop_duplicates(subset='path')['sizeMB'].sum() / 1024.0
        print("\nTotal disk usage (G): {:.2f}".format(pipelineDiskUsage))

        du_table = pd.read_csv(DU_CSV)
        totalDiskUsage = du_table['diskUsageG'].iloc[0]
        print('')
        print(_heading("Project Directory"))
        print("disk usage (G): {:.2f}".format(totalDiskUsage))
