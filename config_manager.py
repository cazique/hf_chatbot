"""Configuration management for AI providers.

This module encapsulates reading and writing of the AI provider
configuration file.  The configuration file is stored in JSON
format and contains a list of provider definitions as well as
the identifier of the currently active provider.  To prevent
concurrent writes and ensure thread safety when running under a
WSGI server, file operations are protected by a threading lock.

Example configuration file (ai_config.json)
-----------------------------------------

::

    {
        "default_provider": "ollama_cloud_default",
        "providers": [
            {
                "id": "ollama_cloud_default",
                "name": "Ollama Cloud (Default)",
                "type": "ollama",
                "api_key": "YOUR_API_KEY",
                "base_url": "https://ollama.com",
                "model": "gpt-oss:20b-cloud"
            }
        ]
    }

The :class:`ConfigManager` allows adding, removing and activating
providers through simple methods.  To obtain an instance of the
currently active provider, see :func:`get_active_provider`.
"""

from __future__ import annotations

import json
import os
from threading import Lock
from typing import Dict, List, Optional

from ia_providers import LLMProvider, OllamaCloudProvider


class ConfigManager:
    """Manage persistent configuration for AI providers.

    Parameters
    ----------
    config_path: str
        Path to the JSON configuration file.  If the file does not
        exist, it will be created with an empty configuration on
        initialisation.
    """

    def __init__(self, config_path: str = "ai_config.json") -> None:
        self.config_path = config_path
        self._lock = Lock()
        # Ensure that the configuration file exists
        if not os.path.exists(self.config_path):
            default_config: Dict[str, object] = {
                "default_provider": None,
                "providers": [],
            }
            self._write_config(default_config)

    def _read_config(self) -> Dict[str, object]:
        """Read the JSON configuration from disk.

        Returns
        -------
        dict
            The parsed configuration.
        """
        with self._lock:
            with open(self.config_path, "r", encoding="utf-8") as f:
                return json.load(f)

    def _write_config(self, config: Dict[str, object]) -> None:
        """Write the JSON configuration to disk atomically.

        Parameters
        ----------
        config: dict
            The configuration data to write.
        """
        with self._lock:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=4)

    def load_config(self) -> Dict[str, object]:
        """Return the current configuration dictionary."""
        return self._read_config()

    def save_config(self, config: Dict[str, object]) -> None:
        """Persist the given configuration to disk."""
        self._write_config(config)

    def add_provider(self, provider: Dict[str, object]) -> None:
        """Add a new provider to the configuration.

        If this is the first provider being added, it will also be set
        as the default provider.

        Parameters
        ----------
        provider: dict
            A dictionary describing the provider.  Required keys
            include ``id``, ``name``, ``type`` and ``api_key``.  Optional
            keys include ``base_url`` and ``model``.
        """
        config = self.load_config()
        providers: List[Dict[str, object]] = config.get("providers", [])
        providers.append(provider)
        config["providers"] = providers
        # Set default if none currently set
        if not config.get("default_provider"):
            config["default_provider"] = provider.get("id")
        self.save_config(config)

    def remove_provider(self, provider_id: str) -> None:
        """Remove a provider by its identifier.

        If the removed provider is the current default, another
        provider will be promoted to default if available; otherwise
        ``default_provider`` will be set to ``None``.

        Parameters
        ----------
        provider_id: str
            Identifier of the provider to remove.
        """
        config = self.load_config()
        providers: List[Dict[str, object]] = config.get("providers", [])
        providers = [p for p in providers if p.get("id") != provider_id]
        config["providers"] = providers
        if config.get("default_provider") == provider_id:
            config["default_provider"] = providers[0].get("id") if providers else None
        self.save_config(config)

    def activate_provider(self, provider_id: str) -> None:
        """Set a provider as the active/default provider.

        Parameters
        ----------
        provider_id: str
            Identifier of the provider to activate.
        """
        config = self.load_config()
        config["default_provider"] = provider_id
        self.save_config(config)

    def get_provider_by_id(self, provider_id: str) -> Optional[Dict[str, object]]:
        """Return the provider definition matching the given identifier.

        Parameters
        ----------
        provider_id: str
            Identifier of the provider to locate.

        Returns
        -------
        dict or None
            The provider dictionary if found, otherwise ``None``.
        """
        config = self.load_config()
        for provider in config.get("providers", []):
            if provider.get("id") == provider_id:
                return provider
        return None


def get_active_provider(config_manager: ConfigManager) -> Optional[LLMProvider]:
    """Instantiate and return the active LLM provider.

    This helper reads the configuration via ``config_manager``,
    determines the default provider and constructs the appropriate
    concrete provider instance.  If no active provider is set or
    the provider type is unknown, ``None`` is returned.

    Parameters
    ----------
    config_manager: ConfigManager
        The configuration manager responsible for reading the config.

    Returns
    -------
    Optional[LLMProvider]
        An instance of :class:`LLMProvider` or ``None`` if no
        active provider exists.
    """
    config = config_manager.load_config()
    provider_id = config.get("default_provider")
    if not provider_id:
        return None
    provider_data = config_manager.get_provider_by_id(provider_id)
    if not provider_data:
        return None
    ptype = provider_data.get("type")
    api_key = provider_data.get("api_key")
    base_url = provider_data.get("base_url") or ""
    name = provider_data.get("name", provider_id)
    model = provider_data.get("model")
    # Instantiate based on provider type
    if ptype == "ollama":
        return OllamaCloudProvider(
            provider_id=provider_id,
            name=name,
            api_key=api_key or "",
            base_url=base_url or "https://ollama.com",
            model=model or "gpt-oss:20b-cloud",
        )
    # Placeholder for future provider types (openai, anthropic, etc.)
    return None