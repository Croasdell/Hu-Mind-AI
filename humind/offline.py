"""Fail-closed endpoint policy for the air-gapped reference system."""

from __future__ import annotations

from dataclasses import dataclass
import ipaddress
from urllib.parse import urlparse


class OfflinePolicyError(ValueError):
    """Raised when an endpoint crosses the configured offline boundary."""


@dataclass(frozen=True)
class OfflineNetworkPolicy:
    """Permit loopback plus explicitly named hosts on an isolated LAN.

    Hostnames are compared exactly and IP addresses must be contained in an
    explicitly configured network. Empty allowlists therefore mean loopback
    only. This validates application endpoints; host firewall rules remain a
    separate deployment requirement.
    """

    allowed_hosts: tuple[str, ...] = ()
    allowed_networks: tuple[str, ...] = ()

    def validate_url(self, url: str) -> str:
        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"} or not parsed.hostname:
            raise OfflinePolicyError("endpoint must be an absolute HTTP(S) URL")
        if parsed.username or parsed.password:
            raise OfflinePolicyError("credentials must not be embedded in endpoint URLs")

        host = parsed.hostname.rstrip(".").lower()
        if host == "localhost":
            return url.rstrip("/")
        try:
            address = ipaddress.ip_address(host)
        except ValueError:
            if host not in {item.rstrip(".").lower() for item in self.allowed_hosts}:
                raise OfflinePolicyError(f"host {host!r} is outside the offline allowlist")
            return url.rstrip("/")

        if address.is_loopback:
            return url.rstrip("/")
        networks = tuple(ipaddress.ip_network(item, strict=True) for item in self.allowed_networks)
        if not any(address in network for network in networks):
            raise OfflinePolicyError(f"address {address} is outside the offline allowlist")
        return url.rstrip("/")
