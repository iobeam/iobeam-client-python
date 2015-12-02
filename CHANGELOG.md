# iobeam Python Library

[iobeam](https://iobeam.com) is a data platform for connected devices.

This is a Python library for sending data to **iobeam**.
For more information on the iobeam, please [check our our documentation](https://docs.iobeam.com).

Please note that we are currently invite-only. You will need an invite
to generate a valid token and use our APIs.
([Sign up here](https://iobeam.com) for an invite.)


## Changelog

### 12/02/15 - v0.8.0
- Automatic refresh of project tokens when they are expired. It is recommended that you
update as soon as possible to avoid breakage.
- bugfix: device ids are no longer allowed to be non-strings when registering

### 10/20/15 - v0.7.0
- *IMPORTANT*: previously sent data points were being kept and sent on subsequent sends, this
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
