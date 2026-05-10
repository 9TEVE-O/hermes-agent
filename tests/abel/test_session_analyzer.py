"""Tests for Abel session analyzer and knowledge base."""
import pytest

from abel.knowledge_base import BIT_DEPTHS, SAMPLE_RATES, USE_CASE_RECOMMENDATIONS
from abel.session_analyzer import (
    analyze_session_settings,
    calculate_file_size,
    get_bit_depth_info,
    get_sample_rate_info,
    get_use_case_recommendation,
)


class TestKnowledgeBase:
    def test_sample_rates_have_required_keys(self):
        for rate, info in SAMPLE_RATES.items():
            assert "name" in info, f"{rate}: missing 'name'"
            assert "nyquist_frequency" in info, f"{rate}: missing 'nyquist_frequency'"
            assert "relative_cpu" in info, f"{rate}: missing 'relative_cpu'"
            assert "ableton_notes" in info, f"{rate}: missing 'ableton_notes'"

    def test_nyquist_is_half_sample_rate(self):
        for rate, info in SAMPLE_RATES.items():
            assert info["nyquist_frequency"] == rate // 2

    def test_bit_depths_have_dynamic_range(self):
        for depth, info in BIT_DEPTHS.items():
            assert "dynamic_range_db" in info, f"{depth}: missing 'dynamic_range_db'"


class TestSampleRateInfo:
    def test_known_rate_returns_data(self):
        result = get_sample_rate_info(44100)
        assert result["sample_rate"] == 44100
        assert "name" in result
        assert "ableton_notes" in result

    def test_unknown_rate_returns_error(self):
        result = get_sample_rate_info(12345)
        assert "error" in result
        assert "valid_sample_rates" in result


class TestBitDepthInfo:
    def test_24bit_is_ableton_default(self):
        result = get_bit_depth_info(24)
        assert result["ableton_default"] is True

    def test_16bit_lower_dynamic_range_than_24bit(self):
        r16 = get_bit_depth_info(16)
        r24 = get_bit_depth_info(24)
        assert r16["dynamic_range_db"] < r24["dynamic_range_db"]

    def test_32f_is_float(self):
        result = get_bit_depth_info("32f")
        assert result["is_float"] is True

    def test_unknown_bit_depth_returns_error(self):
        result = get_bit_depth_info(8)
        assert "error" in result
        assert "valid_bit_depths" in result


class TestFileSizeCalculation:
    def test_stereo_44100_24bit_approx_15mb_per_minute(self):
        result = calculate_file_size(60, 44100, 24, channels=2)
        assert abs(result["mb_per_minute"] - 15.09) < 0.1

    def test_higher_sample_rate_larger_file(self):
        r44 = calculate_file_size(60, 44100, 24)
        r96 = calculate_file_size(60, 96000, 24)
        assert r96["megabytes"] > r44["megabytes"]

    def test_unknown_bit_depth_returns_error(self):
        result = calculate_file_size(60, 44100, 8)
        assert "error" in result


class TestSessionAnalysis:
    def test_default_settings_parse_correctly(self):
        result = analyze_session_settings(44100, 24)
        assert result["sample_rate"] == 44100
        assert result["bit_depth"] == 24
        assert result["is_ableton_default"] is True
        assert "cpu_load_description" in result
        assert "estimated_storage_gb_per_hour_per_track" in result

    def test_unknown_settings_return_error(self):
        result = analyze_session_settings(12345, 24)
        assert "error" in result

    def test_96khz_higher_cpu_than_44100(self):
        r44 = analyze_session_settings(44100, 24)
        r96 = analyze_session_settings(96000, 24)
        assert r96["relative_cpu_load"] > r44["relative_cpu_load"]


class TestUseCaseRecommendations:
    def test_music_production_recommends_44100(self):
        result = get_use_case_recommendation("music_production")
        assert result["sample_rate"] == 44100

    def test_video_scoring_recommends_48000(self):
        result = get_use_case_recommendation("video_scoring")
        assert result["sample_rate"] == 48000

    def test_stems_export_recommends_32f(self):
        result = get_use_case_recommendation("stems_export")
        assert result["bit_depth"] == "32f"

    def test_unknown_use_case_returns_error(self):
        result = get_use_case_recommendation("djing")
        assert "error" in result
        assert "valid_use_cases" in result
