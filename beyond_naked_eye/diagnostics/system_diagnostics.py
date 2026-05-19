from __future__ import annotations

import platform
import socket
from dataclasses import dataclass, asdict
from typing import Any


@dataclass
class SystemStatus:
    hostname: str
    os: str
    os_version: str
    machine: str
    processor: str


@dataclass
class NetworkStatus:
    local_ip: str
    gateway_hint: str
    dns_servers: list[str]
    interfaces: list[str]
    wifi_ssid: str
    wifi_signal: str
    bandwidth_note: str


@dataclass
class DeviceInfo:
    bluetooth_enabled: str
    paired_devices: list[str]
    lan_discovery_enabled: bool
    lan_devices: list[str]


def get_system_status() -> SystemStatus:
    return SystemStatus(
        hostname=socket.gethostname(),
        os=platform.system(),
        os_version=platform.version(),
        machine=platform.machine(),
        processor=platform.processor() or "unknown",
    )


def get_network_status() -> NetworkStatus:
    host = socket.gethostname()
    ip = socket.gethostbyname(host)
    dns_hint = ["Check OS resolver config (ipconfig /all or resolv.conf)"]
    interfaces = [name[1] for name in socket.getaddrinfo(host, None) if name and len(name) > 1]
    interfaces = sorted(set(interfaces))
    return NetworkStatus(
        local_ip=ip,
        gateway_hint="Auto-detection not available cross-platform without optional adapters",
        dns_servers=dns_hint,
        interfaces=interfaces,
        wifi_ssid="Unavailable (optional OS adapter required)",
        wifi_signal="Unavailable",
        bandwidth_note="Install psutil for interface throughput stats",
    )


def get_device_info(enable_lan_discovery: bool = False) -> DeviceInfo:
    lan_devices = []
    if enable_lan_discovery:
        lan_devices = ["Authorized basic LAN discovery placeholder (implement ARP adapter)"]
    return DeviceInfo(
        bluetooth_enabled="Unknown (use OS-specific adapter)",
        paired_devices=["Use OS-specific paired-device query adapters"],
        lan_discovery_enabled=enable_lan_discovery,
        lan_devices=lan_devices,
    )


def run_diagnostics(enable_lan_discovery: bool = False) -> dict[str, Any]:
    return {
        "system": asdict(get_system_status()),
        "network": asdict(get_network_status()),
        "device": asdict(get_device_info(enable_lan_discovery)),
        "summary": "Diagnostics completed in safe, non-invasive mode.",
    }
