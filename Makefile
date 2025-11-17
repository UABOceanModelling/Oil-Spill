output = output.txt

run:
	@python app.py

log:
	@python app.py > $(output) 2>&1 &

make plot:
	@python oil_spill/plotter/make_plots.py

