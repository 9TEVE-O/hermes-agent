"""Abel CLI — ask the Ableton Live audio quality copilot a question."""
import sys


def main() -> None:
    if len(sys.argv) < 2:
        print("Abel: Offline AI Copilot for Ableton Live\n")
        print("Usage: python -m abel.main <question>\n")
        print("Examples:")
        print('  python -m abel.main "What sample rate should I use for music production?"')
        print('  python -m abel.main "Compare 44.1 kHz vs 96 kHz for a 20-track session"')
        print('  python -m abel.main "How much disk space do 10 stems at 96 kHz need for a 4-min track?"')
        sys.exit(0)

    from abel.audio_quality_agent import ask_abel_streaming

    question = " ".join(sys.argv[1:])
    print(f"\nAbel: ", end="", flush=True)
    ask_abel_streaming(question)


if __name__ == "__main__":
    main()
