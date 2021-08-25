clean:
		rm -rf webapp-flask *.checkpoint .pytest_cache webapp myenv

init: clean
	pip install poetry
	sudo apt install python3-virtualenv
	poetry install
