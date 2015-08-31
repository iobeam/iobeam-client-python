# iobeam Python Library

**[iobeam](http://iobeam.com)** is a data platform for connected devices.

This is a Python library for sending data to the **iobeam Cloud**.
For more information on the iobeam Cloud, please read our [full API documentation](http://docs.iobeam.com).

*Please note that we are currently invite-only. You will need an invite
to generate a valid token and use our APIs. (Sign up [here](http://iobeam.com) for an invite.)*

## Before you start ##

Before you can start sending data to the iobeam Cloud, you'll need a
`project_id` and  `project_token` (with write-access enabled) for a valid
**iobeam** account. You can get these easily with our
[Command-line interface tool](https://github.com/iobeam/iobeam) or by
accessing your project settings from [our web app](https://app.iobeam.com).

You will need the [requests](http://www.python-requests.org/en/latest/) library
installed. You can get it via pip:

    pip install requests

Further, you need python **2.7.9+** or **3.4.3** (other versions of python3 may work,
but it has only been tested on 3.4.3).


## Installation ##

**[insert `pip` instructions]**

To install from source:

    git clone https://github.com/iobeam/iobeam-client-python.git

Then make sure that the `iobeam-client-python` folder is in your `PYTHONPATH`.


## Overview ##

This library allows Python clients to send data to the iobeam Cloud.

At a high-level, here's how it works:

1. Build an iobeam client object with your `project_id` and
`project_token`

1. Register your device to get an auto-generated `device_id`. Optionally,
you can initialize the object with a previously registered `device_id` in
the previous step and skip this step

1. Create a `iobeam.DataPoint` object for each time-series data point. Or,
for a collection of data points, create a `iobeam.DataSeries` object.

1. Add the `DataPoint` under your `series_name` (e.g., "temperature")

1. When you're ready, send your data to the iobeam Cloud


## Getting Started ##

Here's how to get started, using a basic example that sends temperature
data to iobeam. (For simplicity, let's assume that the current temperature
can be accessed with `getTemperature()`).

(Reminder: Before you start, create a user account, project, and
project_token (with write access) using the iobeam APIs, CLI or web app.
Write down your new `project_id` and `project_token`.)

### iobeam Initialization ###

There are several ways to initialize the `Iobeam` library. All require
that you have `project_id` and `project_token` before hand.

**Without a registered `device_id`**

Perhaps the most natural way is to let the device register itself.
There are two ways to register a `device_id`:

(1) Let iobeam generate one for you:

    from iobeam import iobeam

    ...

    builder = iobeam.ClientBuilder(PROJECT_ID, PROJECT_TOKEN) \
                  .saveToDisk().registerDevice()
    iobeamClient = builder.build()

(2) Provide your own (must be unique to your project):

    from iobeam import iobeam

    ...

    builder = iobeam.ClientBuilder(PROJECT_ID, PROJECT_TOKEN) \
                  .saveToDisk().registerDevice(deviceId="my_desired_id")
    iobeamClient = builder.build()

With the `saveToDisk()` call, the `device_id` will be saved to disk in the
directory the script is called from (optionally, you can supply a `path`).
On future calls, this on-disk storage will be read first.
If a `device_id` exists, the `registerDevice` will do nothing; otherwise,
it will get a new random ID from us. If you provide a _different_ `device_id` to `registerDevice`, the old one will be replaced.

**With a registered `device_id`**

If you have registered a `device_id` (e.g. using our
[CLI](https://github.com/iobeam/iobeam)), you can pass this in the
constructor and skip the registration step.

    from iobeam import iobeam

    ...

    builder = iobeam.ClientBuilder(PROJECT_ID, PROJECT_TOKEN) \
                  .saveToDisk().setDeviceId(DEVICE_ID)
    iobeamClient = builder.build()

You *must* have registered some other way (CLI, website, previous
installation, etc) for this to work.

**Advanced: not saving to disk**

If you don't want the `device_id` to be automatically stored for you, simply
exclude the `saveToDisk()` call while building:

    builder = iobeam.ClientBuilder(PROJECT_ID, PROJECT_TOKEN).registerDevice()
    iobeamClient = builder.build()

This is useful for cases where you want to persist the ID yourself (e.g.
in a settings file), or if you are making `Iobeam` objects that are
temporary. For example, if the device you are using acts as a relay or
proxy for other devices, it could get the `device_id` from those devices
and have no need to save it.

### Tracking Time-series Data ###

For each time-series data point, create a `iobeam.DataPoint` object:

    t = getTemperature()
    d = iobeam.DataPoint(t)

    # You can also pass a specific timestamp
    now = ... # e.g., now = int(time.time()*1000) (import time first)
    d = iobeam.DataPoint(t, timestamp=now)

(The timestamp provided should be in milliseconds since epoch. The value
can be integral or real.)

Now, pick a name for your data series (e.g., "temperature"), and add the
`iobeam.DataPoint` under that series:

    iobeamClient.addDataPoint("temperature", d)

Note that the `iobeam.Iobeam` object can hold several series at once. For
example, if you also had a `getHumidity()` function, you could add both
data points to the same `iobeam.Iobeam`:

    now = ... # current time
    dt = iobeam.DataPoint(getTemperature(), timestamp=now)
    dh = iobeam.DataPoint(getHumidity(), timestamp=now)

    iobeamClient.addDataPoint("temperature", dt)
    iobeamClient.addDataPoint("humidity", dh)


### Connecting to the iobeam Cloud ###

You can send your data stored in `iobeam.Iobeam` to the iobeam Cloud
easily:

    iobeamClient.send()

This call is blocking and will attempt to send all your data. It will
return `True` if successfull.


### Full Example ###

Here's the full source code for our example:

    from iobeam import iobeam
    import time

    # Constants initialization
    PATH = ... # Can be None if you don't want to persist device_id to disk
    PROJECT_ID = ... # int
    PROJECT_TOKEN = ... # String
    ...

    # Init iobeam
    builder = iobeam.ClientBuilder(PROJECT_ID, PROJECT_TOKEN) \
                  .saveToDisk().registerDevice()
    iobeamClient = builder.build()

    ...

    # Data gathering
    now = int(time.time()*1000)
    dt = iobeam.DataPoint(getTemperature(), timestamp=now)
    dh = iobeam.DataPoint(getHumidity(), timestamp=now)

    iobeamClient.addDataPoint("temperature", dt)
    iobeamClient.addDataPoint("humidity", dh)

    ...

    # Data transmission
    iobeamClient.send()


## Retrieving Data ##

Once you've sent data to the iobeam backend, you may want to query it and
process it. To do that, you'll need to create an `iobeam.QueryReq`, which is
composed of three parts: a project id, a device name (optional), and a series
name (optional). If a series name is not given, all series for that device are
retrieved. If a device name is not given, all devices will be queried.

In the simplest form, here is how you make a few different queries:

    # all series from all devices in project PROJECT_ID
    q = iobeam.QueryReq(PROJECT_ID)

    # all series from device DEVICE_ID in project PROJECT_ID
    q = iobeam.QueryReq(PROJECT_ID, deviceId=DEVICE_ID)

    # series "temp" from device DEVICE_ID in project PROJECT_ID
    q = iobeam.QueryReq(PROJECT_ID, deviceId=DEVICE_ID, seriesName="temp")

Then to actually execute the query:

    # token is a project token with read access
    res = iobeam.MakeQuery(token, q)

Your result will look something like this:

    { "result": [
        {
            "project_id": "<PROJECT_ID>",
            "device_id": "<DEVICE_ID>",
            "name": "temp",
            "data": [
                {
                    "time":  1427316488000,
                    "value": 22.23
                },
                {
                    "time":  1427316489000,
                    "value": 22.22
                }, ...
            ]
        }, ...
      ],
      "timefmt": "msec"
    }


### Adjusting Your Query ###

You can modify your with several parameters, such as `to` and `from` and limits
on the values you're interested in:

    # start with this basic query
    q = iobeam.QueryReq(PROJECT_ID, deviceId=DEVICE_ID, seriesName="temp")

    # Last 5 results after a given START_TIME:
    q = q.limit(5).fromTime(START_TIME)

    # All results between two times, START and END
    q = q.fromTime(START).toTime(END)

    # All results where the value is greater than 0
    q = q.greaterThan(0)

The full list of (chainable) parameters:

    limit(limit)
    fromTime(time)
    toTime(time)
    greaterThan(value)
    lessThan(value)
    equals(value)
