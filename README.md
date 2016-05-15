# HA-component-sharpTV
Home Assistant media player component for use with Sharp TV's. 

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisities

What things you need to install the software and how to install them

```
[Home Assistant](https://github.com/home-assistant/home-assistant)
```

### Installing

The component is implemented as a "custom_component" until it is natively integrated with Home Assistant

To install...

```
copy "sharpTV.py" to [PATH TO HOME ASSISTANT]/config/custom_components/media_player

```

## Running the component

To implement the component in HA you will need to modify your config.yaml

```
- platform: sharptv
  host: (IP ADDRESS to Sharp TV)
  name: sharpTV (optional)
  port: 10002 (default port to Sharp TV)
  user: (username implemented in Sharp TV settings)
  password: (password implemented in Sharp TV settings)
```

## Authors

* **B Thome** - *Initial work* - [bthome](https://github.com/bthome)


## License

MIT

## Acknowledgments

* jmoore987 - [jmoore987](https://github.com/jmoore987/sharp_aquos_rc).  Sharp integration made this possible.
* Based off existing component - [samsungtv](https://home-assistant.io/components/media_player.samsungtv/)

