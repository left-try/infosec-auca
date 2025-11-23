I promise to meet the deadline and will take disciplinary action if this requirement is not met.

## How to use

Fetch current weather (and save):

```
python weather_app.py current Bishkek
python weather_app.py current "New York" --units imperial
# or just:
python weather_app.py
# (will prompt for city, metric by default)
```

Show history:
```
python weather_app.py history
python weather_app.py history -n 5
```

History for one city:
```
python weather_app.py city-history Bishkek -n 3
```

List all cities:
```
python weather_app.py cities
```

Stats:
```
python weather_app.py stats          # per city
python weather_app.py stats -c Rome  # one city
```

Export to JSON:
```
python weather_app.py export all_weather.json
python weather_app.py export bishkek.json -c Bishkek -n 20
```

Clear history:
```
python weather_app.py clear          # asks for confirmation
python weather_app.py clear -c Rome  # only Rome entries
python weather_app.py clear -y       # nuke all without prompt
```