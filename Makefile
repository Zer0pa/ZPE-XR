.PHONY: install verify test build benchmark-manifest comparator-triage clean

install:
	python -m pip install "./code[dev]"

verify:
	python ./executable/verify.py

test:
	python -m pytest ./code/tests -q

build:
	python -m build ./code --wheel

benchmark-manifest:
	python ./code/scripts/export_public_benchmark_manifest.py

comparator-triage:
	python ./code/scripts/export_comparator_triage.py --output ./code/dist/comparator_triage.json

clean:
	rm -rf ./code/dist ./code/build
