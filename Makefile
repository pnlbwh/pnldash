######################################################
.PHONY: conda
conda: requirements.txt
	while read requirement; do conda install --yes $$requirement; done < requirements.txt


######################################################
.PHONY: pip
pip: requirements.txt
	pip install -r requirements.txt


######################################################
.PHONY: venv
venv: _venv

_venv: requirements.txt
	virtualenv $@; $@/bin/pip install -r $<
	@echo "Now run 'source $@/bin/activate'"


######################################################
.PHONY: nix
nix: _pip_packages.nix

_pip_packages.nix: requirements.txt
	if [ ! -d "_pip2nix" ]; then \
		git clone https://github.com/acowley/pip2nix _pip2nix; \
  fi
	cd _pip2nix; nix-shell --run 'pip2nix ../requirements.txt -o ../_pip_packages.nix'
	@echo "Now run 'nix-shell'"
