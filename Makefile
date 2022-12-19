# this target runs checks on all files
quality:
	isort . -c
	flake8
	mypy
	pydocstyle
	black --check .
	bandit -r . -c pyproject.toml
	autoflake -r .

# this target runs checks on all files and potentially modifies some of them
style:
	isort .
	black .
	autoflake --in-place -r .

# Run tests for the library
test:
	coverage run -m pytest tests/

# Check that docs can build
docs:
	sphinx-build docs/source docs/build -a -v
