init:
	pip install -r requirements.txt

test: clean
	pytest

clean:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	rm -rf ./dist
	rm -rf ./log

package: init test clean
	python setup.py sdist

publish: package
	twine upload dist/*
