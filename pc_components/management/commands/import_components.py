from django.core.management.base import BaseCommand
from pc_components.models import Component
import csv
import os
import re
from decimal import Decimal


class Command(BaseCommand):
    help = 'Imports PC components from CSV files'

    def handle(self, *args, **options):
        # Currency exchange rate from INR to EUR (example rate, should be updated)
        INR_TO_EUR = 0.011  # 1 INR = 0.011 EUR

        # Mapping of file names to component types
        component_types = {
            'CPU.csv': 'CPU',
            'GPU.csv': 'GPU',
            'MotherBoard.csv': 'Motherboard',
            'RAM.csv': 'RAM',
            'StorageSSD.csv': 'Storage',
            'PowerSupply.csv': 'Power Supply',
            'cabinates.csv': 'Case',
            'Cooler.csv': 'Cooler'
        }

        # Base directory for CSV files
        base_dir = os.path.join('app', 'data', 'pc_data')

        for filename, component_type in component_types.items():
            file_path = os.path.join(base_dir, filename)

            if not os.path.exists(file_path):
                self.stdout.write(self.style.WARNING(f'Data was not found: {file_path}'))
                continue

            self.stdout.write(f'Importiere {component_type} aus {filename}...')

            with open(file_path, 'r', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)
                next(reader)  # Skip header row

                for row in reader:
                    try:
                        # Extract name and price depending on file type
                        if filename in ['cabinates.csv', 'PowerSupply.csv', 'StorageSSD.csv', 'Cooler.csv']:
                            full_name = row[0].strip()
                            price_str = row[1].strip()
                        else:
                            full_name = row[1].strip()
                            price_str = row[2].strip()

                        # Skip laptops or notebooks
                        manufacturer = 'Unknown'
                        full_name_lower = full_name.lower()
                        if "laptop" in full_name_lower or "notebook" in full_name_lower:
                            continue

                        # Attempt to detect manufacturer
                        manufacturer_mappings = {
                            'amd': 'AMD',
                            'intel': 'Intel',
                            'nvidia': 'NVIDIA',
                            'gigabyte': 'Gigabyte',
                            'msi': 'MSI',
                            'asus': 'ASUS',
                            'corsair': 'Corsair',
                            'samsung': 'Samsung',
                            'crucial': 'Crucial',
                            'seagate': 'Seagate',
                            'western digital': 'Western Digital',
                            'zebronics': 'ZEBRONICS',
                            'ant esports': 'Ant Esports',
                            'cooler master': 'Cooler Master',
                            'deepcool': 'Deepcool',
                            'frontech': 'Frontech',
                            'artis': 'Artis',
                            'ars infotech': 'ARS Infotech',
                            'matrix': 'Matrix',
                            'rubaintech': 'Rubaintech',
                            'wefly': 'WEFLY',
                            'techon': 'TECHON',
                            'betaohm': 'Betaohm',
                            'gigastar': 'GIGASTAR',
                            'asrock': 'ASRock'
                        }

                        for key, value in manufacturer_mappings.items():
                            if key in full_name_lower:
                                manufacturer = value
                                break

                        if manufacturer == 'Unknown':
                            continue

                        # Convert price from INR to EUR
                        price_str = price_str.replace('₹', '').replace(',', '')
                        price_inr = Decimal(price_str)
                        price_eur = price_inr * Decimal(str(INR_TO_EUR))

                        # Create component entry
                        Component.objects.create(
                            name=full_name,
                            type=component_type,
                            manufacturer=manufacturer,
                            price=price_eur,
                            currency='EUR',
                            description='',
                            technical_details=''
                        )

                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f'Error importing row {row}: {str(e)}'))

            self.stdout.write(self.style.SUCCESS(f'Import of {component_type} completed'))

        self.stdout.write(self.style.SUCCESS('All components imported successfully'))