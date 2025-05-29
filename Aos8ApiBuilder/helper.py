
import re
import json
from typing import List, Dict, Union

def parse_system_output_json(cli_output: str) -> Dict[str, Union[str, dict]]:
    data = {}
    current_section = None
    section_indent = None

    lines = cli_output.strip().splitlines()
    
    for line in lines:
        # Normalize indentation
        indent_match = re.match(r'^(\s+)', line)
        indent = len(indent_match.group(1)) if indent_match else 0
        line = line.strip().rstrip(',')

        # Section header (e.g. "Flash Space:")
        if line.endswith(':') and not ':' in line[:-1]:
            section_name = line[:-1].strip()
            data[section_name] = {}
            current_section = data[section_name]
            section_indent = indent
            continue

        # Key-value pair
        if ':' in line:
            key, value = map(str.strip, line.split(':', 1))
            # If we're in a section, add to it
            if current_section is not None and indent > section_indent:
                current_section[key] = value
            else:
                # Top-level field
                data[key] = value
                current_section = None
                section_indent = None

    return data

def parse_output_json(output: str):
    lines = output.strip().splitlines()
    
    # Find the header line
    header_line = lines[0]
    headers = re.split(r"\s{2,}", header_line.strip())  # split on 2+ spaces

    # Parse each data line
    vlan_list = []
    for line in lines[2:]:  # skip header + separator line
        if not line.strip():
            continue
        parts = re.split(r"\s{2,}", line.strip())
        entry = dict(zip(headers, parts))
        vlan_list.append(entry)

    return vlan_list


def parse_vlan_output_json(output: str):
    lines = output.strip().splitlines()
    
    # Find the header line
    header_line = lines[0]
    headers = re.split(r"\s{2,}", header_line.strip())  # split on 2+ spaces

    # Parse each data line
    vlan_list = []
    for line in lines[2:]:  # skip header + separator line
        if not line.strip():
            continue
        parts = re.split(r"\s{2,}", line.strip())
        entry = dict(zip(headers, parts))
        vlan_list.append(entry)

    return vlan_list


def parse_ip_interface_output(cli_output: str) -> List[Dict[str, str]]:
    """
    Parses the 'show ip interface' CLI output into a list of dictionaries.

    :param cli_output: Raw CLI output as a string
    :return: List of dictionaries with parsed interface data
    """
    lines = cli_output.strip().splitlines()
    data_lines = []
    start_parsing = False

    for line in lines:
        # Look for the line of dashes that separates the header from the data
        if re.match(r'-{10,}', line):
            start_parsing = True
            continue
        if start_parsing and line.strip():
            data_lines.append(line)

    interfaces = []
    for line in data_lines:
        # Split by 2+ spaces to get columns
        parts = re.split(r'\s{2,}', line.strip())
        if len(parts) >= 5:
            interface = {
                "name": parts[0],
                "ip_address": parts[1],
                "subnet_mask": parts[2],
                "status": parts[3],
                "forward": parts[4],
                "device": parts[5] if len(parts) > 5 else None
            }
            interfaces.append(interface)

    return interfaces


