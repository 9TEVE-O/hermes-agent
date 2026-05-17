"""Abel CLI — ask the Ableton Live audio quality copilot a question."""
import sys


def main() -> None:
    from abel.config import load_config

    config = load_config()

    if len(sys.argv) < 2:
        print(f"Abel: Offline AI Copilot for Ableton Live  [mode: {config.mode}]\n")
        print("Usage: python -m abel.main <question>\n")
        print("Environment variables:")
        print("  ABEL_MODE=online|offline     (default: online)")
        print("  ABEL_LOCAL_MODEL=<model>     (default: llama3.1, offline only)")
        print("  ABEL_DATA_DIR=<path>         (default: ~/.abel)\n")
        print("Examples:")
        print('  python -m abel.main "What sample rate should I use for music production?"')
        print('  python -m abel.main "Analyse my session at ~/Music/Ableton/MySong.als"')
        print('  ABEL_MODE=offline python -m abel.main "How does sidechain compression work?"')
        sys.exit(0)

    from abel.audio_quality_agent import ask_abel_streaming

    question = " ".join(sys.argv[1:])
    label = "offline" if config.mode == "offline" else "online"
    print(f"\nAbel ({label}): ", end="", flush=True)
    ask_abel_streaming(question, config)


if __name__ == "__main__":
    main()
