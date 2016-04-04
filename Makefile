PACKAGE := aionotify

CODE_DIRS := aionotify/ tests/ examples/


default: test


test:
	tox


lint:
	flake8 $(CODE_DIRS)
