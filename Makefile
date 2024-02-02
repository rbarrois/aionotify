PACKAGE := aionotify

CODE_DIRS := aionotify/ tests/ examples/


default: test


testall:
	tox

test:
	python -Wdefault -m unittest

lint:
	flake8 $(CODE_DIRS)
