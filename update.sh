#!/usr/bin/env bash


help() {
    echo -e "Updates csvs, crawls and computes diff for a project directory.

Usage:
    ${0##*/} <db/ymlfile>"
}

if [ ! "${1:-}" ]; then
    help
    exit 0
fi

yml=$1
stem=$(basename $yml)
stem=${stem%.*}
echo $stem

rm -f _csvs/${stem}--paths.csv
rm -f _csvs/${stem}--params.csv
rm -f _crawler/${stem}.txt
rm -f _diff/${stem}.txt

make _diff/${stem}.txt
make _csvs/paths.csv _csvs/params.csv
