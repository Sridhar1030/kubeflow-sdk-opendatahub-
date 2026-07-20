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

import json

from kubeflow.common.logging import configure_logging, get_logger


def test_get_logger_returns_named_logger():
    logger = get_logger("kubeflow.test.logging")
    assert logger is not None
    logger.info("structured_log_check", component="common")


def test_configure_logging_json_output(capsys, monkeypatch):
    monkeypatch.delenv("CI", raising=False)
    configure_logging(level="INFO", json_output=True)

    logger = get_logger("kubeflow.test.json")
    logger.info("json_event", job_name="demo")

    captured = capsys.readouterr()
    output = (captured.out + captured.err).strip().splitlines()
    assert output, "expected at least one log line"
    payload = json.loads(output[-1])
    assert payload["event"] == "json_event"
    assert payload["job_name"] == "demo"
    assert payload["level"] == "info"
