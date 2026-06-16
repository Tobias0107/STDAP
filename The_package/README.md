### Simulate Transit Distance After Pedestrianization (STDAP)
> Supply and Demand based pedestrianization, moving bus-stops accordingly

This package simulates the effects of pedestrianization upon the average distance to transit stops in Dutch cities. Pedestrianization can be performed based on the population and the number of interesting destinations nearby. Bus stops can be moved by either moving them to the nearest valid location, or by completely redesigning the bus-network. This package is build to be capable of large scale simulations in a reasonable time frame. Simulations can be run from the provided gui, or in Python code directly.

#### Features
* Highly scalable simulations
* Great visualization of results
* Highly configurable

#### Getting started
The package can be used to simulate pedestrianization in the following way:

```python
from STDAP.core.main_class import Simulator
sim = Simulator(datasets)
city_options = sim.get_cities()
sim.choose_city(city_name)
### Run a single pedestrianization for detailed results.
sim.Sim_trans_dist_single(percentage, options)
### Simulate for a range of pedestrianization percentages for fast results.
sim.Sim_trans_dist_single(start, stop, count, options)
```

Datasets can be downloaded from the Dutch Central Bureau of Statistics (CBS).
- https://www.cbs.nl/nl-nl/maatwerk/2025/40/kerncijfers-wijken-en-buurten-2025
- https://www.cbs.nl/nl-nl/dossier/nederland-regionaal/geografische-data/wijk-en-buurtkaart-2025

The dashboard gui can be started with the following code:
```Python
from STDAP.gui.dashboard import show_dashboard
show_dashboard()
```

A more detailed manual is available on the GitHub page (see Project links).

##### Configuration

The package is designed to be highly configurable. This can be done easily with the settings class.
```python
from STDAP.config.settings import get_settings 
settings = get_settings()
settings.parameter = value
```
Configurable parameters and their default values can be obtained with the describe method:
```python
print(settings.describe())
```
