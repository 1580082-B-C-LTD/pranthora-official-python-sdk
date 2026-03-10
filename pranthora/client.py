from typing import Optional, Dict, Any, List
import threading
import time

from pranthora.utils.api_requestor import APIRequestor
from pranthora.api_resources.agents import Agents
from pranthora.api_resources.calls import Calls


class Pranthora:
    def __init__(self, api_key: str, base_url: str = "https://7e3a-14-139-122-139.ngrok-free.app"):
        """
        Initialize the Pranthora client.

        Args:
            api_key: Your Pranthora API key.
            base_url: The base URL for the API (must include /api/v1).
                      Defaults to https://api.pranthora.com/api/v1.
                      Use "http://localhost:5050/api/v1" for local development.
        """
        self.api_key = api_key
        self.base_url = base_url

        self.requestor = APIRequestor(api_key, base_url)

        # Resources
        self.agents = Agents(self.requestor)
        self.calls = Calls(self.requestor)

        # Track last outbound call for stop()
        self._last_call_sid: Optional[str] = None
        self._last_from_phone_number: Optional[str] = None

    def start(
        self,
        agent_id: Optional[str] = None,
        to_phone_number: Optional[str] = None,
        from_number: Optional[str] = None,
        assistant_overrides: Optional[Dict[str, Any]] = None,
        provider: Optional[str] = "twilio",
    ) -> Dict[str, Any]:
        """
        Start a real-time voice call.

        For outbound phone calls: pass to_phone_number and optionally from_number.
        The backend will use your attached phone number to call to_phone_number
        and connect the call to the agent mapped to that phone number.

        Args:
            agent_id: Deprecated - agent is determined by phone mapping.
            to_phone_number: Phone number to call (e.g. "+1234567890"). Required for outbound.
            from_number: The phone number to call from. If not provided, backend selects one.
            assistant_overrides: Optional overrides (e.g. variableValues). Reserved for future use.

        Returns:
            Dict with status, call_sid, from_phone_number, etc. Use call_sid with stop() to hang up.
        """
        if not to_phone_number:
            raise ValueError(
                "to_phone_number is required for outbound calls. "
                "Example: client.start(agent_id='...', to_phone_number='+1234567890')"
            )
        result = self.calls.create(phone_number=to_phone_number, from_number=from_number, agent_id=agent_id, provider=provider)
        self._last_call_sid = result.get("call_sid")
        self._last_from_phone_number = result.get("from_phone_number")
        return result

    def stop(
        self,
        call_sid: Optional[str] = None,
        from_phone_number: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Stop (hang up) an active call.

        Args:
            call_sid: Twilio call SID. If omitted, uses the call from the last start().
            from_phone_number: Your Twilio number that placed the call. If omitted, uses the one from last start().

        Returns:
            Dict with status from the API.
        """
        sid = call_sid or self._last_call_sid
        if not sid:
            raise ValueError(
                "No call_sid provided and no recent call. "
                "Pass call_sid (and optionally from_phone_number) or call start() first."
            )
        from_phone = from_phone_number or self._last_from_phone_number
        return self.calls.stop(call_sid=sid, from_phone_number=from_phone)

    def start_multiple(
        self,
        call_configs: List[Dict[str, Any]],
        delay_between_calls: float = 0.0,
    ) -> List[Dict[str, Any]]:
        """
        Start multiple real-time voice calls simultaneously or with a delay.

        Args:
            call_configs: List of call configurations. Each config should contain:
                - to_phone_number: Phone number to call (required)
                - from_number: Phone number to call from (optional)
                - agent_id: Agent ID (optional, deprecated)
                - provider: Call provider (optional, defaults to "twilio")
            delay_between_calls: Delay in seconds between starting each call (default: 0.0 for simultaneous)

        Returns:
            List of results from each call start, in the same order as call_configs.
            Each result contains status, call_sid, from_phone_number, etc.
        """
        results = []
        threads = []

        def start_single_call(config: Dict[str, Any], index: int):
            try:
                result = self.start(
                    agent_id=config.get("agent_id"),
                    to_phone_number=config.get("to_phone_number"),
                    from_number=config.get("from_number"),
                    provider=config.get("provider", "twilio"),
                )
                results.append((index, result))
            except Exception as e:
                results.append((index, {"error": str(e), "config": config}))

        # Start threads for each call
        for i, config in enumerate(call_configs):
            if not config.get("to_phone_number"):
                results.append((i, {"error": "to_phone_number is required", "config": config}))
                continue

            thread = threading.Thread(target=start_single_call, args=(config, i))
            threads.append(thread)
            thread.start()

            if delay_between_calls > 0 and i < len(call_configs) - 1:
                time.sleep(delay_between_calls)

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Sort results by index to maintain order
        results.sort(key=lambda x: x[0])
        return [result for _, result in results]

    def stop_multiple(
        self,
        call_details: List[Dict[str, str]],
    ) -> List[Dict[str, Any]]:
        """
        Stop multiple active calls.

        Args:
            call_details: List of call details. Each should contain:
                - call_sid: The call SID to stop (required)
                - from_phone_number: The phone number that placed the call (optional)

        Returns:
            List of results from each call stop, in the same order as call_details.
        """
        results = []
        threads = []

        def stop_single_call(detail: Dict[str, str], index: int):
            try:
                result = self.stop(
                    call_sid=detail.get("call_sid"),
                    from_phone_number=detail.get("from_phone_number"),
                )
                results.append((index, result))
            except Exception as e:
                results.append((index, {"error": str(e), "detail": detail}))

        # Start threads for each stop
        for i, detail in enumerate(call_details):
            if not detail.get("call_sid"):
                results.append((i, {"error": "call_sid is required", "detail": detail}))
                continue

            thread = threading.Thread(target=stop_single_call, args=(detail, i))
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Sort results by index to maintain order
        results.sort(key=lambda x: x[0])
        return [result for _, result in results]
