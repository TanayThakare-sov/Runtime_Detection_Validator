.PHONY: setup lint unit sensor integration clean

setup:
	python3 -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt

lint:
	ruff check .

unit:
	pytest -m "not integration" -v

# Run in a separate terminal (needs root for eBPF)
sensor:
	sudo python3 sensor/sensor.py

integration:
	pytest -m integration -v

clean:
	rm -rf .pytest_cache .ruff_cache logs/events.log
	-docker rm -f rdv-target
