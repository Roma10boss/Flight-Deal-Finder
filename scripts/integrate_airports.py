#!/usr/bin/env python3
"""
Windows Path Fixed Integration Script
Works correctly when run from the scripts directory
"""

import json
import re
import os
import sys

def load_airports(filename='airports.json'):
    """Load airport data from JSON file"""
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)

def generate_javascript_array(airports):
    """Generate JavaScript array for website integration"""
    js_content = """// Comprehensive International Airport Database
// Auto-generated from airport extractor script
const airports = [
"""
    
    for i, airport in enumerate(airports):
        # Escape quotes in strings
        code = airport['code']
        name = airport['name'].replace("'", "\\'").replace('"', '\\"')
        city = airport['city'].replace("'", "\\'").replace('"', '\\"')
        country = airport['country'].replace("'", "\\'").replace('"', '\\"')
        
        js_content += f'    {{ code: "{code}", name: "{name}", city: "{city}", country: "{country}" }}'
        
        if i < len(airports) - 1:
            js_content += ','
        js_content += '\n'
    
    js_content += '];\n'
    return js_content

def update_html_file(airports):
    """Update the HTML file with the new airport data"""
    # Get the correct path (go up one directory from scripts)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    html_file = os.path.join(project_root, 'public', 'index.html')
    
    print(f"Looking for HTML file at: {html_file}")
    
    if not os.path.exists(html_file):
        print(f"Error: {html_file} not found")
        return False
    
    # Read the current HTML file
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Generate the new airport array
    js_array = generate_javascript_array(airports)
    
    # Find the airport array in the HTML and replace it
    pattern = r'const airports = \[[\s\S]*?\];'
    
    if re.search(pattern, html_content):
        # Replace existing array
        html_content = re.sub(pattern, js_array.strip(), html_content)
    else:
        # If array not found, insert it after the script tag
        script_pattern = r'<script>'
        replacement = f'<script>\n{js_array}\n'
        html_content = re.sub(script_pattern, replacement, html_content, count=1)
    
    # Write the updated content back
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"Successfully updated {html_file} with {len(airports)} airports")
    return True

def update_server_file(airports):
    """Update the server file with the new airport data"""
    # Get the correct path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    server_file = os.path.join(project_root, 'server.js')
    
    print(f"Looking for server file at: {server_file}")
    
    if not os.path.exists(server_file):
        print(f"Warning: {server_file} not found - skipping server update")
        return False
    
    # Read the current server file
    with open(server_file, 'r', encoding='utf-8') as f:
        server_content = f.read()
    
    # Generate the airport data for server
    js_array = """// Airport data
const airportData = [
"""
    
    for i, airport in enumerate(airports):
        # Escape quotes in strings
        code = airport['code']
        name = airport['name'].replace("'", "\\'").replace('"', '\\"')
        city = airport['city'].replace("'", "\\'").replace('"', '\\"')
        country = airport['country'].replace("'", "\\'").replace('"', '\\"')
        
        js_array += f'    {{ code: "{code}", name: "{name}", city: "{city}", country: "{country}" }}'
        
        if i < len(airports) - 1:
            js_array += ','
        js_array += '\n'
    
    js_array += '];\n'
    
    # Find and replace the airport data in the server file
    pattern = r'const airportData = \[[\s\S]*?\];'
    
    if re.search(pattern, server_content):
        # Replace existing array
        server_content = re.sub(pattern, js_array.strip(), server_content)
    else:
        # If array not found, insert it at the beginning of the file
        server_content = js_array + '\n' + server_content
    
    # Write the updated content back
    with open(server_file, 'w', encoding='utf-8') as f:
        f.write(server_content)
    
    print(f"Successfully updated {server_file} with {len(airports)} airports")
    return True

def create_json_database(airports):
    """Create a JSON database file for the server"""
    # Get the correct path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    output_file = os.path.join(project_root, 'data', 'airports.json')
    
    # Create data directory if it doesn't exist
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # Save airports to JSON file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(airports, f, indent=2, ensure_ascii=False)
    
    print(f"Created {output_file} with {len(airports)} airports")
    return True

def main():
    print("Windows Path Fixed Integration Script")
    print("====================================")
    
    # Load the extracted airport data
    print("Loading airport data...")
    try:
        airports = load_airports('airports.json')
        print(f"Loaded {len(airports)} airports")
    except FileNotFoundError as e:
        print(f"Error: airports.json not found in current directory")
        print("Please ensure you're running this from the scripts directory")
        sys.exit(1)
    
    # Update the HTML file
    print("\nUpdating HTML file...")
    html_success = update_html_file(airports)
    
    # Update the server file
    print("\nUpdating server file...")
    server_success = update_server_file(airports)
    
    # Create JSON database for server
    print("\nCreating JSON database...")
    json_success = create_json_database(airports)
    
    if html_success or server_success or json_success:
        print("\nIntegration complete!")
        
        # Print some statistics
        countries = {}
        for airport in airports:
            country = airport.get('country', 'Unknown')
            countries[country] = countries.get(country, 0) + 1
        
        print(f"\nTotal countries: {len(countries)}")
        print(f"Total airports: {len(airports)}")
        
        # Show sample of airports
        print("\nSample airports:")
        for airport in airports[:5]:
            print(f"  {airport['code']} - {airport['name']} ({airport['city']}, {airport['country']})")
        
        print("\nYour flight deals website now has access to:")
        print(f"- {len(airports)} international airports")
        print(f"- {len(countries)} countries")
        print("- Full autocomplete functionality for all airport fields")
    else:
        print("\nIntegration failed - please check the error messages above")

if __name__ == "__main__":
    main()