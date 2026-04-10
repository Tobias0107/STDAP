/*
  Requirements:

  This simulation should obtain the fraction of car-accessible road to transform into pedestrian area.\ 
  Then it should estimate the location of the new transit points. \
  Doing so it should calculate the new distance to those transit points for every neighborhood (buurt).\
  Then it should divide the new distance by the amount of people living in that neighborhood of a certain demographic group. This should be done for every demographic group. The results should be added to a total. This would result in the average increase in distance for every demographic group. \
  The parameters should include the demographic groups to target (performance wise).\
  The parameters should include any visualizing mechanics, like saving an image of the transformed map (before and after in a single image), and make the increase in distance per neighborhood visual with colors. Also maybe a bar diagram showing the results. The results should also be returned by the method in the form of a dictionary. \
*/

=== General steps
- Pre simulation. 
 + For every neighborhood, create an instance of the network class. 
  - Store the class in a dictionary with the neighborhood names as key, and classes as value.
  - The class should contain the following information:
   - The relevant values of the demographic groups
   - The 5 points denoting the neighborhood.
 + For every node in the network, determine the neighborhood, and store as attribute.
 + For every neighborhood, calculate amenity density (amenity by category divided by area)
 + Identify all transit stations in the city, with some buffer.
- simulation
 + Remove edges based on street length divided by population size or amenity size. Keep removing edges until the correct fraction is met.
 + For every transit station, check if it is located on an edge that is now pedestrian area. If so, relocate it to the nearest node allowing cars (or road if possible)
 + For every neighborhood:
  + For all 5 points, calculate the distance to the nearest transit station.
  + For every demographic group, add the average distance divided by the number of that demographic group

