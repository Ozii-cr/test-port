import requests
import os

# === CONFIGURATION ===
PORT_API_BASE_URL = "https://api.port.io/v1"
PORT_CLIENT_TOKEN = os.getenv("PORT_CLIENT_TOKEN")
HEADERS = {
    "Authorization": f"Bearer {PORT_CLIENT_TOKEN}",
    "Content-Type": "application/json"
}

SERVICE_BLUEPRINT = "service"
FRAMEWORK_BLUEPRINT = "framework"
EOL_STATE = "EOL"
EOL_PROP_KEY = "number_of_eol_packages"  


def get_all_frameworks():
    url = f"{PORT_API_BASE_URL}/blueprints/{FRAMEWORK_BLUEPRINT}/entities"
    resp = requests.get(url, headers=HEADERS)
    resp.raise_for_status()
    frameworks = resp.json().get("entities", [])
    return {fw["identifier"]: fw for fw in frameworks}


def get_all_services():
    url = f"{PORT_API_BASE_URL}/blueprints/{SERVICE_BLUEPRINT}/entities"
    resp = requests.get(url, headers=HEADERS)
    resp.raise_for_status()
    return resp.json().get("entities", [])


def update_eol_counts():
    frameworks = get_all_frameworks()
    services = get_all_services()

    for svc in services:
        svc_id = svc["identifier"]
        relations = svc.get("relations", {})
        related_framework_ids = relations.get("used_frameworks", []) 

        eol_count = sum(
            1 for fw_id in related_framework_ids
            if frameworks.get(fw_id, {}).get("properties", {}).get("state") == EOL_STATE
        )

        #  entity update 
        update_url = f"{PORT_API_BASE_URL}/blueprints/{SERVICE_BLUEPRINT}/entities/{svc_id}"
        payload = {
            "identifier": svc_id,
            "properties": {
                EOL_PROP_KEY: eol_count
            },
            "relations": {
                "used_frameworks": related_framework_ids
            }
        }
        resp = requests.put(update_url, headers=HEADERS, json=payload)
        if resp.ok:
            print(f"Updated {svc_id} with {eol_count} EOL packages")
        else:
            print(f"Failed to update {svc_id}: {resp.text}")


if __name__ == "__main__":
    update_eol_counts()
