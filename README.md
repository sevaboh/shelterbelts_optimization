# shelterbelts_optimization
create_graph.py:
    Generates fields.py and shelterbelts.py files from shapefiles fields_N36.shp and shelterbelts_N36.shp (inputs also for all other scripts).
    In fields.py for each field the following is saved: area (determined from shapefile), class (field ID from shapefile), average VTCI (field VTCI from shapefile), presence of irrigation (from class number).
    In shelterbelts.py for each shelterbelt the following is saved: length (determined from shapefile), list of adjacent fields).
classify_fields.py:
    Classifies fields according to shelterbelts placement around them (8 bit classification, each for 45 grad sector).
    Writes class number in the field ID2 of fields_N36.shp.
classify_pot_places.py:
    Determines places for potential shelterbelts planting.
    Generates pot_shelterbelts.shp file with lines of their location, pot_shelterbelts.py file with list of adjacent fields and length for each place, graph.shp file with lines from the centers of adjacent fields to the centers of existing shelterbelts, graph_pot.shp file with lines from the centers of adjacent fields to the centers of potential shelterbelts' planting sites. 
classify_all.py:
    Creates all_fields.py file with all fields from fields.py and lists of adjacent existing and potential shelterbelts sites.
    Creates all_shelterbelts.py file with all fields from shelterbelts.py for both existing and potential shelterbelts sites.
create_graph_input.py:
    Runs other scripts to create all needed python and shapefiles for further execution of genetic algorithm.
graph_genetic_all.py:
    Runs genetic algorithm to determine best places to plant new shelterbelts. Coefficients of all needed dependencies and algorithm's parameters' values are set in the file.
