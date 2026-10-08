"""Async HTTP client for Juice Goose IP-series controllers."""

from __future__ import annotations

import logging
import xml.etree.ElementTree as ET
from typing import TypedDict

import aiohttp
from yarl import URL

from .const import (
	MANUAL_OVERRIDE_STATUS_TAG,
	MIN_SEQUENCE_DELAY_SECONDS,
	POD_CONTROL_PATHS,
	POD_NAMES,
	POD_STATUS_TAGS,
	QUERY_DELAY,
	QUERY_STATUS,
	SEQUENCE_DOWN,
	SEQUENCE_PATH,
	SEQUENCE_STATUS_TAG,
	SEQUENCE_UP,
	STATUS_OFF,
	STATUS_ON,
	STATUS_PATH,
)

_LOGGER = logging.getLogger(__name__)
REQUEST_TIMEOUT = 10


class JuiceGooseStatus(TypedDict):
	"""Decoded state returned by the controller's status XML endpoint."""

	pods: dict[int, bool]
	sequence_active: bool
	manual_override: bool


class JuiceGooseApiError(Exception):
	"""Raised when a controller request fails."""


class JuiceGooseInvalidResponseError(JuiceGooseApiError):
	"""Raised when the controller returns malformed or incomplete status XML."""


class JuiceGooseApi:
	"""Communicate with an IP-series controller over its HTTP API."""

	def __init__(self, host: str, port: int, session: aiohttp.ClientSession) -> None:
		self._base_url = URL.build(scheme="http", host=host, port=port)
		self._session = session

	async def async_get_status(self) -> JuiceGooseStatus:
		"""Fetch and parse POD, sequence, and manual override states."""
		response_text = await self._async_request(STATUS_PATH)
		try:
			root = ET.fromstring(response_text)
		except ET.ParseError as err:
			raise JuiceGooseInvalidResponseError("Status response is not valid XML") from err

		pods = {
			pod: self._read_boolean(root, POD_STATUS_TAGS[pod])
			for pod in POD_NAMES
		}
		return {
			"pods": pods,
			"sequence_active": self._read_boolean(root, SEQUENCE_STATUS_TAG),
			"manual_override": self._read_boolean(
				root, MANUAL_OVERRIDE_STATUS_TAG
			),
		}

	async def async_set_pod(self, pod: int, is_on: bool) -> None:
		"""Set one POD's state using its documented CGI endpoint."""
		if pod not in POD_CONTROL_PATHS:
			raise ValueError(f"Unknown POD: {pod}")
		status = STATUS_ON if is_on else STATUS_OFF
		await self._async_request(
			POD_CONTROL_PATHS[pod], params={QUERY_STATUS: str(status)}
		)

	async def async_start_sequence(self, sequence: int, delay: int) -> None:
		"""Start an UP or DOWN sequence with the requested inter-POD delay."""
		if sequence not in (SEQUENCE_DOWN, SEQUENCE_UP):
			raise ValueError(f"Unknown sequence: {sequence}")
		if delay < MIN_SEQUENCE_DELAY_SECONDS:
			raise ValueError(
				f"Sequence delay must be at least {MIN_SEQUENCE_DELAY_SECONDS} seconds"
			)
		await self._async_request(
			SEQUENCE_PATH,
			params={QUERY_STATUS: str(sequence), QUERY_DELAY: str(delay)},
		)

	async def _async_request(
		self, path: str, *, params: dict[str, str] | None = None
	) -> str:
		"""Perform a bounded GET request and return its response body."""
		url = self._base_url.with_path(path)
		try:
			async with self._session.get(
				url,
				params=params,
				timeout=aiohttp.ClientTimeout(total=REQUEST_TIMEOUT),
			) as response:
				response.raise_for_status()
				return await response.text()
		except (aiohttp.ClientError, TimeoutError) as err:
			_LOGGER.error("Request to Juice Goose controller failed: %s", err)
			raise JuiceGooseApiError("Unable to communicate with controller") from err

	@staticmethod
	def _read_boolean(root: ET.Element, tag: str) -> bool:
		"""Read a required 0/1 state element from the status response."""
		element = root.find(tag)
		if element is None or element.text is None:
			raise JuiceGooseInvalidResponseError(
				f"Status response is missing the {tag} element"
			)
		value = element.text.strip()
		if value not in ("0", "1"):
			raise JuiceGooseInvalidResponseError(
				f"Status element {tag} has invalid value {value!r}"
			)
		return value == "1"