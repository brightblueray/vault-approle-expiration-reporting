# vault-approle-expiration-reporting

This repository contains a script to export Secret ID data for Vault AppRoles and save it as a CSV file. The script retrieves authentication paths, roles, and associated Secret ID accessors, and then fetches Secret ID data for each accessor.

## Prerequisites

- Python 3.x
- Requests library (`pip install requests`)


## Setup

1. Clone this repository to your local machine:

   ```bash
   git clone https://github.com/brightblueray/vault-approle-expiration-reporting.git
   cd vault-approle-expiration-reporting

2. Set Environment Variables
   ```bash
    export VAULT_ADDR="http://your-vault-address:8200"
    export VAULT_TOKEN="your-vault-token"
    ```

## Usage


### Running the Jupyter Notebook
This repository includes Jupyter notebooks that help you set up test data using a bash kernel and demonstrate the execution of the script.

- 01_Approle_setup_bash.ipynb: Sets up test data for Vault using a bash kernel.
- 02_Approle_Secret_Expiration.ipynb: Demonstrates the execution of the secret ID data export script.

### Running the Python Script
  ```bash
  python3 vault-approle-report.py


