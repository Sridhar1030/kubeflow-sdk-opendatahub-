# Copyright 2026 The Kubeflow Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Structured logging helpers for the Kubeflow SDK.

Uses structlog with stdlib integration so existing ``logging`` handlers still
work. Call :func:`configure_logging` once in application entrypoints when JSON
output is desired (auto-enabled when ``CI`` is set).
"""

from __future__ import annotations

import logging
import os

import structlog

_CONFIGURED = False


def configure_logging(level: str = "INFO", *, json_output: bool | None = None) -> None:
    """Configure structlog processors and stdlib logging.

    Args:
        level: Root log level name (DEBUG, INFO, WARNING, ERROR).
        json_output: If True, emit JSON lines; if False, human-readable console
            output. When None, JSON is used when the ``CI`` env var is set.
    """
    global _CONFIGURED
    if json_output is None:
        json_output = bool(os.environ.get("CI"))

    shared_processors: list[structlog.types.Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
    ]

    renderer: structlog.types.Processor = (
        structlog.processors.JSONRenderer() if json_output else structlog.dev.ConsoleRenderer()
    )

    structlog.configure(
        processors=[
            *shared_processors,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    formatter = structlog.stdlib.ProcessorFormatter(
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            renderer,
        ],
        foreign_pre_chain=shared_processors,
    )

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(getattr(logging, level.upper(), logging.INFO))
    _CONFIGURED = True


def get_logger(name: str | None = None) -> structlog.stdlib.BoundLogger:
    """Return a structlog logger for the given module name.

    Args:
        name: Logger name, typically ``__name__``.

    Returns:
        A structlog bound logger compatible with stdlib logging levels.
    """
    return structlog.get_logger(name)
