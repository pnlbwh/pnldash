YMLS=$(wildcard db/*yml)
CSVS:=$(YMLS:.yml=--paths.csv)
CSVS:=$(CSVS:db/%=_csvs/%)

.PHONY: all
all: $(CSVS)

_csvs/%--paths.csv: db/%.yml
	./yaml2csv.py $< -o $(dir $@)
