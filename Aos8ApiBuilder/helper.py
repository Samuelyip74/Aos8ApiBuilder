import re
from typing import List, Dict, Union


def parse_system_output_json(cli_output: str) -> Dict[str, Union[str, dict]]:
    """
    Parses CLI output with section headers and key-value pairs into a nested dictionary.

    :param cli_output: Raw CLI output as a string
    :return: Dictionary representing parsed output
    """
    data = {}
    current_section = None
    section_indent = None

    lines = cli_output.strip().splitlines()

    for line in lines:
        indent_match = re.match(r'^(\s+)', line)
        indent = len(indent_match.group(1)) if indent_match else 0
        line = line.strip().rstrip(',')

        if line.endswith(':') and ':' not in line[:-1]:
            section_name = line[:-1].strip()
            data[section_name] = {}
            current_section = data[section_name]
            section_indent = indent
            continue

        if ':' in line:
            key, value = map(str.strip, line.split(':', 1))
            if current_section is not None and indent > section_indent:
                current_section[key] = value
            else:
                data[key] = value
                current_section = None
                section_indent = None

    return data


def parse_output_json(output: str) -> List[Dict[str, str]]:
    """
    Parses CLI table output with headers and fixed-format rows.

    :param output: Raw CLI output as a string
    :return: List of dictionaries mapping headers to values
    """
    lines = output.strip().splitlines()
    headers = re.split(r"\s{2,}", lines[0].strip())
    vlan_list = []

    for line in lines[2:]:
        if not line.strip():
            continue
        parts = re.split(r"\s{2,}", line.strip())
        vlan_list.append(dict(zip(headers, parts)))

    return vlan_list


def parse_vlan_output_json(output: str) -> List[Dict[str, str]]:
    """
    Parses VLAN CLI output in table format.

    :param output: Raw CLI output as a string
    :return: List of dictionaries per VLAN entry
    """
    return parse_output_json(output)


def parse_interface_status(cli_output: str) -> List[Dict[str, str]]:
    """
    Parses 'show interfaces' status CLI output.

    :param cli_output: Raw CLI output as a string
    :return: List of dictionaries per interface row
    """
    lines = cli_output.strip().splitlines()
    data_lines = []
    in_data = False

    for line in lines:
        if re.match(r"^\s*\d+/\d+/\d+", line):
            in_data = True
        if in_data:
            data_lines.append(line.strip())

    parsed = []
    for line in data_lines:
        parts = re.split(r'\s{2,}', line)
        if len(parts) < 13:
            continue
        parsed.append({
            "port": parts[0],
            "admin_status": parts[1],
            "auto_nego": parts[2],
            "det_speed": parts[3],
            "det_duplex": parts[4],
            "det_pause": parts[5],
            "det_fec": parts[6],
            "cfg_speed": parts[7],
            "cfg_duplex": parts[8],
            "cfg_pause": parts[9],
            "cfg_fec": parts[10],
            "link_trap": parts[11],
            "eee": parts[12],
        })

    return parsed


def parse_interface_detail(cli_output: str) -> Dict[str, Union[str, Dict[str, str]]]:
    """
    Parses 'show interface detail' CLI output including Rx and Tx subsections.

    :param cli_output: Raw CLI output as a string
    :return: Dictionary with top-level and Rx/Tx values
    """
    data = {}
    rx_section = {}
    tx_section = {}

    lines = cli_output.strip().splitlines()
    current_section = "general"

    for line in lines:
        line = line.strip()
        if line.startswith("ACSW"):
            continue
        if line.startswith("Rx"):
            current_section = "rx"
            continue
        elif line.startswith("Tx"):
            current_section = "tx"
            continue

        if ":" in line:
            parts = line.split(":")
            key = parts[0].strip()
            value = ":".join(parts[1:]).strip().rstrip(",")

            if "," in value:
                sub_parts = [v.strip() for v in value.split(",")]
                for sub_part in sub_parts:
                    if ":" in sub_part:
                        sub_key, sub_val = map(str.strip, sub_part.split(":", 1))
                        key = f"{key} / {sub_key}"
                        value = sub_val

            if current_section == "rx":
                rx_section[key] = value
            elif current_section == "tx":
                tx_section[key] = value
            else:
                data[key] = value

    if rx_section:
        data["Rx"] = rx_section
    if tx_section:
        data["Tx"] = tx_section

    return data


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
        if re.match(r'-{10,}', line):
            start_parsing = True
            continue
        if start_parsing and line.strip():
            data_lines.append(line.strip())

    interfaces = []
    for line in data_lines:
        parts = re.split(r'\s{2,}', line)
        if len(parts) >= 5:
            interfaces.append({
                "name": parts[0],
                "ip_address": parts[1],
                "subnet_mask": parts[2],
                "status": parts[3],
                "forward": parts[4],
                "device": parts[5] if len(parts) > 5 else None
            })

    return interfaces
