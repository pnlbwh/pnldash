#!/usr/bin/env python
from plumbum import cli, local
import csv
import yaml
from collections import OrderedDict

PUBLISH_CONFIG_FILE = 'publish.yml'
PNLPROJECTSMETA = 'PNLPROJECTSMETA'

TEMPLATE="""\
projectInfo:
    projectName: {}
    projectPath: {}
    grantId:
    description:
pipelines:
    - parameters:
        version_FreeSurfer: 5.3.0
        hash_UKFTractography: 421a7ad
        hash_tract_querier: e045eab
        hash_BRAINSTools: 41353e8
        hash_trainingDataT1AHCC: d6e5990
      paths:
        fs: _data/003_GNX_007/std_fs0.mgz
        dwied: _data/003_GNX_007/std_dwied0.nrrd
        dwimask: _data/003_GNX_007/std_dwimask0.nrrd
        t1mask: _data/003_GNX_007/std_t1mask0.nrrd
        t1: _data/003_GNX_007/std_t10.nrrd
        wmql: _data/003_GNX_007/std_wmql0.vtk
        tractmeasures: _data/003_GNX_007/std_tractmeasures0.csv
        dwixc: _data/003_GNX_007/std_dwixc0.nrrd
        ukf: _data/003_GNX_007/std_ukf0.vtk
        t1xc: _data/003_GNX_007/std_t1xc0.nrrd
        fsindwi: _data/003_GNX_007/std_fsindwi0.nii.gz
        dwi: _data/003_GNX_007/std_dwi0.nhdr
        caseid: 003_GNX_007
        caselist: ./caselist.txt
""".format(local.cwd.name.__str__(), local.cwd.__str__())


def csvFromDict(d):
    s = ""
    hdr = 'projectName,projectPath,grantId,paramId,caselist,param,paramValue'
    row = ','.join(d.values())
    return hdr + '\n' + row


def readProjectInfo():
    with open(PUBLISH_CONFIG_FILE, 'r') as f:
        return yaml.load(f)


class Publish(cli.Application):
    def main(self, *args):
        if args:
            print("Unknown command {0!r}".format(args[0]))
            return 1
        if self.nested_command:
            return

        readAndSetSrcPaths()
        combos = readComboPaths(self.parent.paramsFile)
        projectInfo = readProjectInfo()

        paramsCsv = '_{}_publish_params.csv'.format(self.parent.name)
        pathsCsv = '_{}_publish_paths.csv'.format(self.parent.name)

        with open(paramsCsv, 'w') as fparamsCsv:
            csvwriter = csv.writer(fparamsCsv)
            hdr = ['projectName', 'projectPath', 'description', 'paramId',
                   'param', 'paramValue']
            csvwriter.writerow(hdr)
            with open(pathsCsv, 'w') as fpathsCsv:
                hdr = ['projectName', 'projectPath', 'paramId', 'pathKey',
                       'caseid', 'path', 'exists']
                csvwriter2 = csv.writer(fpathsCsv)
                csvwriter2.writerow(hdr)

                for combo in combos:
                    for k, v in combo['paramCombo'].items():
                        csvwriter.writerow([projectInfo['projectName'],
                                            projectInfo['projectPath'],
                                            projectInfo['description'],
                                            combo['paramId'], k, v])
                    for pathKey, subjectPaths in combo['paths'].items():
                        for subjectPath in subjectPaths:
                            csvwriter2.writerow(
                                [projectInfo['projectName'],
                                 projectInfo['projectPath'], combo['paramId'],
                                 pathKey, subjectPath.caseid, subjectPath.path,
                                 subjectPath.path.exists()])
            print("Made '{}'".format(paramsCsv))
            print("Made '{}'".format(pathsCsv))


@Publish.subcommand("init")
class Init(cli.Application):
    def main(self):
        represent_dict_order = lambda self, data: self.represent_mapping('tag:yaml.org,2002:map', data.items())
        yaml.add_representer(OrderedDict, represent_dict_order)

        with open(PUBLISH_CONFIG_FILE, 'w') as f:
            f.write(TEMPLATE)
        print("Made '{}'".format(PUBLISH_CONFIG_FILE))


@Publish.subcommand("push")
class Push(cli.Application):
    def main(self):
        import os
        centralRepo = os.environ.get(PNLPROJECTSMETA, None)
        if not centralRepo:
            errmsg = "Set '{}' environment variable first.".format(
                PNLPROJECTSMETA)
            raise Exception(errmsg)

        centralRepo = local.path(centralRepo)
        paramsCsv = local.path('_{}_publish_params.csv'.format(
            self.parent.parent.name))
        pathsCsv = local.path('_{}_publish_paths.csv'.format(
            self.parent.parent.name))

        if not paramsCsv.exists():
            errmsg = "'{}' does not exist, run 'publish' command first".format(
                paramsCsv)
            raise Exception(errmsg)
        if not pathsCsv.exists():
            errmsg = "'{}' does not exist, run 'publish' command first".format(
                pathsCsv)
            raise Exception(errmsg)

        dest = centralRepo / readProjectInfo()['projectName']

        # if dest.exists():
        #     errmsg = "Destination direction '{}' already exists, so you must choose a different project name (change it in '{}')".format(dest, PUBLISH_CONFIG_FILE)
        #     raise Exception(errmsg)

        dest.mkdir()
        pathsCsv.copy(dest)
        paramsCsv.copy(dest)

        print("Successfully published '{}' to '{}'".format(pathsCsv, dest))
        print("Successfully published '{}' to '{}'".format(paramsCsv, dest))

if __name__ == '__main__':
    Publish.run()
