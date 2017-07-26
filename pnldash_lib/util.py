import os.path

def getsize(path):
    if not os.path.exists(path):
        return 0
    if path.endswith('nhdr'):
        return os.path.getsize(path)/1024.0/1024.0 + \
                getsize(path[:-4]+'raw') + \
                getsize(path[:-4]+'raw.gz')
    return os.path.getsize(path)/1024.0/1024.0
