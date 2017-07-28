from __future__ import print_function
import yaml
import sys
from pnldash_config import *
from plumbum import cli, local, FG
from collections import OrderedDict

TEMPLATE = """\
name: intrust_std
grantId:
description: |
            Meaning of path keys:
            fs:      freesurfer subject directory
            dwied:   eddy corrected DWI
            dwimask: FSL bet generated DWI mask
            etc.
pipelines:
    - parameters:
        version_FreeSurfer: 5.3.0
        hash_UKFTractography: 421a7ad
        hash_tract_querier: e045eab
        hash_BRAINSTools: 41353e8
        hash_trainingDataT1AHCC: d6e5990
      paths:
        fs: _data/003_GNX_007/freesurfer/*/*
        dwied: _data/003_GNX_007/std_dwied0.nrrd
        dwimask: _data/003_GNX_007/std_dwimask0.nrrd
        t1mask: _data/003_GNX_007/std_t1mask0.nrrd
        t1: _data/003_GNX_007/std_t10.nrrd
        wmql: _data/003_GNX_007/wmql/*.vtk
        tractmeasures: _data/003_GNX_007/std_tractmeasures0.csv
        dwixc: _data/003_GNX_007/std_dwixc0.nrrd
        ukf: _data/003_GNX_007/std_ukf0.vtk
        t1xc: _data/003_GNX_007/std_t1xc0.nrrd
        fsindwi: _data/003_GNX_007/std_fsindwi0.nii.gz
        dwi: _data/003_GNX_007/std_dwi0.nhdr
        caseid: 003_GNX_007
        caselist: ./caselist.txt
""".format(local.cwd.name.__str__())


class Init(cli.Application):
    """Makes template 'pnldash.yml'"""

    force = cli.Flag(['-f', '--force'], default=False, help='force overwrite')

    def main(self):
        if PROJECT_YML.exists() and not self.force:
            msg = "'{}' already exists, to recreate it delete it first or use --force/-f flag.".format(
                PROJECT_YML)
            print(msg)
            sys.exit(1)

        represent_dict_order = lambda self, data: self.represent_mapping('tag:yaml.org,2002:map', data.items())
        yaml.add_representer(OrderedDict, represent_dict_order)

        with open(PROJECT_YML, 'w') as f:
            f.write(TEMPLATE)
        print("Made template '{}'.".format(PROJECT_YML))
