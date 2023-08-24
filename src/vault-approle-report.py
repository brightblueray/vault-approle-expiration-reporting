import os
import requests
from pprint import pprint
import csv

# Set my environment
# os.environ['VAULT_ADDR'] =  'http://127.0.0.1:8200'
# os.environ['VAULT_TOKEN'] = 'hvs.4O3Nh0I75YUMdZZS99cJt8xk'

# Environment Variables Should be set ahead of time
token = os.getenv('VAULT_TOKEN')
base_url = os.getenv('VAULT_ADDR')

# Build Auth Lookup Table
auth_url = f"{base_url}/v1/sys/auth"
headers = {
    "X-Vault-Token": token,
    "accept": "*/*"
}

auth_lookup = {}
response = requests.get(auth_url, headers=headers)
data = response.json()
for path, auth_info in data.items():
    if isinstance(auth_info, dict) and 'accessor' in auth_info and 'type' in auth_info:
        accessor = auth_info['accessor']
        auth_type = auth_info['type']
        auth_lookup[accessor] = {"path": path, "type": auth_type}

# Find all the approles
approles = {key: value for key, value in auth_lookup.items() if value['type'] == 'approle'}

# Get roles for each approle
role_url_template = f"{base_url}/v1/auth/{{auth_path}}role?list=true"

for approle_name, approle_info in approles.items():
    auth_path = approle_info['path']
    role_url = role_url_template.format(auth_path=auth_path)
    response = requests.get(role_url, headers=headers)
    role_data = response.json()

    roles = role_data.get('data', {}).get('keys', [])
    approle_info['roles'] = roles

    for role_name in roles:
        accessor_url = f"{base_url}/v1/auth/{auth_path}role/{role_name}/secret-id?list=true"
        response = requests.get(accessor_url, headers=headers)
        accessor_data = response.json()

        accessors = accessor_data.get('data', {}).get('keys', [])
        approle_info.setdefault('secret_id_accessors', {})[role_name] = accessors

# pprint(approles)

# Get the Secret-ID data
secret_id_url_template = f"{base_url}/v1/auth/{{auth_path}}role/{{role_name}}/secret-id-accessor/lookup"

for approle_name, approle_info in approles.items():
    auth_path = approle_info['path']
    secret_id_accessors = approle_info.get('secret_id_accessors', {})
    
    for role_name, accessors in secret_id_accessors.items():
        for accessor in accessors:
            secret_id_url = secret_id_url_template.format(auth_path=auth_path, role_name=role_name)
            data = {
                "secret_id_accessor": accessor
            }
            response = requests.post(secret_id_url, json=data, headers=headers)
            secret_data = response.json()
            
            approle_info.setdefault('secret_id_data', {}).setdefault(role_name, {})[accessor] = secret_data

# pprint(approles)

# Create and write CSV file
csv_filename = "secret_id_data.csv"
csv_columns = ["accessor", "auth_path", "auth_type", "role", "secret_id_accessor", "creation_time", "expiration_time", "last_updated_time", "metadata"]

with open(csv_filename, "w", newline="") as csv_file:
    writer = csv.DictWriter(csv_file, fieldnames=csv_columns)
    writer.writeheader()

    for approle_name, approle_info in approles.items():
        auth_path = approle_info['path']
        secret_id_data = approle_info.get('secret_id_data', {})

        for role_name, accessor_data in secret_id_data.items():
            for accessor, data in accessor_data.items():
                row = {
                    "accessor": accessor,
                    "auth_path": auth_path,
                    "auth_type": approle_info['type'],
                    "role": role_name,
                    "secret_id_accessor": accessor,
                    "creation_time": data['data']['creation_time'],
                    "expiration_time": data['data']['expiration_time'],
                    "last_updated_time": data['data']['last_updated_time'],
                    "metadata": data['data']['metadata']
                }
                writer.writerow(row)

print("CSV file generated:", csv_filename)