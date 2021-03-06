# Managing Data with the iobeam Python Library

## Overview

This document is to be used as a guide for how to manage your data with
the iobeam Python library. There are currently two supported ways to
manage your data: (1) using `DataStore` (preferred) and (2) using `DataPoint`s
and `DataSeries`s (legacy). This guide covers both, but we urge you to use
`DataStore` whenever possible.

## Using `DataStore` (**preferred**)

The `iobeam.DataStore` data type (located in `iobeam/resources/data.py`) stores
data in a table format, where the columns name an individual data stream/series
(e.g. `temperature`, `humidity`, etc) and rows contain a timestamp and values for
streams that happen at that particular time. This allows you to group related streams
that share the same collection cycle into one data structure.

A `DataStore` is initialized by providing a list of column/field names that
the store should expect. For example, if you are collecting accelerometer
data, you could create a `DataStore` with fields `x-axis`, `y-axis`, and
`z-axis` to track the three components of acceleration:
```python
    store = iobeam.createDataStore(["x-axis", "y-axis", "z-axis"])
```

Then, to add data, you simply provide a timestamp and a dictionary of values
keyed by which column the value belongs to:
```python
nowMsec = int(time.time() * 1000)
timestamp = iobeam.Timestamp(nowMsec)
values = {
    "x-axis": getXAccel(),
    "y-axis": getYAccel(),
    "z-axis": getZAccel()
}
store.add(timestamp, values)
```

`DataStore` verifies that only keys it knows about are included in your data
values and creates a row with the following representation:

    {"time": ..., "x-axis": ..., "y-axis": ..., "z-axis"}

It is only an error to include keys _not_ in the original column name list;
you _can_ exclude columns and they will be assumed to be `None`/null. For
example, if you are collecting temperature and humidity data, but get
temperature twice as often as humidity, you can do the following:
```python
store = iobeam.createDataStore(["temperature", "humidity"])
# first time you have both:
t1 = ...
temp1 = getTemperature()
humid1 = getHumidity()
values = {"temperature": temp1, "humidity": humid1}
store.add(t1, values)
...
# next time you only have temperature:
t2 = ...
temp2 = getTemperature()
values = {"temperature": temp2}
store.add(t2, values)
```

The representation of these two adds will be:

    [
        {"time": t1, "temperature": temp1, "humidity": humid1},
        {"time": t2, "temperature": temp2, "humidity": None}
    ]

To have the data sent to iobeam, you need to add the `DataStore` to your
iobeam client:
```python
builder = iobeam.ClientBuilder(PROJECT_ID, PROJECT_TOKEN) \
            .saveToDisk().registerDevice()
iobeamClient = builder.build()
store = iobeam.createDataStore(["x-axis", "y-axis", "z-axis"])

# code adding data points, etc...

iobeamClient.send()
```

## Using `DataPoint` and `DataSeries` (**legacy**)
_Note: This way should be considered legacy and users should use the previous
method whenever possible. This could be removed in future releases._

Prior to v0.8.0, adding data consisted of creating a `DataPoint` for each
measurement and adding it to a specific series using `addDataPoint()` on a
iobeam client object. Similarly, you could add a named group of points using
a `DataSeries` object and `addDataSeries()`. This method could be a bit
onerous, however, when you had multiple data streams that were always added
together, e.g. an accelerometer. Using `DataPoint`s it looked like this:
```python
nowMsec = int(time.time() * 1000)
timestamp = iobeam.Timestamp(nowMsec)
dpX = iobeam.DataPoint(getXAccel(), timestamp=timestamp)
dpY = iobeam.DataPoint(getYAccel(), timestamp=timestamp)
dpZ = iobeam.DataPoint(getZAccel(), timestamp=timestamp)
iobeam.addDataPoint("x-axis", dpX)
iobeam.addDataPoint("y-axis", dpY)
iobeam.addDataPoint("z-axis", dpZ)
```

Alternatively you could create a `DataSeries` which consists of a name and a
list of `DataPoint`s.

### Converting to a `DataStore`

Converting to a `DataStore` from this legacy method is fairly straight
forward. The simplest way is just to create a separate store for each stream
and add the values. For example, these calls:
```python
dp1 = iobeam.DataPoint(1, timestamp=0)
dp2 = iobeam.DataPoint(2, timestamp=10)
dp3 = iobeam.DataPoint(3, timestamp=20)
iobeam.addDataPoint("series1", dp1)
iobeam.addDataPoint("series1", dp2)
iobeam.addDataPoint("series1", dp3)
```

becomes:
```python
store = iobeam.createDataStore(["series1"])
store.add(0, {"series1": 1})
store.add(10, {"series1": 2})
store.add(20, {"series1": 3})
```

However, you may find that some streams go together, like the accelerometer
example. Converting between the two is rather straightforward using the
example above.
