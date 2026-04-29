/*
  Requirements:

  This simulation should obtain the fraction of car-accessible road to transform into pedestrian area.\
  Then it should estimate the location of the new transit points. \
  Doing so it should calculate the new distance to those transit points for every neighborhood (buurt).\
  Then it should divide the new distance by the amount of people living in that neighborhood of a certain demographic group. This should be done for every demographic group. The results should be added to a total. This would result in the average increase in distance for every demographic group. \
  The parameters should include the demographic groups to target (performance wise).\
  The parameters should include any visualizing mechanics, like saving an image of the transformed map (before and after in a single image), and make the increase in distance per neighborhood visual with colors. Also maybe a bar diagram showing the results. The results should also be returned by the method in the form of a dictionary. \
*/
= Design
- Pre simulation
 + Data collection
  - Initialize Database
  - Initialize Network
   - Include pedestrian network
 + Choose city
 + Data_pre_processing
  - Per node, determine
   - the zone
   - population / amenity nearby
   - Number of transit
  - Per neighborhood, determine
   - the total street length, and car-accessible length
   - Population density
   - Amenity density (category specific)
   - Per demographic group, the group size divided by the total people in the neighborhood.
- Simulation
 + Calculate number of edges to remove
 + Sort edges based on length / population or amenity.
 + Remove number of edges in database
 + Remove number of edges in Network
 + Move transit
  - When relocating, take pedestrian accessibility into account
   - Import pedestrian network (also needed later)
   - Import this network also into Duckdb (pre-processed)
   - Merge the two networks to find overlapping edges (do not update after transforming f edges (nodes remain the same))
   - Moving only onto this network
  - Simpel move:
   - Move if node degree < 2
   - Move to closest node with degree >= 2
  - Route based move (minimizing route adjusting)
  - Move minimizing travel time
 + Per neighborhood
  + Calculate distance from 5 points to closest transit
  + Store the the average of the distance to the 5 points.
  + Calculate for every demographic group, this average multiplied by the percentage of the demographic group of the total.
- Visualization
 + Old network
 + New, transformed network
  - Color neighborhoods by increase/decrease in distance.
 + Bar diagram with bar for every demographic groups average increase/decrease in distance.
 + Something showing network fragmentation


=== Optimizations:
- Remove points not in a neighborhood
- Remove points not close to pedestrian network (nobody lives there)
- Link ped network and drive network using max-dist (create edges ped network for this)
- 
