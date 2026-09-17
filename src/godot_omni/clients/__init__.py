"""Clients package for Godot Omni."""

from godot_omni.clients.manager import ClientManager
from godot_omni.clients.models import (
    ClientDescriptor,
    ClientReport,
    ClientStatus,
    ConfigFormat,
)
from godot_omni.clients.registry import get_known_client_descriptors

__all__ = [
    "ClientManager",
    "ClientDescriptor",
    "ClientReport",
    "ClientStatus",
    "ConfigFormat",
    "get_known_client_descriptors",
]
