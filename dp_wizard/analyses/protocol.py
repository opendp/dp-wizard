from typing import Protocol

from dp_wizard.utils.code_generators import CodeGenerator


class Analysis(Protocol):  # pragma: no cover
    # There should also be a "name".
    # @property can't be combined with @staticmethod,
    # so we can't make that explicit here.

    @staticmethod
    def has_bins() -> bool: ...

    @staticmethod
    def make_query(
        code_gen: CodeGenerator,
        identifier: str,
        accuracy_name: str,
        stats_name: str,
    ) -> str: ...

    @staticmethod
    def make_output(
        code_gen: CodeGenerator,
        column_name: str,
        accuracy_name: str,
        stats_name: str,
    ) -> str: ...

    @staticmethod
    def make_report_kv(
        name: str,
        confidence: float,
        identifier: str,
    ) -> str: ...

    @staticmethod
    def make_column_config_block(
        column_name: str,
        lower_bound: float,
        upper_bound: float,
        bin_count: int,
    ) -> str: ...
