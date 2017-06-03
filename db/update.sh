#!/usr/bin/env bash

dirs=$(find "$PWD" -type d | tail -n +2)
for d in ${dirs}; do
    echo $d
    projdir=$(basename $d | sed 's,---,/,g' | sed 's,^,/,')
    pushd $projdir
    pnlproj diff
    pnlproj push
    popd
done
