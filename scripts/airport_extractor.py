#!/usr/bin/env python3
"""
Comprehensive Airport Extractor - All Countries A to Z
Extracts ALL international airports including small countries
"""

import requests
from bs4 import BeautifulSoup
import json
import re
import time
import string

class ComprehensiveAirportExtractor:
    def __init__(self):
        self.airports = []
        self.processed_codes = set()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def extract_all_airports(self):
        """Extract airports from all sources"""
        print("Starting comprehensive airport extraction...")
        
        # 1. Extract from IATA code pages (A-Z)
        self.extract_by_iata_code()
        
        # 2. Extract from specific country pages
        self.extract_by_country()
        
        # 3. Add manually curated airports from small countries
        self.add_manual_airports()
        
        # 4. Clean and deduplicate
        self.clean_and_deduplicate()
        
        print(f"\nExtraction complete! Found {len(self.airports)} unique airports")
    
    def extract_by_iata_code(self):
        """Extract from Wikipedia IATA code pages"""
        base_url = "https://en.wikipedia.org/wiki/List_of_airports_by_IATA_airport_code:_"
        
        for letter in string.ascii_uppercase:
            print(f"Processing airports starting with: {letter}")
            url = f"{base_url}{letter}"
            
            try:
                response = requests.get(url, headers=self.headers, timeout=10)
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find tables
                tables = soup.find_all('table', {'class': 'wikitable'})
                
                for table in tables:
                    rows = table.find_all('tr')[1:]  # Skip header
                    
                    for row in rows:
                        cells = row.find_all(['td', 'th'])
                        if len(cells) >= 4:
                            airport_data = self.extract_from_iata_row(cells)
                            if airport_data and airport_data['code'] not in self.processed_codes:
                                self.airports.append(airport_data)
                                self.processed_codes.add(airport_data['code'])
                
                time.sleep(0.5)  # Be respectful
                
            except Exception as e:
                print(f"Error processing letter {letter}: {e}")
    
    def extract_from_iata_row(self, cells):
        """Extract airport data from IATA table row"""
        try:
            # IATA code is usually in the first cell
            iata_code = cells[0].get_text().strip()
            if not re.match(r'^[A-Z]{3}$', iata_code):
                return None
            
            # ICAO code (if available)
            icao_code = cells[1].get_text().strip() if len(cells) > 1 else ""
            
            # Airport name is typically in the 3rd cell
            airport_name = cells[2].get_text().strip() if len(cells) > 2 else ""
            
            # Location/City is typically in the 4th cell
            location = cells[3].get_text().strip() if len(cells) > 3 else ""
            
            # Parse location for city and country
            city, country = self.parse_location(location)
            
            # Clean up the data
            airport_name = re.sub(r'\[.*?\]', '', airport_name).strip()
            
            return {
                'code': iata_code,
                'icao': icao_code,
                'name': airport_name,
                'city': city,
                'country': country
            }
        except:
            return None
    
    def parse_location(self, location):
        """Parse location string to extract city and country"""
        # Clean up the location string
        location = re.sub(r'\[.*?\]', '', location).strip()
        
        # Common patterns
        if ',' in location:
            parts = location.split(',')
            if len(parts) >= 2:
                city = parts[0].strip()
                # Take the last part as country (might have state/province in between)
                country = parts[-1].strip()
                return city, country
        
        # Fallback
        return location, "Unknown"
    
    def extract_by_country(self):
        """Extract from country-specific pages"""
        countries = [
            # Caribbean
            ("Guadeloupe", "https://en.wikipedia.org/wiki/List_of_airports_in_Guadeloupe"),
            ("Haiti", "https://en.wikipedia.org/wiki/List_of_airports_in_Haiti"),
            ("Martinique", "https://en.wikipedia.org/wiki/List_of_airports_in_Martinique"),
            ("Jamaica", "https://en.wikipedia.org/wiki/List_of_airports_in_Jamaica"),
            ("Barbados", "https://en.wikipedia.org/wiki/List_of_airports_in_Barbados"),
            ("Trinidad and Tobago", "https://en.wikipedia.org/wiki/List_of_airports_in_Trinidad_and_Tobago"),
            ("Bahamas", "https://en.wikipedia.org/wiki/List_of_airports_in_the_Bahamas"),
            ("Dominican Republic", "https://en.wikipedia.org/wiki/List_of_airports_in_the_Dominican_Republic"),
            ("Puerto Rico", "https://en.wikipedia.org/wiki/List_of_airports_in_Puerto_Rico"),
            ("Cuba", "https://en.wikipedia.org/wiki/List_of_airports_in_Cuba"),
            ("Saint Lucia", "https://en.wikipedia.org/wiki/List_of_airports_in_Saint_Lucia"),
            ("Antigua and Barbuda", "https://en.wikipedia.org/wiki/List_of_airports_in_Antigua_and_Barbuda"),
            ("Grenada", "https://en.wikipedia.org/wiki/List_of_airports_in_Grenada"),
            ("Saint Vincent and the Grenadines", "https://en.wikipedia.org/wiki/List_of_airports_in_Saint_Vincent_and_the_Grenadines"),
            ("Dominica", "https://en.wikipedia.org/wiki/List_of_airports_in_Dominica"),
            ("Saint Kitts and Nevis", "https://en.wikipedia.org/wiki/List_of_airports_in_Saint_Kitts_and_Nevis"),
            
            # Pacific Islands
            ("Fiji", "https://en.wikipedia.org/wiki/List_of_airports_in_Fiji"),
            ("French Polynesia", "https://en.wikipedia.org/wiki/List_of_airports_in_French_Polynesia"),
            ("Samoa", "https://en.wikipedia.org/wiki/List_of_airports_in_Samoa"),
            ("Tonga", "https://en.wikipedia.org/wiki/List_of_airports_in_Tonga"),
            ("Vanuatu", "https://en.wikipedia.org/wiki/List_of_airports_in_Vanuatu"),
            ("New Caledonia", "https://en.wikipedia.org/wiki/List_of_airports_in_New_Caledonia"),
            ("Solomon Islands", "https://en.wikipedia.org/wiki/List_of_airports_in_the_Solomon_Islands"),
            ("Cook Islands", "https://en.wikipedia.org/wiki/List_of_airports_in_the_Cook_Islands"),
            
            # Indian Ocean
            ("Mauritius", "https://en.wikipedia.org/wiki/List_of_airports_in_Mauritius"),
            ("Seychelles", "https://en.wikipedia.org/wiki/List_of_airports_in_Seychelles"),
            ("Maldives", "https://en.wikipedia.org/wiki/List_of_airports_in_the_Maldives"),
            ("Comoros", "https://en.wikipedia.org/wiki/List_of_airports_in_the_Comoros"),
            ("Réunion", "https://en.wikipedia.org/wiki/List_of_airports_in_Réunion"),
            
            # Small European countries
            ("Malta", "https://en.wikipedia.org/wiki/List_of_airports_in_Malta"),
            ("Cyprus", "https://en.wikipedia.org/wiki/List_of_airports_in_Cyprus"),
            ("Iceland", "https://en.wikipedia.org/wiki/List_of_airports_in_Iceland"),
            ("Luxembourg", "https://en.wikipedia.org/wiki/List_of_airports_in_Luxembourg"),
            ("Estonia", "https://en.wikipedia.org/wiki/List_of_airports_in_Estonia"),
            ("Latvia", "https://en.wikipedia.org/wiki/List_of_airports_in_Latvia"),
            ("Lithuania", "https://en.wikipedia.org/wiki/List_of_airports_in_Lithuania"),
            
            # Other small countries
            ("Bhutan", "https://en.wikipedia.org/wiki/List_of_airports_in_Bhutan"),
            ("Brunei", "https://en.wikipedia.org/wiki/List_of_airports_in_Brunei"),
            ("East Timor", "https://en.wikipedia.org/wiki/List_of_airports_in_East_Timor"),
        ]
        
        for country_name, url in countries:
            print(f"Processing {country_name}...")
            try:
                response = requests.get(url, headers=self.headers, timeout=10)
                soup = BeautifulSoup(response.content, 'html.parser')
                
                tables = soup.find_all('table', {'class': 'wikitable'})
                
                for table in tables:
                    rows = table.find_all('tr')[1:]
                    
                    for row in rows:
                        cells = row.find_all(['td', 'th'])
                        airport_data = self.extract_from_country_row(cells, country_name)
                        if airport_data and airport_data['code'] not in self.processed_codes:
                            self.airports.append(airport_data)
                            self.processed_codes.add(airport_data['code'])
                
                time.sleep(0.5)
                
            except Exception as e:
                print(f"Error processing {country_name}: {e}")
    
    def extract_from_country_row(self, cells, country):
        """Extract airport data from country-specific table row"""
        try:
            iata_code = None
            icao_code = None
            airport_name = None
            city = None
            
            # Look for IATA code (3 letters)
            for cell in cells:
                text = cell.get_text().strip()
                if re.match(r'^[A-Z]{3}$', text) and not iata_code:
                    iata_code = text
                elif re.match(r'^[A-Z]{4}$', text) and not icao_code:
                    icao_code = text
            
            # Look for airport name and city
            for cell in cells:
                text = cell.get_text().strip()
                if any(keyword in text.lower() for keyword in ['airport', 'international', 'aeroporto', 'aéroport']):
                    airport_name = text
                elif text and not re.match(r'^[A-Z]{3,4}$', text) and not city:
                    city = text.split(',')[0].strip()
            
            if iata_code and airport_name:
                return {
                    'code': iata_code,
                    'icao': icao_code or "",
                    'name': re.sub(r'\[.*?\]', '', airport_name).strip(),
                    'city': city or "Unknown",
                    'country': country
                }
        except:
            pass
        return None
    
    def add_manual_airports(self):
        """Add important airports that might be missed"""
        manual_airports = [
            # Guadeloupe
            {'code': 'PTP', 'icao': 'TFFR', 'name': 'Pointe-à-Pitre International Airport', 'city': 'Pointe-à-Pitre', 'country': 'Guadeloupe'},
            {'code': 'LSS', 'icao': 'TFFS', 'name': 'Les Saintes Airport', 'city': 'Les Saintes', 'country': 'Guadeloupe'},
            {'code': 'DSD', 'icao': 'TFFA', 'name': 'La Désirade Airport', 'city': 'La Désirade', 'country': 'Guadeloupe'},
            {'code': 'GBJ', 'icao': 'TFFM', 'name': 'Marie-Galante Airport', 'city': 'Grand-Bourg', 'country': 'Guadeloupe'},
            
            # Haiti
            {'code': 'PAP', 'icao': 'MTPP', 'name': 'Toussaint Louverture International Airport', 'city': 'Port-au-Prince', 'country': 'Haiti'},
            {'code': 'CAP', 'icao': 'MTCH', 'name': 'Cap-Haïtien International Airport', 'city': 'Cap-Haïtien', 'country': 'Haiti'},
            {'code': 'JAK', 'icao': 'MTJA', 'name': 'Jacmel Airport', 'city': 'Jacmel', 'country': 'Haiti'},
            
            # Martinique
            {'code': 'FDF', 'icao': 'TFFF', 'name': 'Martinique Aimé Césaire International Airport', 'city': 'Fort-de-France', 'country': 'Martinique'},
            
            # Other Caribbean
            {'code': 'SXM', 'icao': 'TNCM', 'name': 'Princess Juliana International Airport', 'city': 'Sint Maarten', 'country': 'Sint Maarten'},
            {'code': 'AUA', 'icao': 'TNCA', 'name': 'Queen Beatrix International Airport', 'city': 'Oranjestad', 'country': 'Aruba'},
            {'code': 'CUR', 'icao': 'TNCC', 'name': 'Hato International Airport', 'city': 'Willemstad', 'country': 'Curaçao'},
            {'code': 'BON', 'icao': 'TNCB', 'name': 'Flamingo International Airport', 'city': 'Kralendijk', 'country': 'Bonaire'},
            
            # Pacific Islands
            {'code': 'PPT', 'icao': 'NTAA', 'name': 'Faa\'a International Airport', 'city': 'Papeete', 'country': 'French Polynesia'},
            {'code': 'BOB', 'icao': 'NTTB', 'name': 'Bora Bora Airport', 'city': 'Bora Bora', 'country': 'French Polynesia'},
            {'code': 'RRR', 'icao': 'NTTG', 'name': 'Raroia Airport', 'city': 'Raroia', 'country': 'French Polynesia'},
            {'code': 'RGI', 'icao': 'NTTL', 'name': 'Rangiroa Airport', 'city': 'Rangiroa', 'country': 'French Polynesia'},
            {'code': 'APW', 'icao': 'NSFA', 'name': 'Faleolo International Airport', 'city': 'Apia', 'country': 'Samoa'},
            {'code': 'NAN', 'icao': 'NFFN', 'name': 'Nadi International Airport', 'city': 'Nadi', 'country': 'Fiji'},
            {'code': 'SUV', 'icao': 'NFNS', 'name': 'Nausori International Airport', 'city': 'Suva', 'country': 'Fiji'},
            
            # Others to ensure coverage
            {'code': 'RUN', 'icao': 'FMEE', 'name': 'Roland Garros Airport', 'city': 'Saint-Denis', 'country': 'Réunion'},
            {'code': 'DZA', 'icao': 'FMCZ', 'name': 'Dzaoudzi–Pamandzi International Airport', 'city': 'Dzaoudzi', 'country': 'Mayotte'},
        ]
        
        for airport in manual_airports:
            if airport['code'] not in self.processed_codes:
                self.airports.append(airport)
                self.processed_codes.add(airport['code'])
    
    def clean_and_deduplicate(self):
        """Clean data and remove duplicates"""
        # Sort by country and city
        self.airports.sort(key=lambda x: (x['country'], x['city'], x['code']))
    
    def export_files(self):
        """Export to various formats"""
        # Create lightweight version for web
        lightweight_airports = []
        for airport in self.airports:
            lightweight_airports.append({
                'code': airport['code'],
                'name': airport['name'],
                'city': airport['city'],
                'country': airport['country']
            })
        
        # Export to JSON
        with open('airports_complete.json', 'w', encoding='utf-8') as f:
            json.dump(self.airports, f, indent=2, ensure_ascii=False)
        
        # Create JavaScript file for web integration
        with open('airportData.js', 'w', encoding='utf-8') as f:
            f.write('// Comprehensive Airport Database\n')
            f.write('// Auto-generated - includes airports from all countries\n\n')
            f.write('window.AIRPORT_DATA = ')
            f.write(json.dumps(lightweight_airports, ensure_ascii=False))
            f.write(';\n')
        
        # Create statistics
        self.create_statistics()
    
    def create_statistics(self):
        """Create statistics file"""
        countries = {}
        for airport in self.airports:
            country = airport['country']
            countries[country] = countries.get(country, 0) + 1
        
        with open('airport_statistics.txt', 'w', encoding='utf-8') as f:
            f.write(f"Total airports: {len(self.airports)}\n")
            f.write(f"Total countries/territories: {len(countries)}\n\n")
            
            # Sort by count
            sorted_countries = sorted(countries.items(), key=lambda x: x[1], reverse=True)
            
            f.write("Top 20 countries by airport count:\n")
            for country, count in sorted_countries[:20]:
                f.write(f"{country}: {count}\n")
            
            f.write("\nCaribbean airports:\n")
            caribbean = [a for a in self.airports if any(c in a['country'] for c in ['Guadeloupe', 'Haiti', 'Martinique', 'Jamaica', 'Barbados'])]
            for airport in caribbean:
                f.write(f"{airport['code']} - {airport['name']} ({airport['city']}, {airport['country']})\n")
    
    def run(self):
        """Run the extraction process"""
        self.extract_all_airports()
        self.export_files()
        
        # Print summary
        print("\n" + "="*50)
        print(f"Extraction complete!")
        print(f"Total airports: {len(self.airports)}")
        print(f"Files created:")
        print(f"  - airports_complete.json")
        print(f"  - airportData.js (for web integration)")
        print(f"  - airport_statistics.txt")
        
        # Show some Caribbean examples
        caribbean = [a for a in self.airports if any(c in a['country'] for c in ['Guadeloupe', 'Haiti', 'Martinique'])]
        print(f"\nCaribbean airports found: {len(caribbean)}")
        for airport in caribbean[:5]:
            print(f"  {airport['code']} - {airport['name']} ({airport['city']}, {airport['country']})")

if __name__ == "__main__":
    extractor = ComprehensiveAirportExtractor()
    extractor.run()