# iobeam Python Library

[iobeam](https://iobeam.com) is a data platform for connected devices.

This is a Python library for sending data to **iobeam**.
For more information on the iobeam, please [check our our documentation](https://docs.iobeam.com).

Please note that we are currently invite-only. You will need an invite
to generate a valid token and use our APIs.
([Sign up here](https://iobeam.com) for an invite.)


## Changelog

### 03/07/16 - v0.10.1
- Library checks that device ID is valid with regex `[a-zA-Z0-9:_-]+` instead of error
from server

### 02/01/16 - v0.10.0
- Error messages from the server are now included in stacktrace output
- Errors during refreshing tokens now raise an `UnknownCodeError`

### 01/28/16 - v0.9.7
- Rejects reserved column names, case-insensitive

### 01/27/16 - v0.9.6
- Add additional reserved column name: 'all'
- Fix error with when manually adding `DataStore` to a client (not recommended)

### 01/26/16 - v0.9.5
- Raise `ValueError` if `DataStore` contains reserved column names: time, time_offset

### 01/08/16 - v0.9.4
- Remove accidental dependency on pypandoc when installing from sources

### 12/22/15 - v0.9.2
- `registerOrSetId()` now accepts optional `deviceName` argument

### 12/18/15 - v0.9.1
- **IMPORTANT**: The client now correctly tracks batches it has seen before
so subsequent calls to `send()` do not send nothing.
- Documentation fixes

### 12/16/15 - v0.9.0
- Adding data should now be done via the new `iobeam.createDataStore(columns)` method,
which allows you to track multiple streams of data in one object.
- Internally, old methods involving `DataPoint`s and `DataSerie`s have been converted
to use `DataStore`s.
- Additional documentation provided [here](https://github.com/iobeam/iobeam-client-python/blob/master/docs/DataGuide.md).

### 12/02/15 - v0.8.0
- Automatic refresh of project tokens when they are expired. It is recommended that you
update as soon as possible to avoid breakage.
- bugfix: device ids are no longer allowed to be non-strings when registering

### 10/20/15 - v0.7.0
- **IMPORTANT**: previously sent data points were being kept and sent on subsequent sends, this
has been fixed
- Query assumes time values given in to/from are same unit as when it is initialized

### 10/13/15 - v0.6.0
- `Timestamp`: changed `type` param name to `unit` in constructor
- utils: Adds a check for whether this is python2 or 3
- New Error for duplicate ids
- New `registerOrSetId()` added to `iobeam.ClientBuilder` to allow you to register a name, or
if it already exists, set the client to use that id.

### 10/05/15 - v0.5.2
- Fix missing return for `iobeam.makeQuery()`

### 10/02/15 - v0.5.1

- Use persistent connections for HTTP to improve performance
- Rename `iobeam.MakeQuery()` to `iobeam.makeQuery()`
