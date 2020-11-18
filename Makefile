install-extras:
	poetry install --extras "parquet excel docs"

docu:
	cd docs && make doctest && make html