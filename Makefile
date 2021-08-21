DOC_BUILD_DIR=/tmp/cvts-pages

.PHONY: initial-setup latest-cmake setup-valhalla setup-postgre venv sphinx-doc push-doc clean clean-sphinx-doc

initial-setup: latest-cmake setup-valhalla venv sphinx-doc setup-postgre

latest-cmake:
	sudo apt-get install -y libssl-dev
	cd /tmp && wget https://github.com/Kitware/CMake/releases/download/v3.21.0/cmake-3.21.0.tar.gz
	cd /tmp && tar -zxf cmake-3.21.0.tar.gz
	cd /tmp/cmake-3.21.0 && \
	    ./bootstrap && \
	    make && \
	    sudo make install

setup-valhalla:
	./scripts/setup-valhalla.sh

setup-postgre:
	# ---------------------------------------------------------------------
	# --------------BE CAREFUL: THIS DESTROYS THE EXISTING DB--------------
	# ---------------------------------------------------------------------
	echo "DROP DATABASE IF EXISTS ${CVTS_POSTGRES_DB};" > /tmp/cvts.sql
	echo "DROP USER IF EXISTS ${CVTS_POSTGRES_USER};" >> /tmp/cvts.sql
	echo "CREATE DATABASE ${CVTS_POSTGRES_DB};" >> /tmp/cvts.sql
	echo "CREATE USER ${CVTS_POSTGRES_USER} WITH ENCRYPTED PASSWORD '${CVTS_POSTGRES_PASS}';" >> /tmp/cvts.sql
	echo "GRANT ALL PRIVILEGES ON DATABASE ${CVTS_POSTGRES_DB} TO ${CVTS_POSTGRES_USER};" >> /tmp/cvts.sql
	chmod 777 /tmp/cvts.sql
	cd /tmp && sudo -u postgres psql -f /tmp/cvts.sql
	rm /tmp/cvts.sql
	. venv/bin/activate && bin/createpgdb

venv: clean
	rm -rf venv
	virtualenv -p python3 venv
	. ./venv/bin/activate && pip install -e .[dev]

sphinx-doc: clean-sphinx-doc
	. ./venv/bin/activate \
	    && cd doc && sphinx-apidoc -f -o ./source ../cvts \
	    && rm -f ./source/modules.rst
	echo "   :imported-members:" >> doc/source/cvts.rst
	echo "   :imported-members:" >> doc/source/cvts.tasks.rst
	. ./venv/bin/activate \
	    && cd doc/source \
	    && PYTHONPATH=$(CURDIR) sphinx-build -b html . ../build

push-doc: sphinx-doc
	if [ ! -d $(DOC_BUILD_DIR) ]; then git worktree add $(DOC_BUILD_DIR) gh-pages; fi
	cp -r doc/build/* $(DOC_BUILD_DIR) && \
	    cd $(DOC_BUILD_DIR) && \
	    git add -A && \
	    git commit -m "Updates of Documenation."
	git push -f origin gh-pages
	rm -rf $(DOC_BUILD_DIR)
	git worktree prune

clean: clean-sphinx-doc
	rm -rf build/ dist/ *.egg-info
	find . -name '__pycache__' -type d -exec rm -rf {} +
	find . -type f \( -iname '*.pyc' -o -iname '*.pyo' -o -iname '*~' \) -exec rm -f {} +

clean-sphinx-doc:
	rm -rf doc/build doc/source/cvts* $(DOC_BUILD_DIR)
