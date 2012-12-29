# ngspice-python-common-source

A design exploration tool for a simple common source amplifier actively
loaded with a simple current mirror. Python is used for coordinating
ngspice simulations and plotting results.

To use this tool, you may edit only `design.py` to adjust the design
specifications and variables.

To simulate, execute `commander.py`.

Results are then plotted to `plot.pdf`.

# Credits

The SPICE model used in this tool is the 65nm Predictive Technology
Model, which can be found at
[http://ptm.asu.edu/modelcard/2006/65nm_bulk.pm][65nm]

[65nm]: http://ptm.asu.edu/modelcard/2006/65nm_bulk.pm
