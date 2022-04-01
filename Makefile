upload:
	rm -rf ./dist/
	rm -rf ./require_foss.egg-info/
	python3 -m build
	python3 -m twine upload --repository testpypi dist/* --verbose

build:
	rm -rf ./dist/
	rm -rf ./require_foss.egg-info/
	python3 -m build