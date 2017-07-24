from plumbum import local
CACHE_DIR = local.path(".pnldash")
PROJECT_YML = local.path('pnldash.yml')
PROJECTS_DB_ENV = 'PROJECTS_DB'
PATHS_CSV = CACHE_DIR / "paths.csv"
PARAMS_CSV = CACHE_DIR / "params.csv"
FIND_TXT = CACHE_DIR / "all_image_files.txt"
DU_CSV = CACHE_DIR / "du.csv"
EXTRA_CSV = CACHE_DIR / "unaccounted_files.csv"
