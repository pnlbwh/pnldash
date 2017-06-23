from plumbum import local
import os.path

def getsize(path):
    pathP = local.path(path)
    if not pathP.exists():
        return 0
    if '.nhdr' in pathP.suffixes:
        return os.path.getsize(path)/1024.0/1024.0 + \
            getsize(pathP.with_suffix('.raw').__str__()) + \
            getsize(pathP.with_suffix('.raw.gz').__str__())
    return os.path.getsize(path)/1024.0/1024.0
