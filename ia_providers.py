"""LLM Providers abstraction and concrete implementations.

This module defines a base class for Large Language Model (LLM) providers
and concrete implementations for supported services. A provider is
responsible for handling the low‑level API communication with an AI
service (such as Ollama Cloud, OpenAI, Anthropic, etc.) and exposing
a simple, unified interface (`generate_response`) to the rest of the
application.  Additional helper methods like `test_connection` can be
implemented by each provider to verify that credentials and endpoints
are working correctly.

The design follows the Strategy pattern: the application holds a
reference to an `LLMProvider` without caring about the concrete
implementation.  Swapping providers only requires updating the
configuration; no changes to business logic are necessary.
"""

from __future__ import annotations

import requests
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class LLMProvider(ABC):
    """Abstract base class for Large Language Model providers.

    All provider implementations must inherit from this class and
    implement the :meth:`generate_response` method.  Optionally,
    providers can override :meth:`test_connection` to perform a
    health check against the remote API.

    Attributes
    ----------
    provider_id: str
        Unique identifier for the provider instance.  This value is
        assigned by the configuration manager and is used to reference
        providers in the UI and storage.
    name: str
        Human‑friendly name of the provider (e.g. "Ollama Cloud").
    provider_type: str
        Shorthand type of the provider (e.g. "ollama", "openai").
    api_key: Optional[str]
        API key required to authenticate with the provider.  Some
        providers may not require a key if running locally.
    base_url: str
        Base URL of the provider's HTTP API.  This value should not
        include trailing slashes.  For example, ``https://ollama.com``.
    model: Optional[str]
        Name of the default model to use when none is provided by the
        caller.  Providers can override this in their constructor.
    """

    def __init__(
        self,
        provider_id: str,
        name: str,
        provider_type: str,
        api_key: Optional[str] = None,
        base_url: str = "",
        model: Optional[str] = None,
    ) -> None:
        self.provider_id = provider_id
        self.name = name
        self.provider_type = provider_type
        self.api_key = api_key
        self.base_url = base_url.rstrip("/") if base_url else ""
        self.model = model

    @abstractmethod
    def generate_response(self, prompt: str, model: Optional[str] = None, **kwargs: Any) -> Dict[str, Any]:
        """Generate a completion for a given prompt.

        Concrete providers must implement this method to call their
        respective APIs.  The method should raise an exception if
        something goes wrong (e.g. authentication failure, network
        error) so that callers can handle errors appropriately.

        Parameters
        ----------
        prompt: str
            The user's prompt to the model.
        model: Optional[str], default None
            Optional override for the model name.  If ``None``, the
            provider's default ``model`` attribute will be used.
        **kwargs: Any
            Additional provider‑specific parameters (e.g. system
            messages, temperature, max tokens) can be passed via
            keyword arguments.  Providers should document any extra
            options they support.

        Returns
        -------
        dict
            A JSON‑serialisable dictionary containing the API
            response.  Each provider is free to shape this
            dictionary as appropriate, but at a minimum it should
            include the generated text under a reasonable key (e.g.
            ``"response"``).
        """

    def test_connection(self) -> bool:
        """Test whether the provider's API is reachable.

        By default, this method simply returns ``True``.  Concrete
        providers should override this method and perform a trivial
        call against their API (such as listing available models).
        If any exception is raised, the UI will report the provider
        as unreachable.

        Returns
        -------
        bool
            ``True`` if the provider is reachable; otherwise ``False``.
        """
        return True


class OllamaCloudProvider(LLMProvider):
    """Concrete provider for Ollama Cloud.

    This implementation uses Ollama's REST API to generate text
    completions.  Authentication is performed via the ``Authorization``
    header using a bearer token.  For more information on the API,
    consult Ollama's documentation: https://docs.ollama.com/cloud.
    """

    def __init__(
        self,
        provider_id: str,
        name: str,
        api_key: str,
        base_url: str = "https://ollama.com",
        model: str = "gpt-oss:20b-cloud",
    ) -> None:
        super().__init__(
            provider_id=provider_id,
            name=name,
            provider_type="ollama",
            api_key=api_key,
            base_url=base_url,
            model=model,
        )

    def _request_headers(self) -> Dict[str, str]:
        """Build standard headers for Ollama Cloud requests.

        Returns
        -------
        dict
            HTTP headers including the bearer token if provided.
        """
        headers: Dict[str, str] = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def generate_response(self, prompt: str, model: Optional[str] = None, **kwargs: Any) -> Dict[str, Any]:
        """Generate a completion using Ollama's /api/generate endpoint.

        Parameters
        ----------
        prompt: str
            The input prompt to send to the model.
        model: Optional[str]
            Optionally override the configured model.  If not
            provided, the default model specified during
            instantiation will be used.
        **kwargs: Any
            Additional options supported by the API, such as
            ``stream`` or ``format``.  Unsupported keys are
            silently ignored.

        Returns
        -------
        dict
            The JSON response from the Ollama API.

        Raises
        ------
        requests.HTTPError
            If the API returns an error status code.
        requests.RequestException
            If there is a network‑related error.
        """
        if not self.base_url:
            raise ValueError("Base URL for Ollama provider is not configured")
        used_model = model or self.model
        if not used_model:
            raise ValueError("No model specified for Ollama provider")
        # Build the request payload
        payload: Dict[str, Any] = {
            "model": used_model,
            "prompt": prompt,
            # stream disabled by default; clients may override via kwargs
            "stream": kwargs.pop("stream", False),
        }
        # Merge any additional supported keys into the payload
        allowed_keys = {"format", "system", "template", "context"}
        for key, value in kwargs.items():
            if key in allowed_keys:
                payload[key] = value
        endpoint = f"{self.base_url}/api/generate"
        response = requests.post(
            endpoint,
            json=payload,
            headers=self._request_headers(),
            timeout=60,
        )
        # Raise an exception for non‑success status codes
        response.raise_for_status()
        return response.json()

    def test_connection(self) -> bool:
        """Check connectivity by listing available models.

        This method calls the `/api/tags` endpoint, which returns
        metadata about models available to the authenticated user.  A
        successful response indicates that the API key and base URL
        are valid.

        Returns
        -------
        bool
            ``True`` if the request succeeds, otherwise ``False``.
        """
        if not self.base_url:
            return False
        try:
            endpoint = f"{self.base_url}/api/tags"
            resp = requests.get(endpoint, headers=self._request_headers(), timeout=10)
            resp.raise_for_status()
            return True
        except Exception:
            return False