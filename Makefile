install-extras:
	poetry install --extras "parquet excel docs"

docu:
	cd docs && $(MAKE) html