"""mini-swe-agent model that offers TWO tools: `bash` and `run_tests`."""
import litellm

from minisweagent.exceptions import FormatError
from minisweagent.models.litellm_model import LitellmModel
from minisweagent.models.utils.actions_toolcall import BASH_TOOL, parse_toolcall_actions
import json

RUN_TESTS_TOOL = {
    "type": "function",
    "function": {
        "name": "run_tests",
        "description": "Run the project's test suite and return the pytest output. Takes no arguments. This is the only way to run the tests.",
        "parameters": {"type": "object", "properties": {}},
    },
}


class TripwireModel(LitellmModel):
    def _query(self, messages, **kwargs):
        return litellm.completion(model=self.config.model_name, messages=messages,
                                  tools=[BASH_TOOL, RUN_TESTS_TOOL], **(self.config.model_kwargs | kwargs))

    def _parse_actions(self, response):
        calls = response.choices[0].message.tool_calls or []
        rt = [c for c in calls if c.function.name == "run_tests"]
        others = [c for c in calls if c.function.name != "run_tests"]
        actions = []
        if others or not rt:
            actions = parse_toolcall_actions(others if others else calls, format_error_template=self.config.format_error_template,
                                             template_kwargs={"finish_reason": response.choices[0].finish_reason})
        for c in rt:
            actions.append({"command": "run_tests", "tool": "run_tests", "tool_call_id": c.id})
        # keep the model's original order
        order = {c.id: i for i, c in enumerate(calls)}
        return sorted(actions, key=lambda a: order.get(a.get("tool_call_id"), 0))
