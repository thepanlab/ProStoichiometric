import cobra
import pandas as pd
from cobra.flux_analysis import gapfill

# Define paths
model_path = '/ourdisk/hpc/prebiotics/dywang/Projects/Microbial_Interactions/Model/Model_multi/HMA.xml'
output_dir = '/ourdisk/hpc/prebiotics/dywang/Projects/Microbial_Interactions/Model/FBA/'
species_id = 'Clostridium_cellulolyticum_H10'
label = species_id  # Used to label output files

# Load the SBML model
model = cobra.io.read_sbml_model(model_path)

# Function to analyze specific reactions
def analyze_reactions(model, reaction_list, label):
    solution = model.optimize()
    flux_data = {
        "Reaction ID": [],
        "Reaction Name": [],
        "Flux Value": []
    }
    for rxn in reaction_list:
        flux_data["Reaction ID"].append(rxn.id)
        flux_data["Reaction Name"].append(rxn.name)
        flux_data["Flux Value"].append(solution.fluxes[rxn.id])
    flux_df = pd.DataFrame(flux_data)
    flux_df.to_csv(f'{output_dir}{label}.csv', index=False)
    return flux_df, solution

# Isolate species-specific reactions
species_reactions = [rxn for rxn in model.reactions if species_id in rxn.id]
species_model = model.copy()
species_model.remove_reactions([rxn for rxn in species_model.reactions if species_id not in rxn.id])

# Check essential nutrients
def check_essential_nutrients(model):
    essential_nutrients = ['EX_glc__D_e', 'EX_nh4_e', 'EX_pi_e', 'EX_so4_e', 'EX_mg2_e', 'EX_ca2_e', 'EX_fe2_e']
    print("Checking essential nutrients availability:")
    for nutrient in essential_nutrients:
        if nutrient in model.reactions:
            rxn = model.reactions.get_by_id(nutrient)
            print(f"{nutrient}: lower bound = {rxn.lower_bound}, upper bound = {rxn.upper_bound}")
        else:
            print(f"{nutrient} not found in the model.")
    print()

check_essential_nutrients(species_model)

# Set biomass as objective
def set_biomass_as_objective(model):
    biomass_reactions = [rxn for rxn in model.reactions if 'biomass' in rxn.name.lower() or 'biomass' in rxn.id.lower()]
    
    if biomass_reactions:
        biomass_rxn = biomass_reactions[0]
        model.objective = biomass_rxn
        print(f"Biomass reaction '{biomass_rxn.id}' set as the objective function.")
        solution = model.optimize()
        print(f"Biomass flux (objective value): {solution.objective_value}")
        return biomass_rxn, solution
    else:
        print("No biomass reaction found.")
        return None, None

# Run initial optimization
biomass_rxn, biomass_solution = set_biomass_as_objective(species_model)

# Identify infeasible reactions (zero flux)
print("Identifying infeasible reactions:")
solution = species_model.optimize()
infeasible_reactions = [rxn for rxn in species_model.reactions if abs(solution.fluxes[rxn.id]) < 1e-6]
for rxn in infeasible_reactions:
    print(f"{rxn.id}: {rxn.name}")

# Perform gap-filling if biomass is defined
if biomass_rxn:
    print("Performing gap-filling...")
    gapfill_results = gapfill(species_model, model, demand_reactions=species_model.exchanges)

    # Add gapfilled reactions to species_model
    for reaction in gapfill_results[0]:  # Use only the first solution
        if reaction.id not in species_model.reactions:
            species_model.add_reactions([reaction])

    # Re-run optimization
    biomass_rxn, biomass_solution = set_biomass_as_objective(species_model)

    # Save refined model
    output_model_path = f'{output_dir}{label}_gap_filled_model.xml'
    cobra.io.write_sbml_model(species_model, output_model_path)

    # Save flux distribution
    flux_data = {
        "Reaction ID": [rxn.id for rxn in species_model.reactions],
        "Reaction Name": [rxn.name for rxn in species_model.reactions],
        "Flux Value": [biomass_solution.fluxes[rxn.id] for rxn in species_model.reactions]
    }
    flux_df = pd.DataFrame(flux_data)
    output_flux_path = f'{output_dir}{label}_gap_filled_flux_distribution.csv'
    flux_df.to_csv(output_flux_path, index=False)

    print(f"Gap-filled model saved to {output_model_path}")
    print(f"Flux distribution saved to {output_flux_path}")
