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

def scan_maven_dependencies(content: str) -> dict:
    """Scans pom.xml for dependencies that have an explicit <version> tag."""
    deps = {}
    try:
        # Namespace handling for Maven
        namespace = {'mvn': 'http://maven.apache.org/POM/4.0.0'}
        # We use a temporary file or just wrap the content to ensure it’s valid XML
        root = ET.fromstring(content)
        
        # Find dependencies in <dependencies> section
        for dep in root.findall(".//mvn:dependency", namespace):
            group = dep.find("mvn:groupId", namespace)
            artifact = dep.find("mvn:artifactId", namespace)
            version = dep.find("mvn:version", namespace)
            
            if group is not None and artifact is not None and version is not None:
                # We skip those with variables ${...} for this lab’s simplicity
                if not version.text.startswith("${"):
                    deps[(group.text.strip(), artifact.text.strip())] = version.text.strip()
    except Exception as e:
        print(f"Error scanning Maven dependencies: {e}")
    return deps

def scan_npm_dependencies(content: str) -> dict:
    """Scans package.json for all dependencies."""
    deps = {}
    try:
        data = json.loads(content)
        for section in ["dependencies", "devDependencies"]:
            if section in data:
                for pkg, ver in data[section].items():
                    # Clean the version of ^ or ~ for latest comparison
                    clean_ver = re.sub(r'^[\^~]', '', ver)
                    deps[pkg] = clean_ver
    except Exception as e:
        print(f"Error scanning NPM dependencies: {e}")
    return deps

def update_pom_xml(content: str, updates: dict) -> str:
    """Updates versions in pom.xml content using regex to preserve formatting."""
    new_content = content
    for (group, artifact), version in updates.items():
        pattern = rf"(<dependency>\s*<groupId>{group}</groupId>\s*<artifactId>{artifact}</artifactId>\s*<version>)(.*?)(</version>)"
        new_content = re.sub(pattern, rf"\g<1>{version}\g<3>", new_content, flags=re.DOTALL)
    return new_content

def update_package_json(content: str, updates: dict) -> str:
    """Updates versions in package.json content."""
    data = json.loads(content)
    for section in ["dependencies", "devDependencies"]:
        if section in data:
            for pkg, version in updates.items():
                if pkg in data[section]:
                    data[section][pkg] = version
    return json.dumps(data, indent=2)
