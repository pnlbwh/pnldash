base=$(readlink -m ${BASH_SOURCE[0]}) && base=${base%/*}
export PATH=$PATH:$base
export PNL_PROJECTS_DB=~/soft/pnlproj/db
