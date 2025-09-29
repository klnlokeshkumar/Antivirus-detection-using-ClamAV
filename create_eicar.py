import os

# Create EICAR test file without triggering Windows Defender
eicar_parts = [
    'X5O!P%@AP[4\\PZX54(P^)7CC)7}$',
    'EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*'
]

# Create tests directory if it doesn't exist
os.makedirs('tests', exist_ok=True)

# Write EICAR file
with open('tests/eicar.txt', 'w', encoding='ascii') as f:
    f.write(''.join(eicar_parts))

print("EICAR test file created successfully!")
print("File location: tests/eicar.txt")