import json
import os

def test_server_config():
    config_path = os.path.join("config", "server_config.json")
    
    if not os.path.exists(config_path):
        print("Config file not found.")
        return

    with open(config_path, "r") as file:
        config = json.load(file)

    print("=== Server Metadata ===")
    print(f"Name: {config['server_name']}")
    print(f"Version: {config['server_version']}")
    print(f"Description: {config['description']}")

    print("\n=== Tools ===")
    for tool in config['tools']:
        print(f"- {tool['name']}: {tool['description']}")

    print("\n=== Resources ===")
    for res in config['resources']:
        print(f"- {res['name']}: {res['description']}")

if __name__ == "__main__":
    test_server_config()
