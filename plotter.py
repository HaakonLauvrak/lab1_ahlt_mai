import os
import re
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path


def extract_f1_macro_score(file_path):
    """
    Extract the F1 Macro average score from a stats file.
    
    Args:
        file_path (str): Path to the stats file
        
    Returns:
        float: F1 Macro score or None if not found
    """
    try:
        with open(file_path, 'r') as f:
            content = f.read()
            
        # Look for the "M.avg" line and extract the F1 score
        match = re.search(r'M\.avg\s+-\s+-\s+-\s+-\s+-\s+\d+\.\d+%\s+\d+\.\d+%\s+(\d+\.\d+)%', content)
        if match:
            return float(match.group(1))
        return None
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return None


def find_stats_files(root_folder):
    """
    Recursively find all stats files in subfolders.
    
    Args:
        root_folder (str): Root directory to start the search
        
    Returns:
        list: List of (subfolder_name, file_path) tuples
    """
    results = []
    root_path = Path(root_folder)
    
    for path in root_path.glob('**/*.stats'):
        # Use relative path as subfolder name
        rel_path = path.relative_to(root_path).parent
        if rel_path == Path('.'):
            subfolder = 'root'
        else:
            subfolder = str(rel_path)
        
        results.append((subfolder, str(path)))
    
    return results


def main(root_folder, output_csv='f1_scores.csv', output_plot='f1_scores_plot.png'):
    """
    Main function to extract F1 scores and create visualizations.
    
    Args:
        root_folder (str): Root directory to search for stats files
        output_csv (str): Path to save the CSV output
        output_plot (str): Path to save the plot image
    """
    # Find all stats files
    stats_files = find_stats_files(root_folder)
    
    if not stats_files:
        print(f"No stats files found in {root_folder} or its subfolders.")
        return
    
    # Extract F1 scores
    data = []
    for subfolder, file_path in stats_files:
        f1_score = extract_f1_macro_score(file_path)
        if f1_score is not None:
            filename = os.path.basename(file_path)
            data.append({
                'Subfolder': subfolder,
                'Filename': filename,
                'F1_Macro': f1_score
            })
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    if df.empty:
        print("No valid F1 scores were extracted.")
        return
    
    # Sort by subfolder for better visualization
    df = df.sort_values('Subfolder')
    
    # Save to CSV
    df.to_csv(output_csv, index=False)
    print(f"F1 scores saved to {output_csv}")
    
    # Create plot
    plt.figure(figsize=(12, 6))
    sns.set_style("whitegrid")
    
    # If we have many subfolders, use different colors
    if len(df['Subfolder'].unique()) > 1:
        ax = sns.lineplot(data=df, x='Filename', y='F1_Macro', hue='Subfolder', marker='o')
        plt.legend(title='Subfolder', bbox_to_anchor=(1.05, 1), loc='upper left')
    else:
        ax = sns.lineplot(data=df, x='Filename', y='F1_Macro', marker='o')
    
    plt.title('F1 Macro Scores Across Different Files')
    plt.xlabel('File')
    plt.ylabel('F1 Macro Score (%)')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    # Save plot
    plt.savefig(output_plot, dpi=300, bbox_inches='tight')
    print(f"Plot saved to {output_plot}")
    
    # Display summary statistics
    print("\nSummary Statistics:")
    print(df.groupby('Subfolder')['F1_Macro'].describe())


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Extract F1 Macro scores from stats files')
    parser.add_argument('root_folder', help='Root folder containing stats files in subfolders')
    parser.add_argument('--output-csv', default='f1_scores.csv', help='Output CSV file path')
    parser.add_argument('--output-plot', default='f1_scores_plot.png', help='Output plot image path')
    
    args = parser.parse_args()
    main(args.root_folder, args.output_csv, args.output_plot)