import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Load your data from an Excel file
file_path = '/ourdisk/hpc/prebiotics/dywang/Projects/Microbial_Interactions/Model/CH4_co2_7day.xlsx'
df = pd.read_excel(file_path, sheet_name='Sheet1')

# Clean the headers and structure the data
df.columns = df.iloc[0]
df = df.drop(0).reset_index(drop=True)
df.columns.values[0] = 'Reactions'

# Drop any empty columns
df_cleaned = df.dropna(axis=1, how='all')

# Rename columns for easier access
df_cleaned.columns = [
    'Reactions', 'Rc_Mean', 'Rc_SD', 'Rc&Mc_Mean', 'Rc&Mc_SD', 
    'Rc&Mh_Mean', 'Rc&Mh_SD', 'Rc&Dv_Mean', 'Rc&Dv_SD', 
    'Rc&Mc&Mh_Mean', 'Rc&Mc&Mh_SD', 'Rc&Mc&Dv_Mean', 'Rc&Mc&Dv_SD',
    'Rc&Mh&Dv_Mean', 'Rc&Mh&Dv_SD', 'Q_Mean', 'Q_SD'
]

# Function to create the bubble plot with customizable options
def create_bubble_plot(df, fig_width=10, fig_height=8, x_axis_width=2, y_axis_width=2, dot_scale=1000, output_path='bubble_plot.tif'):
    # Define colors for each reaction
    color_map = {
        'hydrogenic acetogenesis': '#639dc9',  # Blue
        'Mixed-acid fermentation': '#b6e7fa',  # Blue
        'acetoclastic methanogenesis': '#ffc375',  # Orange
        'hydrogenic methanogenesis': '#71bf83',  # Green
        'Hydrogenic lactate oxidation': '#cfbcf5',  # Purple
        'hydrogenic methanogenesis_ch4': '#6b9945',  # Green
        'acetoclastic methanogenesis_ch4': '#f7944d'  # Orange
    }

    # Create a figure and axis with custom size
    fig, ax = plt.subplots(figsize=(fig_width, fig_height))

    # Get conditions and reactions
    conditions = df.columns[1::2]  # Get mean columns
    reactions = df['Reactions']

    # Loop through the reactions and plot them
    for idx, reaction in enumerate(reactions):
        for jdx, condition in enumerate(conditions):
            mean_value = df.iloc[idx, 2*jdx+1]
            sd_value = df.iloc[idx, 2*jdx+2]

            # Handle cases where the SD or mean might cause issues
            if pd.isna(mean_value) or pd.isna(sd_value) or mean_value <= 0:
                continue

            # Plot the dot with size representing mean value
            size = np.sqrt(mean_value) * dot_scale
            color = color_map.get(reaction, 'black')

            # Plot the error bar for SD
            ax.errorbar(jdx, idx, xerr=sd_value, fmt='o', color=color, ecolor='black', 
                        elinewidth=2, capsize=4, markersize=np.sqrt(size), alpha=1.0)

    # Set labels and title
    ax.set_xticks(np.arange(len(conditions)))
    ax.set_xticklabels(conditions, rotation=45, ha='right')
    ax.set_yticks(np.arange(len(reactions)))
    ax.set_yticklabels(reactions)
    ax.set_title('Bubble Plot of Reactions by Condition with SD Bars')

    # Set axis widths
    ax.spines['top'].set_linewidth(x_axis_width)
    ax.spines['right'].set_linewidth(x_axis_width)
    ax.spines['left'].set_linewidth(y_axis_width)
    ax.spines['bottom'].set_linewidth(y_axis_width)

    ax.grid(True)

    # Save the figure as .tif with 300 dpi
    plt.savefig(output_path, format='tif', dpi=300)

    # Optionally show the plot
    plt.show()

# Call the function with your cleaned data
create_bubble_plot(
    df_cleaned, 
    fig_width=6, 
    fig_height=8, 
    x_axis_width=1.5, 
    y_axis_width=1.5, 
    dot_scale=1000, 
    output_path='/ourdisk/hpc/prebiotics/dywang/Projects/Microbial_Interactions/Figures/CH4_CO2_Flux_7th.tif'  # Specify your output path here
)
