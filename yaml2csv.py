#!/usr/bin/env python
from plumbum import cli, local
import csv
import yaml
import os.path
import glob
import time


PROJECTS_DB = local.path('_data')
PARAM_HDR = ['projectName', 'projectPath', 'description', 'paramId',
                   'param', 'paramValue']
PATH_HDR = ['projectName', 'projectPath', 'paramId', 'pathKey',
                    'caseid', 'path', 'exists', 'modtime', 'modtimeStr']

def readFileLines(fn):
    with open(fn, 'r') as f:
        return f.read().splitlines()

class App(cli.Application):

    outdir = cli.SwitchAttr(['-o'], cli.ExistingDirectory, mandatory=False, help="Output directory", default=local.cwd)

    def main(self, ymlfile):
        ymlfile = local.path(ymlfile)
        with open(ymlfile, 'r') as f:
            yml = yaml.load(f)

        projectInfo = yml['projectInfo']

        paramsCsv = self.outdir / '{}--params.csv'.format(ymlfile.stem)
        pathsCsv = self.outdir / '{}--paths.csv'.format(ymlfile.stem)

        with open(paramsCsv, 'w') as fparamsCsv:
            csvwriterParams = csv.writer(fparamsCsv)
            csvwriterParams.writerow(PARAM_HDR)
            with open(pathsCsv, 'w') as fpathsCsv:
                csvwriterPaths = csv.writer(fpathsCsv)
                csvwriterPaths.writerow(PATH_HDR)

                for paramId, pipeline in enumerate(yml['pipelines']):
                    for param, paramVal in pipeline['parameters'].items():
                        csvwriterParams.writerow([projectInfo['projectName'],
                                            projectInfo['projectPath'],
                                            projectInfo['grantId'],
                                            projectInfo['description'],
                                            paramId, param, paramVal])
                    caseids = readFileLines(pipeline['paths']['caselist'])
                    caseidString = pipeline['paths']['caseid']
                    for pathKey, pathTemplate in pipeline['paths'].items():
                        if pathKey == 'caselist' or pathKey == 'caseid':
                            continue
                        for caseid in caseids:
                            path = pathTemplate.replace(caseidString, caseid)
                            paths = glob.glob(path) # could be a glob pattern
                            if not paths: # no glob
                                paths = [path]
                            for path in paths:
                                mtime = None
                                mtimeStr = None
                                exists = False
                                if os.path.exists(path):
                                    mtime = os.path.getmtime(path)
                                    mtimeStr = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(mtime))
                                    exists = True
                                csvwriterPaths.writerow(
                                    [projectInfo['projectName'],
                                     projectInfo['projectPath'],
                                     paramId,
                                     pathKey, caseid, path,
                                     exists,
                                     mtime,
                                     mtimeStr
                                    ])
            print("Made '{}'".format(paramsCsv))
            print("Made '{}'".format(pathsCsv))


if __name__ == '__main__':
    App.run()
