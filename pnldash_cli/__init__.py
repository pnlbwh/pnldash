import sys
from plumbum import cli

class ParamApp(cli.Application):
    paramid = cli.SwitchAttr(
        ['-p', '--paramid'],
        int,
        default=0,
        mandatory=False,
        help="parameter id, run pipeline only for this parameter combination")

    def validate(self, maxid):
        if self.paramid > maxid:
            print("parameter id must be smaller than {}".format(maxid))
            sys.exit(1)
