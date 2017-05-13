YMLS=$(wildcard db/*yml)
CSVS_PATHS:=$(YMLS:db/%.yml=_csvs/%--paths.csv)
CSVS_PARAMS:=$(YMLS:db/%.yml=_csvs/%--params.csv)
DIFFS:=$(YMLS:db/%.yml=_diff/%.txt)

.SECONDARY:
.PHONY: all clean update diff
all: _csvs/paths.csv _csvs/params.csv

diff: $(DIFFS)

clean:
	@rm -rf _csvs

update:
	@make clean
	@make

_csvs/%--paths.csv: db/%.yml
	@mkdir -p $(dir $@)
	./yaml2csv.py $< -o $(dir $@)

_csvs/%--params.csv: db/%.yml
	@mkdir -p $(dir $@)
	./yaml2csv.py $< -o $(dir $@)

_csvs/paths.csv: $(CSVS_PATHS)
	csvstack $(CSVS_PATHS) > $@

_csvs/params.csv: $(CSVS_PARAMS)
	csvstack $(CSVS_PARAMS) > $@

_crawler/%.txt:
	@mkdir -p $(dir $@)
	./crawler.py $(join /, $(subst -,/, $*)) -o $@

_diff/%.txt: _csvs/%--paths.csv _crawler/%.txt
	@mkdir -p $(dir $@)
	./diffpaths.py $(join _csvs/,$*--paths.csv) $(join _crawler/,$*.txt) -o $@
