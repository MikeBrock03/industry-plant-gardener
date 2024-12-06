import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

def plot_class_distribution():
    # Read the CSV file with header row
    df = pd.read_csv('preprocessed_data.csv')  # now using the first row as header
    
    # Convert Class column to numeric
    df['Class'] = pd.to_numeric(df['Class'])
    
    # Set figure size and style
    plt.figure(figsize=(10, 6))
    sns.set_theme(style="whitegrid")
    
    # Create a histogram of class values
    sns.histplot(data=df, x='Class', bins=15, kde=True)
    
    # Customize the plot
    plt.title('Distribution of Class Scores', fontsize=14, pad=20)
    plt.xlabel('Class Score', fontsize=12)
    plt.ylabel('Count', fontsize=12)
    
    # Set x-axis limits to show full possible range
    plt.xlim(0, 3)
    
    # Add descriptive statistics text box
    stats_text = (
        f'n = {len(df)}\n'
        f'Mean = {df["Class"].mean():.2f}\n'
        f'Std = {df["Class"].std():.2f}\n'
        f'Min = {df["Class"].min():.2f}\n'
        f'Max = {df["Class"].max():.2f}'
    )
    
    plt.text(0.95, 0.95, stats_text,
             transform=plt.gca().transAxes,
             verticalalignment='top',
             horizontalalignment='right',
             bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    # Adjust layout
    plt.tight_layout()
    
    # Save the plot
    plt.savefig('class_score_distribution.png', dpi=300, bbox_inches='tight')
    
    # Display the plot
    plt.show()
    
    # Print detailed statistics
    print("\nClass Score Distribution Statistics:")
    print(df['Class'].describe())

if __name__ == "__main__":
    plot_class_distribution()