"""Pure-function tools for analyzing Ableton Live session audio quality settings."""
from typing import Any

from abel.knowledge_base import BIT_DEPTHS, SAMPLE_RATES, USE_CASE_RECOMMENDATIONS


def get_sample_rate_info(sample_rate: int) -> dict[str, Any]:
    info = SAMPLE_RATES.get(sample_rate)
    if info is None:
        return {
            "error": f"Unknown sample rate: {sample_rate} Hz",
            "valid_sample_rates": sorted(SAMPLE_RATES.keys()),
        }
    return {"sample_rate": sample_rate, **info}


def get_bit_depth_info(bit_depth: int | str) -> dict[str, Any]:
    info = BIT_DEPTHS.get(bit_depth)
    if info is None:
        return {
            "error": f"Unknown bit depth: {bit_depth}",
            "valid_bit_depths": list(BIT_DEPTHS.keys()),
        }
    return {"bit_depth": bit_depth, **info}


def calculate_file_size(
    duration_seconds: float,
    sample_rate: int,
    bit_depth: int | str,
    channels: int = 2,
) -> dict[str, Any]:
    depth_info = BIT_DEPTHS.get(bit_depth)
    if depth_info is None:
        return {"error": f"Unknown bit depth: {bit_depth}"}
    if sample_rate not in SAMPLE_RATES:
        return {"error": f"Unknown sample rate: {sample_rate}"}

    bits = depth_info["bits_per_sample"]
    bytes_per_second = (sample_rate * channels * bits) / 8
    total_bytes = bytes_per_second * duration_seconds
    return {
        "bytes": total_bytes,
        "kilobytes": total_bytes / 1024,
        "megabytes": total_bytes / (1024 ** 2),
        "gigabytes": total_bytes / (1024 ** 3),
        "mb_per_minute": (bytes_per_second * 60) / (1024 ** 2),
        "duration_seconds": duration_seconds,
        "sample_rate": sample_rate,
        "bit_depth": bit_depth,
        "channels": channels,
    }


def analyze_session_settings(
    sample_rate: int,
    bit_depth: int | str,
    track_count: int = 1,
    session_length_minutes: float = 4.0,
) -> dict[str, Any]:
    sr_info = SAMPLE_RATES.get(sample_rate)
    bd_info = BIT_DEPTHS.get(bit_depth)

    if sr_info is None:
        return {
            "error": f"Unknown sample rate: {sample_rate}",
            "valid_sample_rates": sorted(SAMPLE_RATES.keys()),
        }
    if bd_info is None:
        return {
            "error": f"Unknown bit depth: {bit_depth}",
            "valid_bit_depths": list(BIT_DEPTHS.keys()),
        }

    file_size = calculate_file_size(
        duration_seconds=session_length_minutes * 60,
        sample_rate=sample_rate,
        bit_depth=bit_depth,
    )
    total_storage_gb_per_hour = (file_size["mb_per_minute"] * 60) / 1024 * track_count

    relative_cpu = sr_info["relative_cpu"]
    if relative_cpu < 1.5:
        cpu_load = "low"
    elif relative_cpu < 2.5:
        cpu_load = "medium"
    else:
        cpu_load = "high"

    return {
        "sample_rate": sample_rate,
        "bit_depth": bit_depth,
        "sample_rate_name": sr_info["name"],
        "bit_depth_name": bd_info["name"],
        "nyquist_frequency": sr_info["nyquist_frequency"],
        "dynamic_range_db": bd_info["dynamic_range_db"],
        "is_ableton_default": sr_info["ableton_default"] and bd_info["ableton_default"],
        "relative_cpu_load": sr_info["relative_cpu"],
        "cpu_load_description": cpu_load,
        "estimated_storage_gb_per_hour_per_track": round(total_storage_gb_per_hour, 3),
        "track_count": track_count,
        "session_length_minutes": session_length_minutes,
        "ableton_notes": {
            "sample_rate": sr_info["ableton_notes"],
            "bit_depth": bd_info["ableton_notes"],
        },
    }


def get_use_case_recommendation(use_case: str) -> dict[str, Any]:
    rec = USE_CASE_RECOMMENDATIONS.get(use_case)
    if rec is None:
        return {
            "error": f"Unknown use case: {use_case}",
            "valid_use_cases": list(USE_CASE_RECOMMENDATIONS.keys()),
        }
    return {"use_case": use_case, **rec}
