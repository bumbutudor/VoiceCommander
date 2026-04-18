#!/usr/bin/env python3
"""voicecommander/windows - controleaza calculatorul cu vocea"""

from core.runner import Runner
from windows import config
from windows.commands import execute


def main():
    runner = Runner(
        name="windows",
        trigger=config.TRIGGER,
        trigger_variants=config.TRIGGER_VARIANTS,
        predicates=config.PREDICATES,
        context_info=config.context_info(),
        execute_fn=execute,
        help_text=config.HELP,
    )
    runner.run()


if __name__ == "__main__":
    main()
