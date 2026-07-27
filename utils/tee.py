"""Capture notebook stdout to a file while still showing it in the cell."""

import sys
from pathlib import Path
from types import TracebackType


class Tee:
    """Duplicate everything written to stdout into a file.

    The agent reads `output.txt`; the user reads the plots. Without this the
    run log lives only in the notebook's cell outputs, where it cannot be
    grepped, diffed, or pasted into a task report.

    Prefer the context manager form - it restores stdout even when a cell
    raises, which the explicit start/stop pair does not.

    Attributes:
        path: File the duplicated output is written to.

    Example:
        >>> with Tee("output.txt"):  # doctest: +SKIP
        ...     print("goes to the cell and to the file")
    """

    def __init__(self, path: str | Path) -> None:
        """Initialize the tee.

        Args:
            path: Where to write the captured output. Overwritten, not
                appended: a run's log describes that run.
        """
        self.path = Path(path)
        self._original = sys.stdout
        self._file = None

    def start(self) -> None:
        """Redirect stdout through this object."""
        self._original = sys.stdout
        self._file = self.path.open("w", encoding="utf-8")
        sys.stdout = self

    def stop(self) -> None:
        """Restore the original stdout and close the file."""
        if self._file is not None:
            self._file.close()
            self._file = None
        sys.stdout = self._original

    def write(self, data: str) -> int:
        """Write to both the original stdout and the file.

        Args:
            data: Text to write.

        Returns:
            Number of characters written to the original stdout.
        """
        written = self._original.write(data)
        if self._file is not None:
            self._file.write(data)
            # Flushed per write so a killed kernel still leaves a usable log.
            self._file.flush()
        return written

    def flush(self) -> None:
        """Flush both destinations."""
        self._original.flush()
        if self._file is not None:
            self._file.flush()

    def __enter__(self) -> Tee:
        """Start capturing.

        Returns:
            This tee.
        """
        self.start()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        """Stop capturing, whether or not the block raised.

        Args:
            exc_type: Exception type, if the block raised.
            exc: Exception instance, if the block raised.
            tb: Traceback, if the block raised.
        """
        self.stop()
