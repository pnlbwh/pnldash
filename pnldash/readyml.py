import yaml
from plumbum import local
from .config import PROJECT_YML
import sys
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s:%(name)s: %(message)s')
log = logging.getLogger(__name__)



def read_project_yml():
    with open(PROJECT_YML, 'r') as f:
        yml = yaml.load(f, Loader=yaml.loader.BaseLoader)

    required_keys = ['name', 'description', 'pipelines']

    for required_key in required_keys:
        if yml.get(required_key, None) == None:
            errmsg = "'{}' missing top level required key: {}. Edit 'pnldash.yml' and add a value for this key.".format(PROJECT_YML, required_key)
            print(errmsg)
            sys.exit(1)

    required_pipeline_keys = ['paths', 'parameters']
    required_path_keys = ['caselist', 'caseid_placeholder']

    for paramid, pipeline in enumerate(yml['pipelines']):

        for required in required_pipeline_keys:
            if not pipeline.get(required, None):
                log.error("Pipeline #{} is missing key '{}'. Edit pnldash.yml and add it.".format(paramid+1, required))
                sys.exit(1)
        for required in required_path_keys:
            if not pipeline['paths'].get(required,None):
                log.error("Pipeline #{}: 'paths' dictionary is missing key '{}'. Edit pnldash.yml and add it.".format(paramid+1, required))
                sys.exit(1)

    return yml
