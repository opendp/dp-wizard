from dp_wizard.utils.code_generators.base_generators._stats_generator import (
    StatsGenerator,
)
from dp_wizard.utils.code_generators.base_generators._synth_generator import (
    SynthGenerator,
)


class AbstractGenerator(StatsGenerator, SynthGenerator):
    """
    Each class in this hierarchy has its own set of concerns:

    ```
        NotebookGenerator   ScriptGenerator
                │                 │
                └────────┬────────┘
                         │
                 AbstractGenerator
                         │
                ┌-───────┴────────┐
                │                 │
        StatsGenerator    SynthGenerator
                │                 │
                └────────┬────────┘
                         │
                   BaseGenerator
    ```
    """

    pass
