Act as an expert Home Assistant integration developer and Python engineer. I am creating a custom Home Assistant integration (designed to be managed via HACS) for the Juice Goose IP 15-15 IP-addressable power sequencer using its Telnet protocol. 

Please scaffold and generate the foundational file structure, class boilerplate, and core async Telnet communication logic for this custom integration.

### Device & Protocol Requirements:
1. **Target Hardware:** Juice Goose IP 15-15 (IP-addressable AC power sequencer / power distribution unit).
2. **Communication Protocol:** Telnet over TCP.
3. **Control Model:**
   - Controls individual or sequenced AC power outlets/PODs via raw ASCII/Telnet commands.
   - Requires an asynchronous persistent Telnet connection manager (using `asyncio.open_connection` or `aagnotelnet`/`async-telnet` pattern) that handles reconnection, state polling, and command sending without blocking the Home Assistant event loop.

### Integration Architecture & Standards:
- Follow current Home Assistant developer guidelines and modern async standards (`async_setup_entry`).
- Implement the integration using the **Config Flow** UI flow (no YAML configuration). Include discovery/manual IP + Port entry and validation (attempting a test Telnet connection before creating the config entry).
- Domain name: `juicegoose_ip1515`
- Platforms to support: `switch` (for individual outlet POD control) and `sensor` or `binary_sensor` (for connection status and system state).
- Use an `DataUpdateCoordinator` or dedicated custom `DataUpdateCoordinator` wrapper to manage polling intervals, command queuing, and state tracking.

### Deliverables to Generate:
Generate a clean, production-ready project file tree and the full implementation for the core files:

1. `custom_components/juicegoose_ip1515/manifest.json`
   - Configured with domain, integration name, version (`0.1.0`), documentation URL, codeowners, and `config_flow: true`.
2. `custom_components/juicegoose_ip1515/const.py`
   - Constants for DOMAIN, DEFAULT_PORT (typically port 23), DEFAULT_SCAN_INTERVAL, switch/POD mapping, and command strings.
3. `custom_components/juicegoose_ip1515/telnet_client.py`
   - An isolated, robust `asyncio`-based Telnet client class capable of:
     - Connecting to `host:port`.
     - Sending ASCII commands (e.g., status queries, sequence triggers, individual outlet ON/OFF).
     - Parsing ASCII raw responses into clean dictionary/state objects.
     - Gracefully handling timeouts, disconnections, and retries.
4. `custom_components/juicegoose_ip1515/config_flow.py`
   - User step prompting for `host` and `port`.
   - Async validation callback testing the Telnet connection before finalizing setup.
5. `custom_components/juicegoose_ip1515/__init__.py`
   - Entry point establishing the connection manager, setting up `entry.runtime_data` or `hass.data[DOMAIN]`, and forwarding setups to the `switch` platform.
6. `custom_components/juicegoose_ip1515/switch.py`
   - `JuiceGooseSwitch` entity inheriting from `SwitchEntity`.
   - Implementation of `async_turn_on`, `async_turn_off`, and state updates tied to the Telnet client.

Ensure all code includes type hints, async execution throughout, clear docstrings, and robust error logging via `logging.getLogger(__name__)`.