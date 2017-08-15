base=$(readlink -m ${BASH_SOURCE[0]}) && base=${base%/*}
export PATH=$PATH:$base/scripts
export PNLDASH_DB=$base/db
