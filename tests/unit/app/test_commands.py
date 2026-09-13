from uuid import uuid4

import pytest

from arboria.app.commands import CommandValidationError, parse_envelope


def valid_envelope() -> dict[str, object]:
    return {
        "schema_version": 1,
        "command_id": str(uuid4()),
        "world_id": str(uuid4()),
        "timeline_id": str(uuid4()),
        "request_epoch": 1,
        "kind": "clock.pause",
        "payload": {},
    }


def test_parse_envelope_rejects_unknown_fields() -> None:
    envelope = valid_envelope()
    envelope["extra"] = True

    with pytest.raises(CommandValidationError, match="unknown envelope fields"):
        parse_envelope(envelope)


def test_parse_envelope_rejects_nonfinite_payload_numbers() -> None:
    envelope = valid_envelope()
    envelope["payload"] = {"speed": float("nan")}

    with pytest.raises(CommandValidationError, match="nan or infinite"):
        parse_envelope(envelope)


def test_parse_envelope_accepts_bounded_valid_payload() -> None:
    envelope = valid_envelope()
    envelope["kind"] = "clock.set_speed"
    envelope["payload"] = {"speed": 12.0}

    parsed = parse_envelope(envelope)

    assert parsed.kind == "clock.set_speed"
    assert parsed.payload == {"speed": 12.0}
