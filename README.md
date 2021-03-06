# iobeam Python Library

**[iobeam](https://iobeam.com)** is a data platform for connected devices.

This is a Python library for sending data to **iobeam**.
For more information on the iobeam, please [check our our documentation](https://docs.iobeam.com).

*Please note that we are currently invite-only. You will need an invite
to generate a valid token and use our APIs.
([Sign up here](https://iobeam.com) for an invite.)*


## Before you start

Before you can start sending data to the iobeam backend, you'll need a
`project_id` and  `project_token` (with write-access enabled) for a valid
**iobeam** account. You can get these easily with our
[command-line interface (CLI) tool](https://github.com/iobeam/iobeam) or by
accessing your project settings from [our web app](https://app.iobeam.com).

You need python **2.7.9+** or **3.4.3+** (earlier versions of python3 may
work, but it has not been tested).


## Installation

The easiest way to install is to use `pip`:

    pip install iobeam

#### Installing from source

You will need the `requests` and `pyjwt` libraries installed.
You can get it via pip:

    pip install requests pyjwt

If you are using Python2, or Python3 earlier than 3.5,
you will need the `enum34` library as well:

    pip install enum34

Then, to install from source:

    git clone https://github.com/iobeam/iobeam-client-python.git

Then make sure that the `iobeam` folder is in your `PYTHONPATH`.


## Overview

This library allows Python clients to send data to the
iobeam backend.

At a high-level, here's how it works:

1. Build an iobeam client object with your `project_id` and
`project_token`

1. Make sure your device is registered, either generating a `device_id` in
code or via another method (e.g., our CLI or REST APIs).

1. Create `iobeam.DataStore` objects for your data streams.
You can create one object per stream, or, if you have streams that are always
collected together (e.g. the axes of a gyroscope), you can put them in
one object.

1. Add data values to your `iobeam.DataStore` objects.

1. When you're ready, send your data to the iobeam backend


## Getting Started

Here's how to get started, using a basic example that sends temperature
data to iobeam. (For simplicity, let's assume that the current temperature
can be accessed with `getTemperature()`).

(Reminder: Before you start, create a user account, project, and
project_token (with write access) using the iobeam APIs, CLI or web app.
Write down your new `project_id` and `project_token`.)

### iobeam Initialization

There are several ways to initialize the iobeam client. All require
that you have `project_id` and `project_token` before hand.

**Without a registered `device_id`**

Perhaps the most natural way is to let the device register itself.
There are two ways to register a `device_id`:

(1) Let iobeam generate one for you:
```python
from iobeam import iobeam

...

builder = iobeam.ClientBuilder(PROJECT_ID, PROJECT_TOKEN) \
                .saveToDisk().registerDevice()
iobeamClient = builder.build()
```

(2) Provide your own (must be unique to your project):
```python
from iobeam import iobeam

...

builder = iobeam.ClientBuilder(PROJECT_ID, PROJECT_TOKEN) \
                .saveToDisk().registerDevice(deviceId="my_desired_id")
iobeamClient = builder.build()
```

With the `saveToDisk()` call, the `device_id` will be saved to disk in the
directory the script is called from (optionally, you can supply a `path`).
On future calls, this on-disk storage will be read first.
If a `device_id` exists, the `registerDevice` will do nothing; otherwise,
it will get a new random ID from us. If you provide a _different_ `device_id` to `registerDevice`, the old one will be replaced.

**With a registered `device_id`**

If you have registered a `device_id` (e.g. using our
[CLI](https://github.com/iobeam/iobeam)), you can pass this to the `Builder` instead
of registering:
```python
from iobeam import iobeam

...

builder = iobeam.ClientBuilder(PROJECT_ID, PROJECT_TOKEN) \
                .saveToDisk().setDeviceId(DEVICE_ID)
iobeamClient = builder.build()
```

You *must* have registered some other way (CLI, website, previous
installation, etc) for this to work.

**Advanced: not saving to disk**

If you don't want the `device_id` to be automatically stored for you, simply
exclude the `saveToDisk()` call while building:
```python
builder = iobeam.ClientBuilder(PROJECT_ID, PROJECT_TOKEN).registerDevice()
iobeamClient = builder.build()
```

This is useful for cases where you want to persist the ID yourself (e.g.
in a settings file), or if you are making `Iobeam` objects that are
temporary. For example, if the device you are using acts as a relay or
proxy for other devices, it could get the `device_id` from those devices
and have no need to save it.

### Tracking Time-series Data

For a more in-depth discussion about adding data, please see [our guide on
adding data](docs/DataGuide.md).

To track time-series data, you need to decide how to break down your data
streams into "stores", a collection of data streams grouped together. You
create a `iobeam.DataStore` with a list of stream names that it contains.
So if you're tracking just temperature in a store called `conditions`:
```python
conditions = iobeamClient.createDataStore(["temperature"])
```

Then for every data point, you'll want to add it to the store:
```python
now = ...  # e.g., now = int(time.time() * 1000) (import time first)
t = getTemperature()
conditions.add(iobeam.Timestamp(now), {"temperature": t})
```

The values are passed in via a dictionary, keyed by which data stream the
individual values belong to along with a timestamp.
_(For more on timestamps, see the next section.)_

The `iobeam.DataStore` object can hold several streams at once. For
example, if you also had a `getHumidity()` function, you could track both in
the same `DataStore`:
```python
conditions = iobeamClient.createDataStore(["temperature", "humidity"])

now = ... # current time
temp = getTemperature()
humidity = getHumidity()
conditions.add(iobeam.Timestamp(now), {"temperature": temp, "humidity": humidity})
```

Not every `add()` call needs all streams to have a value; if a stream is
omitted from the dictionary, it will be assumed to be `None`.

### Timestamps

By default, if you pass just an integer for timestamp when
constructing an `iobeam.DataPoint`, it will set the unit as
milliseconds. To specify other precisions, you need to use the
`iobeam.Timestamp` and `iobeam.TimeUnit` classes:
```python
# Timestamps in seconds:
now = int(time.time())
ts = iobeam.Timestamp(now, unit=iobeam.TimeUnit.SECONDS)
dp = iobeam.DataPoint(t, timestamp=ts)

# Another way to do milliseconds:
now = int(time.time() * 1000)
ts = iobeam.Timestamp(now, unit=iobeam.TimeUnit.MILLISECONDS)
dp = iobeam.DataPoint(t, timestamp=ts)

# Timestamps in microseconds:
now = int(time.time() * 1000000)
ts = iobeam.Timestamp(now, unit=iobeam.TimeUnit.MICROSECONDS)
dp = iobeam.DataPoint(t, timestamp=ts)
```

Currently we support expressing timestamps in seconds, milliseconds,
and microseconds.

### Connecting to the iobeam backend

You can send your data stored in `iobeam.Iobeam` to the iobeam backend
easily:
```python
iobeamClient.send()
```

This call is blocking and will attempt to send all your data. It will
return `True` if successful.


### Full Sending Example

Here's the full source code for our example:
```python
from iobeam import iobeam
import time

# Constants initialization
PROJECT_ID = ... # int
PROJECT_TOKEN = ... # String

...

# Init iobeam
builder = iobeam.ClientBuilder(PROJECT_ID, PROJECT_TOKEN) \
                .saveToDisk().registerDevice()
iobeamClient = builder.build()
conditions = iobeamClient.createDataStore(["temperature", "humidity"])

...

# Data gathering
now = ... # current time
ts = iobeam.Timestamp(now)

temp = getTemperature()
humidity = getHumidity()
conditions.add(ts, {"temperature": temp, "humidity": humidity})

...

# Data transmission
iobeamClient.send()
```


## Running tests

The tests use the Python `unittest` module, along with `mock`. If you are running a Python lower
than 3.3, you need to install `mock` from PyPI:

    pip install mock

(Versions >= 3.3 already have mock installed.)

You can invoke the tests with:

    python -m unittest discover

Or for more verbose output:

    python -m unittest discover -v
