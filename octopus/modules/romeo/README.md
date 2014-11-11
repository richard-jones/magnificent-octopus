# Sherpa RoMEO Integration

A basic client for interacting with the Sherpa RoMEO API.

At the moment this just supports download of the full list of Journals and ISSNS:

```python
    from octopus.modules.romeo import client
    c = client.RomeoClient()
    c.download("romeo.csv")
```

This will download the list of journals and save it to a file called "romeo.csv"