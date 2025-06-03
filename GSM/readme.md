# The genome scale metabolic model & interaction potential
## Genome scale model was constructed by CarveMe
### Building a model  
module load Python/3.7.6-foss-2019a  
```
carve /PATH2GENOME/SPECIES.faa --output /PATH2OUTPUT/SPECIES_model.xml
```
### Gap Filling  
```
gapfill SPECIES_model.xml -m medium.tsv -o NEW_SPECIES_model.xml
```
### Microbial Communities  
```
merge_community NEW_SPECIES_model_1.xml NEW_SPECIES_model_2.xml NEW_SPECIES_model_3.xml \
                -o Tri-culture_community.xml \
                --mediadb medium.tsv
```
## Calculate the interaction potential by smetana  
module load Python/3.7.6-foss-2019a
### Global mode  
```
smetana -d /PATH2MODEL/Tri-culture_community.xml \
        --mediadb medium.tsv \
        -o OUTPUT_global.tsv
```
