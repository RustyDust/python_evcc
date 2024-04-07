# SonnenCharger

## Purpose

Read status information from [evcc's API](https://docs.evcc.io/docs/reference/api)

## Installation

### Using `pip`

``` bash
pip3 install evcc
```

### Manual installation
[Download the archive from pypi.org](https://pypi.org/project/evcc/#files) and unpack where needed ;)

## Usage

``` python
from evcc import evcc

evcc_host = '192.168.1.2'
evcc_port = 502  # optional, default=502

# Init class, establish connection
evcc_info = evcc(sc_host, sc_port)

print(evcc.get_state())	    # retrieve general wallbox information
```

## Results (examples)

