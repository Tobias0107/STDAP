#show figure.where(kind: image): set align(end)
#set page(
  fill: rgb("f7f4f1"),
  margin: (x: 2.5cm, y: 2.5cm),
  header: [
    #figure(
      image("Assets/Logo.png", alt: "STDAP"),
    )
  ],
  footer: context {
    if calc.even(counter(page).get().first()) [
      #line(length: 100%)
      #counter(page).display("1", both: false)
      #h(1fr)
      _Simulate Transit Distance After Pedestrianization_
    ] else [
      #line(length: 100%)
      #h(1fr)
      #counter(page).display("1", both: false)
    ]
  },
)
#set raw(block: true)

#outline()

= Installation
== The package
The package can be installed with pip with the following command:
```shell
pip install STDAP
```
== The datasets
The simulation needs two datasets: The neighborhood data, and the neighborhood borders. The datasets can be downloaded from the Dutch Central Bureau of Statistics (CBS).\

=== Neighborhood data
The dataset storing neighborhood data is called: "Kerncijfers wijken en buurten \<year>". Some columns are renamed across datasets of different years, and can thus be configured. The package uses the column names of the 2025 dataset by default. The datasets over the years can be found at the following link: "https://www.cbs.nl/nl-nl/reeksen/publicatie/kerncijfers-wijken-en-buurten". This file should be converted to CSV format before its use.

=== Neighborhood borders
The dataset storing neighborhood borders is called: "Wijk- en buurtkaart \<year>". The column names of the 2025 dataset are used for this. Only the 'buurtcode' and 'geom' are read, differentiating datasets should have their columns renamed. The datasets over the years can be found at the following link: "https://www.cbs.nl/nl-nl/dossier/nederland-regionaal/geografische-data". This file should be converted to geopackage format before its use.

=== Network, bus-stop locations, Points Of Interest
This data is all imported from OpenStreetMap using the OSMnx API. If specified, this data is written to the local file system. The simulation is capable of using these files instead to speed up simulations, and allow custom data to be imported. This is done by setting the store_in_file parameter to True, and setting the storage_dir parameter to the folder containing the files to write to / from. These parameters should be set when initializing the main Simulator class:
```Python
sim = Simulator(csv, geopackage, store_in_file=True,
                storage_dir="The_downloaded_graphs/")
```
The files are/should be called the following:
- The car-accessible network:
  - \<city>\_drive.graphml
- The pedestrian network:
  - \<city>\_ped.graphml
- The bus-stops and Points Of Interest
  - \<city>.parquet
The datafiles are obtained using OSMnx features_from_polygon and graph_from_polygon.

= Gui / Dashboard


= Python package
== Selecting the city

==




