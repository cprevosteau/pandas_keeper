install-extras:
	poetry install --extras "parquet excel docs"

documentation:
	cd docs && make doctest && make html