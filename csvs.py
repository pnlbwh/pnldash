#!/usr/bin/env python
from plumbum import cli, local
import csv
import yaml
import os.path
import glob
import time

PARAM_HDR = ['projectPath', 'grantId', 'description', 'paramId', 'pipelineDescription', 'param',
             'paramValue']
PATH_HDR = ['projectPath', 'paramId', 'pathKey', 'caseid',
            'path', 'sizeMB', 'modtime', 'modtimeStr', 'exists']

def concat(l):
    return l if l == [] else [item for sublist in l for item in sublist]

def readCaselistItem(s):
    if '/' in s:
        with open(s, 'r') as f:
            return [line.split()[0] for line in f.read().splitlines()]
    return [s]

def readCaselist(caselist):
    if isinstance(caselist, unicode):
        return readCaselistItem(caselist)
    elif isinstance(caselist, list):
        return concat(map(readCaselistItem, caselist))
    else:
        raise Exception("caselist field must be string or list type")


def getsize(path):
    pathP = local.path(path)
    if not pathP.exists():
        return 0
    if '.nhdr' in pathP.suffixes:
        return os.path.getsize(path)/1024.0/1024.0 + \
            getsize(pathP.with_suffix('.raw').__str__()) + \
            getsize(pathP.with_suffix('.raw.gz').__str__())
    return os.path.getsize(path)/1024.0/1024.0


class Csvs(cli.Application):

    outdir = cli.SwitchAttr(
        ['-o'],
        cli.ExistingDirectory,
        mandatory=False,
        help="Output directory",
        default=local.cwd)

    @cli.positional(cli.ExistingFile)
    def main(self, projectyml):
        with open(projectyml, 'r') as f:
            yml = yaml.load(f, Loader=yaml.loader.BaseLoader) # TODO force read each field as a string

        projectInfo = yml['projectInfo']
        projectPath = projectyml.dirname.replace('-', '/')

        paramsCsv = self.outdir / 'params.csv'
        pathsCsv = self.outdir / 'paths.csv'

        self.outdir.mkdir()

        with open(paramsCsv, 'w') as fparamsCsv:
            csvwriterParams = csv.writer(fparamsCsv)
            csvwriterParams.writerow(PARAM_HDR)
            with open(pathsCsv, 'w') as fpathsCsv:
                csvwriterPaths = csv.writer(fpathsCsv)
                csvwriterPaths.writerow(PATH_HDR)

                for paramId, pipeline in enumerate(yml['pipelines']):
                    for param, paramVal in pipeline['parameters'].items():
                        csvwriterParams.writerow(
                            [projectPath,
                             projectInfo['grantId'],
                             projectInfo['description'], paramId, pipeline['description'], param,
                             paramVal])
                    caseids = readCaselist(pipeline['paths']['caselist'])
                    caseidString = pipeline['paths']['caseid']
                    if not isinstance(caseidString, unicode):
                        raise Exception("caseid field needs to be in quotes to protect its value: TODO force read yml fields as strings")
                    for pathKey, pathTemplate in pipeline['paths'].items():
                        if pathKey == 'caselist' or pathKey == 'caseid':
                            continue
                        for caseid in caseids:
                            path = pathTemplate.replace(caseidString, caseid)
                            paths = glob.glob(path)  # could be a glob pattern
                            if not paths:  # no glob
                                paths = [path]
                            for path in paths:
                                mtime = None
                                mtimeStr = None
                                exists = False
                                sizeMB = None
                                if os.path.exists(path):
                                    mtime = os.path.getmtime(path)
                                    mtimeStr = time.strftime(
                                        '%Y-%m-%d %H:%M:%S',
                                        time.localtime(mtime))
                                    exists = True
                                    sizeMB =  getsize(path)
                                csvwriterPaths.writerow(
                                    [projectPath,
                                     paramId, pathKey, caseid, path, sizeMB,
                                     mtime, mtimeStr, exists])
            print("Made '{}'".format(paramsCsv))
            print("Made '{}'".format(pathsCsv))


if __name__ == '__main__':
    Csvs.run()
