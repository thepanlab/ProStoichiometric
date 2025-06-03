import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import seaborn as sns
from scipy.stats import pearsonr

carbon_transfer_path = '/ourdisk/hpc/prebiotics/dywang/Projects/Microbial_Interactions/Model/Electron_transfer.xlsx'
overall_csv_path = '/ourdisk/hpc/prebiotics/dywang/Projects/Microbial_Interactions/Model/Overall_1.csv'

# Input the two files
carbon_transfer_df = pd.read_excel(carbon_transfer_path, sheet_name='Carbon_transfer')
overall_df = pd.read_csv(overall_csv_path)

# Clean the Carbon Transfer DataFrame
carbon_transfer_df.columns = [
    'Condition', 'Reducing_Sugar_1', 'Reducing_Sugar_2', 'Reducing_Sugar_3', 
    'Lactate_1', 'Lactate_2', 'Lactate_3', 
    'Acetate_1', 'Acetate_2', 'Acetate_3', 
    'Ethanol_1', 'Ethanol_2', 
    'CO2_1', 'CO2_2', 'CO2_3', 
    'CH4_1', 'CH4_2', 'CH4_3', 'CH4_4'
]

# Calculate the mean of replicates for each compound
carbon_transfer_df['Reducing_Sugar_Mean'] = carbon_transfer_df[['Reducing_Sugar_1', 'Reducing_Sugar_2', 'Reducing_Sugar_3']].mean(axis=1)
carbon_transfer_df['Lactate_Mean'] = carbon_transfer_df[['Lactate_1', 'Lactate_2', 'Lactate_3']].mean(axis=1)
carbon_transfer_df['Acetate_Mean'] = carbon_transfer_df[['Acetate_1', 'Acetate_2', 'Acetate_3']].mean(axis=1)
carbon_transfer_df['Ethanol_Mean'] = carbon_transfer_df[['Ethanol_1', 'Ethanol_2']].mean(axis=1)
carbon_transfer_df['CO2_Mean'] = carbon_transfer_df[['CO2_1', 'CO2_2', 'CO2_3']].mean(axis=1)
carbon_transfer_df['CH4_Mean'] = carbon_transfer_df[['CH4_1', 'CH4_2', 'CH4_3', 'CH4_4']].mean(axis=1)

# Select relevant columns
carbon_transfer_mean_df = carbon_transfer_df[['Condition', 'Reducing_Sugar_Mean', 'Lactate_Mean', 'Acetate_Mean', 'Ethanol_Mean', 'CO2_Mean', 'CH4_Mean']]

# Merge the overall dataset with the carbon transfer dataset based on the combination/condition
merged_df = pd.merge(overall_df, carbon_transfer_mean_df, left_on='combination', right_on='Condition')

# Calculate p-values and correlation matrix
correlations = []
p_values = []

for column in ['Reducing_Sugar_Mean', 'Lactate_Mean', 'Acetate_Mean', 'Ethanol_Mean', 'CO2_Mean', 'CH4_Mean']:
    corr_mip, p_mip = pearsonr(merged_df['MIP'], merged_df[column])
    corr_mro, p_mro = pearsonr(merged_df['MRO'], merged_df[column])
    correlations.append((corr_mip, corr_mro))
    p_values.append((p_mip, p_mro))

# Set the size of the figure
fig_size = (6, 10)  # You can adjust the width and height
fig, ax = plt.subplots(figsize=fig_size)

# Plot the heatmap with cell boundaries
sns.heatmap(
    carbon_transfer_mean_df.set_index('Condition'),
    annot=False,
    cmap="Purples",
    cbar=True,
    ax=ax,
    linewidths=0.5,  # Width of the cell boundaries
    linecolor='grey'  # Color of the cell boundaries
)

# Define the locations for MIP and MRO symbols further below the heatmap
mip_x_position = len(correlations) / 2 - 3
mro_x_position = len(correlations) / 2 + 3
symbol_y_position = -5  # Further below the matrix

# Draw symbols for MIP and MRO below the heatmap
ax.text(mip_x_position, symbol_y_position, '?', color='red', ha='center', fontsize=30, zorder=6)
ax.text(mro_x_position, symbol_y_position, '?', color='blue', ha='center', fontsize=30, zorder=6)

# Use a color map for the correlation from red (negative) to blue (positive)
color_map = plt.cm.RdBu_r

# Map p-values to line widths (inverse relation)
def p_value_to_linewidth(p):
    if p < 0.01:
        return 4
    elif p < 0.05:
        return 3
    elif p < 0.1:
        return 2
    else:
        return 1

# Draw curved lines connecting the bottom line of the matrix to the MIP and MRO symbols
for i, ((mip_corr, mro_corr), (p_mip, p_mro)) in enumerate(zip(correlations, p_values)):
    # Determine the color based on the correlation value
    mip_color = color_map((mip_corr + 1) / 2)  # Normalize mip_corr between 0 and 1 for the color map
    mro_color = color_map((mro_corr + 1) / 2)  # Normalize mro_corr between 0 and 1 for the color map

    # Curve for MIP with dynamic line width
    connection_style = patches.ConnectionStyle("arc3", rad=-0.4)
    curve = patches.FancyArrowPatch((i + 0.5, 0), (mip_x_position, symbol_y_position),
                                    connectionstyle=connection_style, 
                                    color=mip_color,
                                    lw=p_value_to_linewidth(p_mip), linestyle='-', zorder=5)
    ax.add_patch(curve)
    
    # Curve for MRO with dynamic line width and dotted line
    connection_style = patches.ConnectionStyle("arc3", rad=0.4)
    curve = patches.FancyArrowPatch((i + 0.5, 0), (mro_x_position, symbol_y_position),
                                    connectionstyle=connection_style, 
                                    color=mro_color,
                                    lw=p_value_to_linewidth(p_mro), linestyle=':', zorder=5)  # Dotted line for MRO
    ax.add_patch(curve)

# Adjust axis limits and labels
ax.set_ylim(symbol_y_position - 2, carbon_transfer_mean_df.shape[0])
ax.set_xlim(-1, len(correlations))

# Hide ticks
ax.xaxis.set_ticks_position('none') 
ax.yaxis.set_ticks_position('none') 

# Set the title and labels
ax.set_title('Heatmap with MIP and MRO Correlations (Line Width Represents p-value)', fontsize=14)
ax.set_xlabel('Biochemical Compounds')
ax.set_ylabel('Combinations')

# Add a colorbar for the correlation
norm = plt.Normalize(-1, 1)
sm = plt.cm.ScalarMappable(cmap=color_map, norm=norm)
sm.set_array([])
cbar = fig.colorbar(sm, ax=ax, orientation='horizontal', fraction=0.02, pad=0.04)
cbar.set_label('Correlation Coefficient')

# Save the figure as a .tif file with 300 dpi
output_path = '/ourdisk/hpc/prebiotics/dywang/Projects/Microbial_Interactions/Figures/electron_correlation_p_value_width.tif'
plt.savefig(output_path, format='tif', dpi=300)

# Show the plot
plt.tight_layout()
plt.show()
