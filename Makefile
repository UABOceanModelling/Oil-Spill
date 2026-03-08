output = output.txt

run:
	@python app.py

log:
	@python app.py > $(output) 2>&1 &
