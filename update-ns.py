import requests
import json
import base64
import boto3

# AWS Secret Manager details
secret_name = "aws-pork-dns-ns"
region_name = "us-east-1"

# Porkbun Domain Name
domain_name = "assafdori.com"

# Initialize a Secrets Manager client
client = boto3.client('secretsmanager', region_name=region_name)

# Retrieve Porkbun API credentials from AWS Secret Manager
response = client.get_secret_value(SecretId=secret_name)
secret_dict = json.loads(response['SecretString'])
pork_api_key = secret_dict['pork_api_key']  # Ensure this key name matches what's in Secrets Manager
pork_api_secret = secret_dict['pork_api_secret']  # Ensure this key name matches what's in Secrets Manager

# Initialize a Route 53 client
route53_client = boto3.client('route53')

# Retrieve the hosted zone ID for the domain
response = route53_client.list_hosted_zones_by_name(DNSName=domain_name)
for hosted_zone in response['HostedZones']:
    if hosted_zone['Name'] == f"{domain_name}.":
        hosted_zone_id = hosted_zone['Id'].split('/')[-1]  # Extracting the hosted zone ID
        break
else:
    raise ValueError("Hosted zone not found for domain.")

# Retrieve name servers from Route 53
response = route53_client.get_hosted_zone(Id=hosted_zone_id)
name_servers = response['DelegationSet']['NameServers']

# Check if name servers are already a list
if isinstance(name_servers, str):
    name_servers = name_servers.split(',')
elif isinstance(name_servers, list):
    # Name servers are already in list format, no need for splitting
    pass
else:
    raise TypeError("Unexpected data type for name servers")

# Update DNS records on Porkbun
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Basic {base64.b64encode(f'{pork_api_key}:{pork_api_secret}'.encode()).decode()}"
}
payload = {
    "domain": domain_name,
    "content": ",".join(name_servers),
    "type": "NS",
    "ttl": 3600  # Adjust TTL as needed
}
response = requests.post(f"https://porkbun.com/api/json/v3/domain/updateNs/{domain_name}", headers=headers, data=json.dumps(payload))
print(response.json())