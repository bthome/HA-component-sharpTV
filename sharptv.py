"""
Support for interface with an Sharp TV.

For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/media_player.sharptv/
"""
import logging
import socket

from homeassistant.components.media_player import (
    DOMAIN, SUPPORT_NEXT_TRACK, SUPPORT_PREVIOUS_TRACK,
    SUPPORT_TURN_OFF, SUPPORT_VOLUME_MUTE, SUPPORT_VOLUME_STEP,
    SUPPORT_SELECT_SOURCE, MediaPlayerDevice)
from homeassistant.const import (
    CONF_HOST, CONF_NAME, STATE_OFF, STATE_ON, STATE_UNKNOWN)
from homeassistant.helpers import validate_config

CONF_PORT = "port"
CONF_USER = "user"
CONF_PASSWORD = "password"

_LOGGER = logging.getLogger(__name__)

REQUIREMENTS = ['sharp_aquos_rc==0.2']

SUPPORT_SHARPTV = SUPPORT_VOLUME_STEP | \
    SUPPORT_VOLUME_MUTE | SUPPORT_PREVIOUS_TRACK | \
    SUPPORT_NEXT_TRACK | SUPPORT_TURN_OFF | SUPPORT_SELECT_SOURCE


# pylint: disable=unused-argument
def setup_platform(hass, config, add_devices, discovery_info=None):
    """Setup the Sharp TV platform."""
    # Validate that all required config options are given
    if not validate_config({DOMAIN: config}, {DOMAIN: [CONF_HOST]}, _LOGGER):
        return False

    # Default the entity_name to 'Sharp TV Remote'
    name = config.get(CONF_NAME, 'Sharp TV Remote')

    # Generate a config for the Sharp lib
    remote_config = {
        "name": "HomeAssistant",
        "description": config.get(CONF_NAME, ''),
        "id": "ha.component.sharp",
        "host": config.get(CONF_HOST),
        "port": config.get(CONF_PORT, 10002),
        "user": config.get(CONF_USER, ""),
        "password": config.get(CONF_PASSWORD, "")
    }

    add_devices([SharpTVDevice(name, remote_config)])


# pylint: disable=abstract-method
class SharpTVDevice(MediaPlayerDevice):
    """Representation of a Sharp TV."""

    # pylint: disable=too-many-public-methods
    def __init__(self, name, config):
        """Initialize the sharp device."""
        from sharp_aquos_rc import TV
        # Save a reference to the imported class
        self._remote_class = TV
        self._name = name
        # Assume that the TV is not muted
        self._muted = False
        self._state = STATE_UNKNOWN
        self._remote = None
        self._current_source = None
        self._source_list = {'TV /Antenna': 0,
                             'HDMI_IN_1': 1,
                             'HDMI_IN_2': 2,
                             'HDMI_IN_3': 3,
                             'HDMI_IN_4': 4,
                             'COMPONENT IN': 5,
                             'VIDEO_IN_1': 6,
                             'VIDEO_IN_2': 7,
                             'PC_IN': 8};
        self._config = config

    def update(self):
        """Retrieve the latest data."""
        # Send an empty key to see if we are still connected
        return self.send_key('KEY_POWER')

    def get_remote(self):
        """Create or return a remote control instance."""
        if self._remote is None:
            # We need to create a new instance to reconnect.
            self._remote = self._remote_class(self._config["host"], self._config["port"], str(self._config["user"]), str(self._config["password"]))

        return self._remote

    def send_key(self, key):
        """Validates TV power status."""
        """FUTURE: Send all possible keys to the tv and handles exceptions."""
        try:
            p = self.get_remote().power()
            
            if (p == 1): self._state = STATE_ON 
            elif (p == 0): self._state = STATE_OFF
            else: _LOGGER.debug('Found Unknown State [%s]', p)
            
            if (self.get_remote().mute() == 1): self._muted = True 
            else: self._muted = False

            i = self.get_remote().input()
            for key in self._source_list:
               if self._source_list.get(key) == i:
                  self._current_source = key
            
            _LOGGER.debug('Found Current Source [%s] [%d]', self._current_source, i)

        except (socket.timeout, TimeoutError, OSError):
            _LOGGER.info('Exception: Timeout.  Current state [%s]', self._state) 
        except BaseException as e:
            _LOGGER.info('Exception: Unknown.  Current state [%s] Error [%s]', self._state, repr(e)) 

        return True

    @property
    def name(self):
        """Return the name of the device."""
        return self._name

    @property
    def state(self):
        """Return the state of the device."""
        return self._state

    @property
    def is_volume_muted(self):
        """Boolean if volume is currently muted."""
        return self._muted

    @property
    def source(self):
        """Return the current input source."""
        return self._current_source

    @property
    def source_list(self):
        """List of available input sources."""
        return sorted(list(self._source_list.keys()))

    @property
    def supported_media_commands(self):
        """Flag of media commands that are supported."""
        return SUPPORT_SHARPTV

    def turn_off(self):
        """Turn off media player."""
        self.get_remote().power_on_command_settings(2)
        self.get_remote().power(0) 
        self.send_key('KEY_POWER')

    def volume_up(self):
        """Volume up the media player."""
        self.get_remote().volume(self.get_remote().volume() + 1)

    def volume_down(self):
        """Volume down media player."""
        self.get_remote().volume(self.get_remote().volume() - 1)

    def mute_volume(self, mute):
        """Send mute command."""
        self.get_remote().mute(0)
        if (self.get_remote().mute() == 1): self._muted = True 
        else: self._muted = False

    def media_next_track(self):
        """Send next track command."""
        self.get_remote().channel_up()

    def media_previous_track(self):
        """Send the previous track command."""
        self.get_remote().channel_down()

    def turn_on(self):
        """Turn the media player on."""
        self.get_remote().power_on_command_settings(2)
        self.get_remote().power(1) 
        self.send_key('KEY_POWER')

    def select_source(self, source):
        """Select input source."""
        i = self._source_list.get(source)
        _LOGGER.info('Source Selection: New Source [%s] Input [%d]', source, i) 
        self.get_remote().input(i)
        self.send_key('KEY_SOURCE')

