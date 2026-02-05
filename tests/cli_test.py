"""Tests for the CLI module."""

import json
import os
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import TYPE_CHECKING
from unittest.mock import AsyncMock, patch

import pytest
from polyfactory.factories.msgspec_factory import MsgspecFactory
from typer.testing import CliRunner

from sghooker.cli import app
from sghooker.schemas.alert_event import AlertEventWebhookBody
from sghooker.schemas.issue_event import IssueCreatedWebhookBody, IssueUnresolvedWebhookBody

if TYPE_CHECKING:
    from pytest_httpserver import HTTPServer

runner = CliRunner()


class AlertEventWebhookBodyFactory(MsgspecFactory[AlertEventWebhookBody]):
    """Factory for generating AlertEventWebhookBody test data."""


class IssueCreatedWebhookBodyFactory(MsgspecFactory[IssueCreatedWebhookBody]):
    """Factory for generating IssueCreatedWebhookBody test data."""


class IssueUnresolvedWebhookBodyFactory(MsgspecFactory[IssueUnresolvedWebhookBody]):
    """Factory for generating IssueUnresolvedWebhookBody test data."""


@pytest.fixture
def mock_env_webhook_url():
    """Set up WEBHOOK_URL environment variable."""
    with patch.dict(os.environ, {"WEBHOOK_URL": "https://chat.googleapis.com/v1/spaces/test/webhook"}):
        yield


@pytest.fixture
def mock_send_message():
    """Mock the send_message function."""
    with patch("sghooker.cli.send_message", new_callable=AsyncMock) as mock:
        yield mock


def create_temp_json_file(data: dict) -> Path:
    """Create a temporary JSON file with the given data."""
    with NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(data, f)
        return Path(f.name)


class TestSendTestMessageCommand:
    """Tests for the send-test-message command."""

    def test_send_alert_event_success(
        self,
        mock_env_webhook_url: None,
        mock_send_message: AsyncMock,
    ) -> None:
        """Test sending an alert event message successfully."""
        # Arrange
        import msgspec

        event_data = AlertEventWebhookBodyFactory.build()
        json_data = json.loads(msgspec.json.encode(event_data))
        temp_file = create_temp_json_file(json_data)

        try:
            # Act
            result = runner.invoke(app, ["send-test-message", str(temp_file)])

            # Assert
            assert result.exit_code == 0
            assert "Loading JSON file" in result.output
            assert "Event type: alert_event" in result.output
            assert "Sending message to Google Chat" in result.output
            assert "Message sent successfully" in result.output
            mock_send_message.assert_called_once()
        finally:
            temp_file.unlink()

    def test_send_issue_created_success(
        self,
        mock_env_webhook_url: None,
        mock_send_message: AsyncMock,
    ) -> None:
        """Test sending an issue created message successfully."""
        # Arrange
        import msgspec

        event_data = IssueCreatedWebhookBodyFactory.build()
        json_data = json.loads(msgspec.json.encode(event_data))
        temp_file = create_temp_json_file(json_data)

        try:
            # Act
            result = runner.invoke(app, ["send-test-message", str(temp_file), "--event-type", "issue_created"])

            # Assert
            assert result.exit_code == 0
            assert "Event type: issue_created" in result.output
            assert "Message sent successfully" in result.output
            mock_send_message.assert_called_once()
        finally:
            temp_file.unlink()

    def test_send_issue_unresolved_success(
        self,
        mock_env_webhook_url: None,
        mock_send_message: AsyncMock,
    ) -> None:
        """Test sending an issue unresolved message successfully."""
        # Arrange
        import msgspec

        event_data = IssueUnresolvedWebhookBodyFactory.build()
        json_data = json.loads(msgspec.json.encode(event_data))
        temp_file = create_temp_json_file(json_data)

        try:
            # Act
            result = runner.invoke(app, ["send-test-message", str(temp_file), "--event-type", "issue_unresolved"])

            # Assert
            assert result.exit_code == 0
            assert "Event type: issue_unresolved" in result.output
            assert "Message sent successfully" in result.output
            mock_send_message.assert_called_once()
        finally:
            temp_file.unlink()

    def test_missing_webhook_url(
        self,
        mock_send_message: AsyncMock,
    ) -> None:
        """Test that missing WEBHOOK_URL environment variable fails."""
        # Arrange
        import msgspec

        event_data = AlertEventWebhookBodyFactory.build()
        json_data = json.loads(msgspec.json.encode(event_data))
        temp_file = create_temp_json_file(json_data)

        # Ensure WEBHOOK_URL is not set
        with patch.dict(os.environ, {}, clear=True):
            try:
                # Act
                result = runner.invoke(app, ["send-test-message", str(temp_file)])

                # Assert
                assert result.exit_code == 1
                assert "WEBHOOK_URL environment variable is required" in result.output
                mock_send_message.assert_not_called()
            finally:
                temp_file.unlink()

    def test_invalid_json_file(
        self,
        mock_env_webhook_url: None,
        mock_send_message: AsyncMock,
    ) -> None:
        """Test handling of invalid JSON file."""
        # Arrange
        with NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write("{invalid json}")
            temp_file = Path(f.name)

        try:
            # Act
            result = runner.invoke(app, ["send-test-message", str(temp_file)])

            # Assert
            assert result.exit_code == 1
            assert "Invalid JSON" in result.output
            mock_send_message.assert_not_called()
        finally:
            temp_file.unlink()

    def test_nonexistent_file(
        self,
        mock_env_webhook_url: None,
        mock_send_message: AsyncMock,
    ) -> None:
        """Test handling of non-existent file."""
        # Act
        result = runner.invoke(app, ["send-test-message", "/nonexistent/file.json"])

        # Assert
        assert result.exit_code == 2
        mock_send_message.assert_not_called()

    def test_explicit_event_type_override(
        self,
        mock_env_webhook_url: None,
        mock_send_message: AsyncMock,
    ) -> None:
        """Test that explicit event type override works."""
        # Arrange - create data that would auto-detect as alert_event
        import msgspec

        event_data = AlertEventWebhookBodyFactory.build()
        json_data = json.loads(msgspec.json.encode(event_data))
        temp_file = create_temp_json_file(json_data)

        try:
            # Act - explicitly specify issue_created (will fail validation)
            result = runner.invoke(app, ["send-test-message", str(temp_file), "--event-type", "issue_created"])

            # Assert - should fail because the data doesn't match issue_created schema
            assert result.exit_code == 1
            assert "JSON validation failed" in result.output
        finally:
            temp_file.unlink()


class TestValidateCommand:
    """Tests for the validate command."""

    def test_validate_alert_event_success(self) -> None:
        """Test validating an alert event payload successfully."""
        # Arrange
        import msgspec

        event_data = AlertEventWebhookBodyFactory.build()
        json_data = json.loads(msgspec.json.encode(event_data))
        temp_file = create_temp_json_file(json_data)

        try:
            # Act
            result = runner.invoke(app, ["validate", str(temp_file)])

            # Assert
            assert result.exit_code == 0
            assert "Validation successful" in result.output
        finally:
            temp_file.unlink()

    def test_validate_issue_created_success(self) -> None:
        """Test validating an issue created payload successfully."""
        # Arrange
        import msgspec

        event_data = IssueCreatedWebhookBodyFactory.build()
        json_data = json.loads(msgspec.json.encode(event_data))
        temp_file = create_temp_json_file(json_data)

        try:
            # Act
            result = runner.invoke(app, ["validate", str(temp_file), "--event-type", "issue_created"])

            # Assert
            assert result.exit_code == 0
            assert "Validation successful" in result.output
        finally:
            temp_file.unlink()

    def test_validate_invalid_json(self) -> None:
        """Test validating an invalid JSON payload."""
        # Arrange
        import msgspec

        # Create invalid data for alert_event schema
        json_data = {"invalid": "data", "structure": True}
        temp_file = create_temp_json_file(json_data)

        try:
            # Act
            result = runner.invoke(app, ["validate", str(temp_file)])

            # Assert
            assert result.exit_code == 1
            assert "JSON validation failed" in result.output
        finally:
            temp_file.unlink()


class TestEventTypeDetection:
    """Tests for event type auto-detection."""

    def test_detect_alert_event(self) -> None:
        """Test auto-detection of alert event type."""
        from sghooker.cli import _detect_event_type

        data = {"event": {"title": "Test Alert"}, "alert_rule": {"name": "Test Rule"}}

        result = _detect_event_type(data)

        assert result == "alert_event"

    def test_detect_issue_created(self) -> None:
        """Test auto-detection of issue created event type."""
        from sghooker.cli import _detect_event_type

        data = {"action": "created", "data": {"issue": {"id": "123"}}}

        result = _detect_event_type(data)

        assert result == "issue_created"

    def test_detect_issue_unresolved(self) -> None:
        """Test auto-detection of issue unresolved event type."""
        from sghooker.cli import _detect_event_type

        data = {"action": "unresolved", "data": {"issue": {"id": "123"}}}

        result = _detect_event_type(data)

        assert result == "issue_unresolved"

    def test_detect_unknown_defaults_to_alert(self) -> None:
        """Test that unknown event types default to alert_event."""
        from sghooker.cli import _detect_event_type

        data = {"some_random": "data"}

        result = _detect_event_type(data)

        assert result == "alert_event"


class TestConfigurationLoading:
    """Tests for configuration loading."""

    def test_load_env_config(self) -> None:
        """Test loading configuration from environment variables."""
        from sghooker.cli import _load_env_config

        with patch.dict(
            os.environ,
            {
                "WEBHOOK_URL": "https://test.webhook.url",
                "GRAFANA_URL_TEMPLATE": "https://grafana.test/{namespace}",
                "TRACING_URL_TEMPLATE": "https://tracing.test/{trace_id}",
            },
        ):
            config = _load_env_config()

            assert config["webhook_url"] == "https://test.webhook.url"
            assert config["grafana_url_template"] == "https://grafana.test/{namespace}"
            assert config["tracing_url_template"] == "https://tracing.test/{trace_id}"

    def test_load_env_config_with_missing_vars(self) -> None:
        """Test loading configuration with missing optional variables."""
        from sghooker.cli import _load_env_config

        with patch.dict(os.environ, {"WEBHOOK_URL": "https://test.webhook.url"}, clear=True):
            config = _load_env_config()

            assert config["webhook_url"] == "https://test.webhook.url"
            assert config["grafana_url_template"] is None
            assert config["tracing_url_template"] is None
