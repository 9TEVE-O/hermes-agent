"""Abel audio quality agent — streams answers about Ableton Live session settings."""
import json
from typing import Any

import anthropic

from abel.session_analyzer import (
    analyze_session_settings,
    calculate_file_size,
    get_bit_depth_info,
    get_sample_rate_info,
    get_use_case_recommendation,
)

MODEL = "claude-opus-4-7"

SYSTEM_PROMPT = """You are Abel, an expert offline AI copilot for Ableton Live. \
You specialize in audio quality settings — sample rate, bit depth, file size, and session optimization.

Your knowledge is Ableton-specific:
- Reference Ableton Live menus, preferences, and keyboard shortcuts (e.g., Preferences → Audio, \
File → Export Audio/Video with Cmd+Shift+R on Mac / Ctrl+Shift+R on Windows).
- Ableton Live processes audio internally at 32-bit float regardless of the project bit depth setting.
- The Ableton Live defaults are 44.1 kHz sample rate and 24-bit depth.
- Never suggest third-party DAW workflows; keep all advice specific to Ableton Live.

When answering questions:
1. Use the provided tools to fetch accurate data before explaining.
2. Explain the WHY behind recommendations, not just the numbers.
3. Be concise and practical — producers need actionable guidance.
4. Always ground your answer in Ableton Live's specific behavior."""

TOOLS = [
    {
        "name": "get_sample_rate_info",
        "description": "Get detailed information about a specific sample rate including Ableton-specific notes, CPU load, and use cases.",
        "input_schema": {
            "type": "object",
            "properties": {
                "sample_rate": {
                    "type": "integer",
                    "description": "Sample rate in Hz (e.g. 44100, 48000, 96000)",
                }
            },
            "required": ["sample_rate"],
        },
    },
    {
        "name": "get_bit_depth_info",
        "description": "Get detailed information about a specific bit depth including dynamic range, Ableton behavior, and use cases.",
        "input_schema": {
            "type": "object",
            "properties": {
                "bit_depth": {
                    "oneOf": [
                        {"type": "integer", "description": "Integer bit depth (16 or 24)"},
                        {"type": "string", "description": "Float bit depth ('32f' or '64f')"},
                    ],
                    "description": "Bit depth: 16, 24, '32f', or '64f'",
                }
            },
            "required": ["bit_depth"],
        },
    },
    {
        "name": "analyze_session_settings",
        "description": "Analyze Ableton session settings and return quality metrics, CPU load, and storage estimates.",
        "input_schema": {
            "type": "object",
            "properties": {
                "sample_rate": {"type": "integer", "description": "Sample rate in Hz"},
                "bit_depth": {
                    "oneOf": [
                        {"type": "integer"},
                        {"type": "string"},
                    ],
                    "description": "Bit depth: 16, 24, '32f', or '64f'",
                },
                "track_count": {
                    "type": "integer",
                    "description": "Number of audio tracks in the session (default 1)",
                    "default": 1,
                },
                "session_length_minutes": {
                    "type": "number",
                    "description": "Approximate session length in minutes (default 4.0)",
                    "default": 4.0,
                },
            },
            "required": ["sample_rate", "bit_depth"],
        },
    },
    {
        "name": "calculate_file_size",
        "description": "Calculate the exact file size for an audio file given duration, sample rate, bit depth, and channel count.",
        "input_schema": {
            "type": "object",
            "properties": {
                "duration_seconds": {"type": "number", "description": "Duration in seconds"},
                "sample_rate": {"type": "integer", "description": "Sample rate in Hz"},
                "bit_depth": {
                    "oneOf": [
                        {"type": "integer"},
                        {"type": "string"},
                    ],
                    "description": "Bit depth: 16, 24, '32f', or '64f'",
                },
                "channels": {
                    "type": "integer",
                    "description": "Number of audio channels (default 2 for stereo)",
                    "default": 2,
                },
            },
            "required": ["duration_seconds", "sample_rate", "bit_depth"],
        },
    },
    {
        "name": "get_use_case_recommendation",
        "description": "Get the recommended Ableton Live sample rate and bit depth for a specific production use case.",
        "input_schema": {
            "type": "object",
            "properties": {
                "use_case": {
                    "type": "string",
                    "description": "Use case: 'music_production', 'video_scoring', 'stems_export', 'live_performance', 'podcast', or 'archival'",
                }
            },
            "required": ["use_case"],
        },
    },
]

TOOL_DISPATCH: dict[str, Any] = {
    "get_sample_rate_info": get_sample_rate_info,
    "get_bit_depth_info": get_bit_depth_info,
    "analyze_session_settings": analyze_session_settings,
    "calculate_file_size": calculate_file_size,
    "get_use_case_recommendation": get_use_case_recommendation,
}


def run_tool(name: str, tool_input: dict[str, Any]) -> str:
    fn = TOOL_DISPATCH.get(name)
    if fn is None:
        return json.dumps({"error": f"Unknown tool: {name}"})
    result = fn(**tool_input)
    return json.dumps(result, indent=2)


def ask_abel_streaming(question: str) -> None:
    """Stream Abel's response to stdout, handling tool use silently."""
    client = anthropic.Anthropic()
    messages: list[dict] = [{"role": "user", "content": question}]

    while True:
        with client.messages.stream(
            model=MODEL,
            max_tokens=4096,
            thinking={"type": "adaptive"},
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=messages,
        ) as stream:
            for event in stream:
                if event.type == "content_block_delta":
                    if event.delta.type == "text_delta":
                        print(event.delta.text, end="", flush=True)
            response = stream.get_final_message()

        tool_uses = [b for b in response.content if b.type == "tool_use"]
        if response.stop_reason == "end_turn" or not tool_uses:
            print()
            return

        messages.append({"role": "assistant", "content": response.content})
        tool_results = []
        for tu in tool_uses:
            result_content = run_tool(tu.name, tu.input)
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": tu.id,
                "content": result_content,
            })
        messages.append({"role": "user", "content": tool_results})
