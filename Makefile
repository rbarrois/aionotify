PACKAGE = aionotify
CODE_DIRS = aionotify/ tests/ examples/

FLAKE8 = flake8


default: test

.PHONY: default

# Package management
# ==================


clean:
	find . -type f -name '*.pyc' -delete
	find . -type f -path '*/__pycache__/*' -delete
	find . -type d -empty -delete
	@rm -rf tmp_test/


update:
	pip install --upgrade pip setuptools
	pip install --upgrade -e .[dev]
	pip freeze


release:
	fullrelease

.PHONY: clean update release

# Tests and quality
# =================


# DOC: Run tests for all supported versions (creates a set of virtualenvs)
testall:
	tox


# DOC: Run tests for the currently installed version
test:
	python -Wdefault -m unittest

# DOC: Perform code quality tasks
lint: check-manifest flake8

# DOC: Verify that MANIFEST.in and .gitignore are consistent
check-manifest:
	check-manifest

# Note: we run the linter in two runs, because our __init__.py files has specific warnings we want to exclude
# DOC: Verify code quality
flake8:
	$(FLAKE8) $(CODE_DIRS) setup.py

.PHONY: testall test lint check-manifest flake8


# Documentation
# =============


# DOC: Show this help message
help:
	@grep -A1 '^# DOC:' Makefile \
	 | awk '    					\
	    BEGIN { FS="\n"; RS="--\n"; opt_len=0; }    \
	    {    					\
		doc=$$1; name=$$2;    			\
		sub("# DOC: ", "", doc);    		\
		sub(":", "", name);    			\
		if (length(name) > opt_len) {    	\
		    opt_len = length(name)    		\
		}    					\
		opts[NR] = name;    			\
		docs[name] = doc;    			\
	    }    					\
	    END {    					\
		pat="%-" (opt_len + 4) "s %s\n";    	\
		asort(opts);    			\
		for (i in opts) {    			\
		    opt=opts[i];    			\
		    printf pat, opt, docs[opt]    	\
		}    					\
	    }'

.PHONY: doc help
