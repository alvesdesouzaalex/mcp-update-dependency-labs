import requests
import json
import xml.etree.ElementTree as ET
import re

def get_latest_maven_version(group: str, artifact: str) -> str:
    """Gets the latest version of a Maven artifact from Maven Central."""
    url = f"https://search.maven.org/solrsearch/select?q=g:\"{group}\"+AND+a:\"{artifact}\"&rows=1&wt=json"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        if data["response"]["docs"]:
            return data["response"]["docs"][0]["latestVersion"]
    except Exception as e:
        print(f"Error fetching Maven version for {group}:{artifact}: {e}")
    return None

def get_latest_npm_version(package: str) -> str:
    """Gets the latest version of an NPM package."""
    url = f"https://registry.npmjs.org/{package}/latest"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        return data["version"]
    except Exception as e:
        print(f"Error fetching NPM version for {package}: {e}")
    return None

def update_pom_xml(content: str, updates: dict) -> str:
    """
    Updates versions in pom.xml content.
    updates: { (group, artifact): new_version }
    """
    # Using regex to preserve formatting more reliably than ET for Pom files
    new_content = content
    for (group, artifact), version in updates.items():
        # Match dependency block for g and a
        pattern = rf"(<dependency>\s*<groupId>{group}</groupId>\s*<artifactId>{artifact}</artifactId>\s*<version>)(.*?)(</version>)"
        new_content = re.sub(pattern, rf"\g<1>{version}\g<3>", new_content, flags=re.DOTALL)
    return new_content

def update_package_json(content: str, updates: dict) -> str:
    """
    Updates versions in package.json content.
    updates: { package_name: new_version }
    """
    data = json.loads(content)
    for section in ["dependencies", "devDependencies"]:
        if section in data:
            for pkg, version in updates.items():
                if pkg in data[section]:
                    # Keep ^ or ~ if present? The user said "versoes mais recentes", 
                    # usually implies fixed versions or keeping the prefix.
                    # Let's assume fixed version for the update.
                    data[section][pkg] = version
    return json.dumps(data, indent=2)
