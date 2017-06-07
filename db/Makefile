YMLS=$(wildcard db/*yml)
CSVS_PATHS:=$(wildcard */paths.csv)
CSVS_PARAMS:=$(wildcard */params.csv)
CSVS_DIFFPATHS:=$(wildcard */diffPaths.csv)

.PHONY: all
all: dashboard.html

dashboard.html: dashboard.Rmd paths.csv params.csv diffPaths.csv
	R -e "library('rmarkdown'); render('dashboard.Rmd')"

paths.csv: $(CSVS_PATHS)
	csvstack $(CSVS_PATHS) > $@

params.csv: $(CSVS_PARAMS)
	csvstack $(CSVS_PARAMS) > $@

diffPaths.csv: $(CSVS_DIFFPATHS)
	csvstack $(CSVS_DIFFPATHS) > $@

##############################################################################
# Python Environments

.PHONY: conda virtualenv nix

virutalenv: _venv
nix: _pip_packages.nix
conda: environment.yml
	conda env create -f $<
	@echo "Now run 'source activate pnlpipe'"

_venv: requirements.txt
	virtualenv $@; $@/bin/pip install -r $<
	@echo "Now run 'source $@/bin/activate'"

_pip_packages.nix: requirements.txt
	if [ ! -d "_pip2nix" ]; then \
		git clone https://github.com/acowley/pip2nix _pip2nix; \
  fi
	cd _pip2nix; nix-shell --run 'pip2nix ../requirements.txt -o ../_pip_packages.nix'
	@echo "Now run 'nix-shell'"
