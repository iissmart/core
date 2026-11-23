"""Test Intellifire light."""

from unittest.mock import AsyncMock, patch

import pytest
from pytest_homeassistant.common import MockConfigEntry

from homeassistant.components.light import ATTR_BRIGHTNESS, DOMAIN as LIGHT_DOMAIN
from homeassistant.const import (
    ATTR_ENTITY_ID,
    SERVICE_TURN_OFF,
    SERVICE_TURN_ON,
    Platform,
)
from homeassistant.core import HomeAssistant

from . import setup_integration


@pytest.mark.usefixtures("entity_registry_enabled_by_default")
async def test_light_brightness(
    hass: HomeAssistant,
    mock_config_entry_current: MockConfigEntry,
    mock_fp,
) -> None:
    """Test changing the light brightness."""
    mock_fp.read_api.data.has_light = True
    mock_fp.read_api.data.light_level = 2
    mock_fp.control_api.set_lights = AsyncMock()

    with patch("homeassistant.components.intellifire.PLATFORMS", [Platform.LIGHT]):
        await setup_integration(hass, mock_config_entry_current)

    entity_id = "light.intellifire_lights"
    state = hass.states.get(entity_id)
    assert state is not None
    assert state.attributes[ATTR_BRIGHTNESS] == 170

    await hass.services.async_call(
        LIGHT_DOMAIN,
        SERVICE_TURN_ON,
        {ATTR_ENTITY_ID: entity_id, ATTR_BRIGHTNESS: 255},
        blocking=True,
    )
    mock_fp.control_api.set_lights.assert_awaited_once_with(level=3)

    mock_fp.control_api.set_lights.reset_mock()
    await hass.services.async_call(
        LIGHT_DOMAIN,
        SERVICE_TURN_OFF,
        {ATTR_ENTITY_ID: entity_id},
        blocking=True,
    )
    mock_fp.control_api.set_lights.assert_awaited_once_with(level=0)
