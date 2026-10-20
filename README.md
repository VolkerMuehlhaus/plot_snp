# plot_snp

plot_snp reads one or more S-parameter files with any number of ports (*.snp) 
and plots magnitude (dB) and phase of all selected parameters.

To run the inductor plot and analysis, specify the *.snp file(s) and the requested S-parameters as commandline parameter. Order does not matter. Default is S11.

example:
```
python plot_snp.py data.s2p S21 

python plot_snp.py measured.s2p simulated.s2p S11 S21

```

With `pip install plot_snp`, the same works as the command `plot_snp data.s2p S21`.

The tool plots all files with the specified parameter(s)

![plot](https://raw.githubusercontent.com/VolkerMuehlhaus/plot_snp/main/doc/png/plot_snp.png)

Add `-smith` to additionally plot reflection parameters (Snn, e.g. S11, S22) on a Smith chart, in a separate window. The dB/phase window still shows all selected parameters as before.

Add `-zoom` to also open a third window with a Smith chart zoomed in to |&Gamma;| <= 0.5, with a denser labeled grid. `-zoom` can be used with or without `-smith`.

```
python plot_snp.py data.s2p S11 S21 -smith -zoom
```



# Use from Python

The plots are also available as functions, for example to save them as PNG without a window:

```python
import matplotlib
matplotlib.use("Agg")
import plot_snp

networks = [plot_snp.read_network("data.s2p")]
parameters = [plot_snp.parse_parameter(p) for p in ("S11", "S21")]
figures = plot_snp.plot_all(networks, parameters, smith=True)   # dB/phase, then Smith chart
figures[0].savefig("data_s11_s21.png")
```

# Prerequisites
The code requires Python3 with the skitkit-rf library.
https://scikit-rf.readthedocs.io/en/latest/tutorials/index.html

`pip install plot_snp` installs scikit-rf and matplotlib.



