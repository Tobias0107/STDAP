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
      _STDAP --- package structure_
      #h(1fr)
      #counter(page).display("1", both: false)
    ]
  },
)
#show raw.where(block: true): block.with(fill: luma(90%), inset: 1em, radius: 0.5em, width: 100%)

#set table(
  stroke: (x: 0.5pt, y: 0.5pt),
)

#set table(
  fill: (x, y) =>
    if y == 0 {
      rgb("#581d1d")
      } else if calc.even(x + y) {
      luma(95%)
      } else {
      luma(100%)
      },
  stroke: rgb("#581d1d")
)

#show table.cell: it => {
  if it.y == 0 {
    set text(rgb("ffffff"))
    strong(it)
  } else {
    it
  }
}

#set math.equation(numbering: "(1)")

#outline(title: [Document outline])

== Pedestrianization methods
To predict where within the network there is a need for additional pedestrian infrastructure, this study first estimates, for each neighborhood, the number of people likely to walk there. Subsequently, the capacity of the existing network to support this level of pedestrian activity is evaluated. Neighborhoods are prioritized for pedestrianization based on their capability to handle the predicted pedestrian activity with the current infrastructure. \

The number of people likely to walk on a street is not determined by the number of people living nearby. People have to make the choice to go out to walk instead of driving. In an study about walking as a choice Benzovic (2020) conducted an extensive literature review on all relevant research available on this topic #cite(<why_walk>). In this study he determined that the majority of the study's that model walking behaviour, predict walking patterns based on the size of the population living nearby. Furthermore he asserted that this method of modeling walking alone, fails to model the complexity and diversity of real pedestrian behaviour. Nevertheless no good alternatives exist. After extensive literature research he concluded no commonly agreed on model explaining walking as a choice exists. He however noted a general consensus that for people to make the choice to walk, destinations should be located within walkable distances, routes should be free from barriers, and roads should be save to walk. #cite(<why_walk>). In the absence of good alternatives this study will therefore extend the simple people based prediction with nearby destinations. Modeling road barriers and road safety will however require more specialized datasets and simulations, not suitable for this studies simulation framework that is focussed on scalability. \

// Because no definitive scoring formula exists to combine pedestrianization based on population nearby, and pedestrianization based on destinations nearby,
This study will pedestrianize based on the ratio between population and destinations in a city, as well as population and destinations separately. This is necessary because of an absence of a clear definition on the ratio between population and destinations effectively modeling walkability. The three methods of pedestrianization are represented by three different scoring formula's used by the simulation to determine what streets to pedestrianize first. Streets with a high score on the formula are pedestrianized before streets with a low score on the formula. The study therefore makes use of the following formulas. A demand driven scoring formula, that uses the population size as the primary factor. A supply driven scoring formula, that uses possible destinations within a neighborhood, represented by the Points Of Interest (POI) within the neighborhood, as it's primary scoring factor. And lastly a hybrid scoring formula, using both the population size and the possible destinations within a neighborhood. Destinations will be considered to be within walkable distance if they are located within the neighborhoods. \

The scoring formula's used to determine the streets within the network to pedestrianize should be impartial to any neighborhood. Therefore, to prevent larger neighborhoods from having an numerical advantage, the primary scoring factor should be divided by the size of the neighborhood. Additionally, as neighborhoods having little pedestrian streets should be prioritized over neighborhoods having a large amount of pedestrian streets, the fraction of pedestrian roads compared to the total of roads in a neighborhood should also be included into the scoring formula. Furthermore, because both fractions work on a different range of values, both fractions should be normalized to prevent any fraction from dominating the scoring formula. \
All these considerations lead to the following three scoring functions to be used within the simulations: \

*Scoring formula:* \
$
  min(d_"norm" - p_"norm")
$ <formula_ped_score>
#align(center)[#block(width: 47%)[
  #set align(left)
  With:
  - $p = "The pedestrian street length in the neighborhood (m)" / "The total street length in the neighborhood (m)"$

  - $x_"norm"= "norm(x)" = (x - x_"min") / (x_"max" - x_"min")$

  *Demand driven:*
  - $d = d_"demand" = "The neighborhood population" / ("The neighborhood size" ("m"^2))$

  *Supply driven:* \
  - $d = d_"supply"$ = $"POI count in the neighborhood" / ("The neighborhood size" ("m"^2))$

  *Hybrid:* \
  - $d = (d_"demand" + "city population" / "POI count in the city" * d_"supply")$
]]


== Bus stop relocation methods
Bus stops are part of bus routes, bus-stop locations are therefore determined by the bus routes. The problem of determining the bus routes and the corresponding bus-stop locations is called the bus line planning problem. \
Solving the bus line planning problem is a complex task that can be handled a in a lot of different ways. Different methods of solving the bus line planning problem have different advantages. Existent research aiming to solve the bus line problem in post-reform environments can be categorized into two philosophies. The first philosophy starts of with a network without any transit stops, discarding any existing transit networks #cite(<bus_planning_blank_slate>). Then big data network analysis is performed to predict the best bus-routes, usually optimizing route properties like population coverage and route distance. The second philosophy starts of with the original network of bus-routes as a starting point. This network is then optimized by applying certain changes to the network. This process of slightly changing the network is often incremental to allow changes to be rejected if counterproductive #cite(<Eliminating_bus_stops>). The following sections present the algorithms, representing both philosophies, chosen by this study. \

=== Redesigning the bus-network <redesign_bus_network>
This algorithm analyses the city and it's network to determine routes maximizing population and POI coverage while minimizing route distance. Existing bus-stops are not part of this process, resulting in a complete redesign of the bus network. The algorithm used for this has been introduced by Li (2026), and was validated through empirical analysis #cite(<bus_planning_blank_slate>). The bus-line planning solution generated through this algorithm demonstrated a 18.26% improvement in route distance, a 15.79% improvement in POI accessibility, and a 10.53% improvement in population coverage when redetermining route 119 in Kunming #cite(<bus_planning_blank_slate>). \
The algorithm, used to find the optimal bus-route between a given source and destination, takes the following steps: \
At first candidate bus-stops are generated along the network, spaced a hundred meters apart. To prevent detours, no candidate busstops are set along dead ends. Furthermore, to ensure pedestrian safety, no candidate busstops are set within a two hundred meter radius of road crossings. \
After candidate bus-stops have been generated, nearby population and POIs are assigned to the bus-stops. Population and POIs are considered nearby when they lay within a five hundred meter radius of the bus-stops. \
The candidate bus-stops are then used to generate candidate routes. For this a directed graph is build with candidate bus-stops as nodes. In this graph an edge from node $n$ to node $m$ means that node $m$ satisfies the conditions for subsequent stops to node $b$. For $m$ to be a possible subsequent node to $n$ the following conditions should hold:
- Stops are spaced three hundred to eight hundred meters apart, as recommended by the relevant city standard. For this Euclidean distance is used as a proxy cost to avoid large computational overheads.
- Node m should have a shorter Euclidean distance to the destination then node n. This condition ensures progression towards the destination.
- Node n should have a larger distance to the origin then node m. This condition maintains logical and efficient route progression.
- Node m should be the node closest to n satisfying all conditions. This condition ensures smooth routes with minimal detours.
Paths through this graph denote potential bus routes. Population and POI coverage can then be assigned to routes as the sum of the population and POI coverage of the bus-stops traveled by the bus-route. This results in a list of candidate routes with their corresponding population coverage, POI accessibility, and route distance. Since these objectives often conflict a specialized non-dominated sorting algorithm is then used to sort this list, resulting in multiple solutions with different trade-offs #cite(<bus_planning_blank_slate>). \

Due to differences in the implementation architecture used for the simulations, some small changes have been made to the algorithm introduced by Li (2026).\
Firstly, by taking advantage of the columnar database and cutting edge software, this study is capable of generating a higher number of bus-routes. Therefore, instead of generating candidate bus-stops spaced a hundred meters apart, candidate bus-stops are now generated for every node in the spatial network accessible by both pedestrians and busses. Dead ends are then avoided by rejecting candidate stops with a degree lower than one, crossings however are ignored. By increasing candidate bus-stops, bus-routes have more options, and more chances to fulfill the bus-route conditions, increasing bus-route quantity and quality.\
Secondly, due to the nature of the datasets used, nearby population and POIs are assigned to candidate bus-stops based on the neighborhood the candidate stop is located within. Population size and POI count are divided by the neighborhood size before assigning them to candidate bus-stops. This ensures fairness across neighborhoods with different sizes.\
Lastly, the non-dominated sorting algorithm used by the original algorithm requires manual route selection. Due to the large number of routes to be generated this process is automated. The manual selection is approximated using a scoring formula maximizing population and POI coverage over route distance (see #ref(<formula_bus_routes>)). Routes with the highest scores are selected until the bus-stop count of all new routes equals the original bus-stop count of the city.\

*Scoring formula:*
$
  min((sum_"n"^"r" [("pop"_n + "pop"_"city" / "poi"_"city" * "poi"_n) / "area"_n]) / "len"_r)
$ <formula_bus_routes>

#align(center)[#block(width: 83%)[
  #set align(left)
  With:
  - $"pop"_n$ = The population, assigned to candidate stop n, part of route r.
  - $"pop"_"city"$ = The population of the simulated city.
  - $"poi"_n$ = The number of POIs, assigned to candidate stop n, part of route r.
  - $"poi"_"city"$ = The number of POIs in city currently being simulated.
  - area = The size of the neighborhood that contains candidate stop n $("m"^2)$
  - len = The length of route r measured in the Euclidean distance over the stops (m).
]]

Network connectivity between the bus, train, metro and tram networks is maintained by using the train, metro and tram stops as the source and destination stops for the algorithm. Because the algorithm used to redesign the entire bus-network creates routes between a source point and a destination point, such points should be defined before redesigning the network #cite(<bus_planning_blank_slate>). The train, metro and tram stops remain fixed, even after pedestrianization, because the high movement costs. This prevents redefinition of source and destination stops increasing the interpretability of results. Furthermore, train, metro and tram stops are often used as hubs for the bus-network, significantly reducing travel time #cite(<public_transit_hubs>). By creating routes between the train, metro and tram stops, these stops will naturally develop into transit hubs during the transit redesign.

=== Optimizing the bus-network <optimize_bus_network>
This algorithm analyses the original placements of the bus-stops, moving isolated and impractical bus-stops to a nearby location that is not isolated or impractical. This algorithm is based on a study by Bertsimas (2020) #cite(<iterative_at_scale>). In his study he argued that by fixing bus-stop locations, algorithms solving the bus-line problem can be made increasingly scalable. According to him transit stops are usually already placed effectively, reflecting the physical infrastructure and established demand patterns. Redefining bus-routes instead of bus-stops can thus be used to increase the scalability of the algorithm without significantly reducing the algorithm's effectiveness. His model implementing this method was able to produce a transit-network capable of servicing 27% to 35% more ridership, compared to the original network subset, within budget constraints. \

Relocating impractical and isolated bus-stops to nearby locations, ensures the algorithm implemented by Bertsimas (2020) is capable of (re)optimizing transit routes. The algorithm by Bertsimas (2020) assumes the current transit stops to be placed in a way that reflects physical infrastructure and established demand patterns. This may be the case for the original placements of the bus-stops, but is not necessarily the case for relocated bus-stops. Bus stop relocation is therefore minimized, relocating only truly inconvenient bus-stops. Therefore only bus stops placed on pedestrian roads, or dead ends are relocated. Bus stops are relocated to the closest practical location. This would minimize extra walking distance generated by the relocation. Furthermore, bus-stops are relocated no further than two hundred meters. If no valid locations exist within a radius of two hundred meters from the original bus-stop location, the bus stop is dropped from the network. By ensuring bus-stops are relocated nearby the original location, physical infrastructure and demand patterns, present in the original bus-stop locations, will be mostly preserved in the new bus-stop locations. This method of relocating bus-stops after pedestrianization ensures valid routes can be generated using Bertsimas (2020) algorithm. This study is however only interested in the bus-stop locations, and will therefore not use Bertsimas (2020) algorithm after relocating bus-stops. \

#bibliography("Assets/refs.bib", style: "apa")
