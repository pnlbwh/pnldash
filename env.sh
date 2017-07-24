base=$(readlink -m ${BASH_SOURCE[0]}) && base=${base%/*}
export PATH=$PATH:$base
export PROJECTS_DB=~/soft/pnldash/db
