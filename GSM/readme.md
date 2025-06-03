# The genome scale metabolic model & interaction potential
## Genome scale model was constructed by CarveMe
### Building a model  
```
carve /PATH2GENOME/SPECIES.faa --output /PATH2OUTPUT/SPECIES_model.xml
```
### Gap Filling  
```
gapfill SPECIES_model.xml -m medium.tsv -o NEW_SPECIES_model.xml
```
