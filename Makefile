create-venv: 
	python3 -m venv .venv

install: requirements.txt
	pip install -r requirements.txt

# Path: Makefile
run:
	python src/email_service_astm_saas_v0.0.1.py

# Path: Makefile
run-background:
	nohup python src/email_service_astm_saas_v0.0.1.py &

# Path: Makefile
clean:
	rm -rf .venv
	rm -rf __pycache__
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf .coverage.*
	rm -rf .mypy_cache
	rm -rf .tox
	rm -rf .eggs
	rm -rf *.egg-info
	rm -rf dist
	rm -rf build
	rm

# Path: Makefile
lint: install
	$(PYTHON) -m pylint --rcfile=.pylintrc email_service_astm_saas_v0.0.1.py

# Path: Makefile
format: install
	$(PYTHON) -m black email_service_astm_saas_v0.0.1.py
	
