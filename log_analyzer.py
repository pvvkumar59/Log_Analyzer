import re
import pandas as pd
from datetime import datetime

def parse_log_file(log_file_path): # Takes file path as string and returns List of dict
    """
    Parse a log file with fields separated by hyphens(-) 
    as the file is known.
    Creates list of dictionaries with four fields
    """
    # Pattern for: timestamp - service - log_level - message
    log_pattern = r'(.*?) - (\w+) - (\w+) - (.*)'
    
    logs = []
    with open(log_file_path, 'r') as file:
        for line in file:
            match = re.match(log_pattern, line.strip())
            if match:
                timestamp_str, service, log_level, message = match.groups()
                try:
                    # Try common timestamp formats
                    for fmt in ('%Y-%m-%d %H:%M:%S', '%d/%m/%Y %H:%M:%S', '%m/%d/%Y %H:%M:%S', '%Y-%m-%d'):
                        try:
                            timestamp = datetime.strptime(timestamp_str, fmt)
                            break
                        except ValueError as e:
                            print("Warning: while parsing date", e)
                            continue
                    else:
                        timestamp = timestamp_str
                except Exception:
                    timestamp = timestamp_str
                
                logs.append({
                    'timestamp': timestamp,
                    'service': service,
                    'log_level': log_level,
                    'message': message
                })
    return logs


def analyze_logs(logs):
    """Perform analysis on parsed logs and return statistics.
    Takes input of List of Dict and returns Dict
    """
    if not logs:
        return {}
    
    # Convert to DataFrame for easier analysis
    df = pd.DataFrame(logs)
    
    # Basic statistics of log file
    analysis = {
        'total_logs': len(logs),
        'log_level_counts': df['log_level'].value_counts().to_dict(),
        'service_counts': df['service'].value_counts().to_dict(),
        'unique_services': df['service'].nunique(),
        'unique_log_levels': df['log_level'].nunique(),
        'earliest_timestamp': df['timestamp'].min(),
        'latest_timestamp': df['timestamp'].max(),
    }
    
    # Error analysis
    if 'ERROR' in analysis['log_level_counts']:
        error_logs = df[df['log_level'] == 'ERROR']
        analysis.update({
            'error_service_distribution': error_logs['service'].value_counts().to_dict(),
            'common_error_messages': error_logs['message'].value_counts().head(5).to_dict()
        })
    
    return analysis


def print_analysis_results(analysis):
    """Print the analysis results in a readable format."""
  
    print("\n=== Log File Analysis Results ===\n")
    print(f"Total logs processed: {analysis['total_logs']}")
    print(f"Time range: {analysis['earliest_timestamp']} to {analysis['latest_timestamp']}\n")

    
    print("=== Log Level Distribution ===")
    for level, count in analysis['log_level_counts'].items():
        print(f"{level}: {count} ({count / analysis['total_logs']:.1%})")
    
    print("\n=== Service Distribution ===")
    for service, count in analysis['service_counts'].items():
        print(f"{service}: {count} ({count / analysis['total_logs']:.2%})")
    
    if 'error_service_distribution' in analysis:
        print("\n=== Error Distribution by Service ===")
        for service, count in analysis['error_service_distribution'].items():
            print(f"{service}: {count} errors")
    
    if 'common_error_messages' in analysis:
        print("\n=== Most Common Error Messages ===")
        for msg, count in analysis['common_error_messages'].items():
            print(f"{count}x: {msg[:60]}{'...' if len(msg) > 60 else ''}")
    

# Example usage
if __name__ == "__main__":
    # Sample log file path - replace with your actual log file path
    log_file_path = 'applog.txt'
    
    # Parse and analyze the logs
    logs = parse_log_file(log_file_path)
    analysis = analyze_logs(logs)
    print_analysis_results(analysis)
