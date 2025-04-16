# F1 Sensor for Home Assistant
![GitHub release (latest)](https://img.shields.io/github/v/release/Nicxe/f1_sensor)
![HACS Custom](https://img.shields.io/badge/HACS-Custom-blue)
<img alt="Maintenance" src="https://img.shields.io/maintenance/yes/2025">
<img alt="GitHub last commit" src="https://img.shields.io/github/last-commit/Nicxe/esphome"><br><br>

## What is F1 Sensor?
This is a custom integration for Home Assistant that creates sensors using data from the [Jolpica-F1 API](https://github.com/jolpica/jolpica-f1). It is designed for users who want to build automations, scripts, notifications, TTS messages, or more advanced use cases such as generating dynamic dashboards, triggering race-day routines, syncing events to calendars, or integrating with external services based on upcoming Formula 1 events.


> [!TIP]
> If your goal is to visually display upcoming race information, current standings, > and more in your Home Assistant dashboard, the [FormulaOne Card](https://github.com/marcokreeft87/formulaone-card) by @marcokreeft87 is the better choice for that purpose.



This integration **does not provide any UI components**. Instead, it creates:
- `sensor.f1_next_race` — Attributes include detailed information about the next race, such as when and where it takes place.
- `sensor.f1_season_calendar` — A list of all races in the current F1 season.
- `sensor.f1_driver_standings` — Current driver championship standings.
- `sensor.f1_constructor_standings` — Current constructor championship standings.

The integration fetches fresh data from the Jolpica-F1 API every 6 hours.

I personally use this integration to display the next race and the following three races on an e-ink display. You can read more about that setup [here](https://github.com/Nicxe/esphome).




## Installation

You can install this integration as a custom repository by following one of these guides:

### With HACS (Recommended)

To install the custom component using HACS:

1. Click on the three dots in the top right corner of the HACS overview menu.
2. Select **Custom repositories**.
3. Add the repository URL: `https://github.com/Nicxe/f1_sensor`.
4. Select type: **Integration**.
5. Click the **ADD** button.

<details>
<summary>Without HACS</summary>

1. Download the latest release of the F1 Sensor integration from **[GitHub Releases](https://github.com/Nicxe/f1_sensor/releases)**.
2. Extract the downloaded files and place the `f1_sensor` folder in your Home Assistant `custom_components` directory (usually located in the `config/custom_components` directory).
3. Restart your Home Assistant instance to load the new integration.

</details>


## Configuration

To add the integration to your Home Assistant instance, use the button below:

<p>
    <a href="https://my.home-assistant.io/redirect/config_flow_start?domain=f1_sensor" class="my badge" target="_blank">
        <img src="https://my.home-assistant.io/badges/config_flow_start.svg">
    </a>
</p>



### Manual Configuration

If the button above does not work, you can also perform the following steps manually:

1. Browse to your Home Assistant instance.
2. Go to **Settings > Devices & Services**.
3. In the bottom right corner, select the **Add Integration** button.
4. From the list, select **F1 Sensor**.
5. Follow the on-screen instructions to complete the setup.


<BR>

## Available Sensors

This integration provides the following sensors:

- `sensor.f1_next_race`: Details about the upcoming race.
- `sensor.f1_season_calendar`: The full season calendar.
- `sensor.f1_driver_standings`: Current driver championship standings.
- `sensor.f1_constructor_standings`: Current constructor championship standings.
- 
## Sensor Attributes Reference

This integration provides several sensors with rich attribute data. Below is a reference guide for what attributes are available in each sensor, including examples of how to access them in templates.

---

### `sensor.f1_next_race`

| Attribute               | Description                           | Example                                |
|------------------------|---------------------------------------|----------------------------------------|
| `season`               | Season year                           | `2025`                                 |
| `round`                | Round number                          | `5`                                    |
| `race_name`            | Name of the race                      | `Saudi Arabian Grand Prix`             |
| `race_url`             | Wikipedia URL of the race             | `https://en.wikipedia.org/...`         |
| `circuit_id`           | Internal ID of the circuit            | `jeddah`                               |
| `circuit_name`         | Full circuit name                     | `Jeddah Corniche Circuit`              |
| `circuit_url`          | Wikipedia URL of the circuit          | `https://en.wikipedia.org/...`         |
| `circuit_lat`          | Latitude of the circuit               | `21.6319`                              |
| `circuit_long`         | Longitude of the circuit              | `39.1044`                              |
| `circuit_locality`     | City                                  | `Jeddah`                               |
| `circuit_country`      | Country                               | `Saudi Arabia`                         |
| `race_start`           | Start datetime (ISO 8601)             | `2025-04-20T17:00:00+00:00`            |
| `first_practice_start` | First practice start time             | `2025-04-18T13:30:00+00:00`            |
| `second_practice_start`| Second practice start time            | `2025-04-18T17:00:00+00:00`            |
| `third_practice_start` | Third practice start time             | `2025-04-19T13:30:00+00:00`            |
| `qualifying_start`     | Qualifying session start              | `2025-04-19T17:00:00+00:00`            |
| `sprint_qualifying_start` | Sprint qualifying start (nullable) | `null`                                 |
| `sprint_start`         | Sprint session start (nullable)       | `null`                                 |

---

### `sensor.f1_driver_standings`

| Attribute           | Description                                    |
|--------------------|------------------------------------------------|
| `season`           | Season year                                    |
| `round`            | Round number                                   |
| `driver_standings` | List of driver entries (see below for schema)  |

Each item in `driver_standings` contains:

| Key                  | Sub-key        | Example                       |
|----------------------|----------------|-------------------------------|
| `position`           |                | `'1'`                         |
| `points`             |                | `'77'`                        |
| `wins`               |                | `'1'`                         |
| `Driver.driverId`    |                | `norris`                      |
| `Driver.givenName`   |                | `Lando`                       |
| `Driver.familyName`  |                | `Norris`                      |
| `Driver.code`        |                | `NOR`                         |
| `Driver.url`         |                | Wikipedia URL                 |
| `Constructors[n]`    | `.name`        | `McLaren`                     |
|                      | `.nationality` | `British`                     |

**Example template usage:**
```jinja
{{ state_attr('sensor.f1_driver_standings', 'driver_standings')[0].Driver.familyName }}
```

---

### `sensor.f1_constructor_standings`

This sensor provides the current constructor standings for the season.

#### Top-level attributes

| Attribute                | Description                        | Example   |
|-------------------------|------------------------------------|-----------|
| `season`                | The current F1 season              | `2025`    |
| `round`                 | Current round number               | `4`       |
| `constructor_standings`| List of constructor standings      | *(list)*  |

#### Structure of each item in `constructor_standings`

Each constructor entry contains:

| Attribute                      | Description                          | Example            |
|-------------------------------|--------------------------------------|--------------------|
| `position`                    | Current position in championship     | `'1'`              |
| `positionText`                | Same as `position` (string)          | `'1'`              |
| `points`                      | Total points earned                  | `'151'`            |
| `wins`                        | Total number of wins                 | `'3'`              |
| `Constructor.constructorId`   | Unique ID for constructor            | `mclaren`          |
| `Constructor.name`            | Constructor/team name                | `McLaren`          |
| `Constructor.nationality`     | Team nationality                     | `British`          |
| `Constructor.url`             | Wikipedia URL                        | `https://...`      |

#### Example usage in template:

```jinja
{% set constructors = state_attr('sensor.f1_constructor_standings', 'constructor_standings') %}
Top team is {{ constructors[0].Constructor.name }} with {{ constructors[0].points }} points.
```


### `sensor.f1_current_season`

This sensor contains the full race calendar for the current Formula 1 season.

#### Top-level attributes

| Attribute | Description       | Example |
|----------|-------------------|---------|
| `season` | The season year   | `2025`  |
| `races`  | List of races     | *(list)*|



#### Structure of each item in `races`

Each entry in the `races` array includes detailed information about a race weekend:

| Attribute                      | Description                         | Example                                  |
|-------------------------------|-------------------------------------|------------------------------------------|
| `season`                      | Year of the race                    | `'2025'`                                 |
| `round`                       | Round number                        | `'1'`                                    |
| `raceName`                    | Name of the race                    | `Australian Grand Prix`                  |
| `url`                         | Wikipedia URL of the race           | `https://en.wikipedia.org/...`           |
| `Circuit.circuitId`           | Circuit ID                          | `albert_park`                            |
| `Circuit.circuitName`         | Full name of circuit                | `Albert Park Grand Prix Circuit`         |
| `Circuit.url`                 | Wikipedia URL of circuit            | `https://en.wikipedia.org/...`           |
| `Circuit.Location.lat`        | Latitude of the circuit             | `-37.8497`                                |
| `Circuit.Location.long`       | Longitude of the circuit            | `144.968`                                 |
| `Circuit.Location.locality`   | City                                | `Melbourne`                               |
| `Circuit.Location.country`    | Country                             | `Australia`                               |
| `date`                        | Race date                           | `2025-03-16`                              |
| `time`                        | Race start time (UTC)               | `04:00:00Z`                               |
| `FirstPractice.date`          | First practice session date         | `2025-03-14`                              |
| `FirstPractice.time`          | First practice session time (UTC)   | `01:30:00Z`                               |
| `SecondPractice.date`         | Second practice session date        | `2025-03-14`                              |
| `SecondPractice.time`         | Second practice session time (UTC)  | `05:00:00Z`                               |
| `ThirdPractice.date`          | Third practice session date         | `2025-03-15`                              |
| `ThirdPractice.time`          | Third practice session time (UTC)   | `01:30:00Z`                               |
| `Qualifying.date`             | Qualifying session date             | `2025-03-15`                              |
| `Qualifying.time`             | Qualifying session time (UTC)       | `05:00:00Z`                               |


#### Example usage in template

Get info about the first race in the calendar:

```jinja
{% set races = state_attr('sensor.f1_current_season', 'races') %}
Next race: {{ races[0].raceName }} at {{ races[0].Circuit.circuitName }} in {{ races[0].Circuit.Location.locality }}
```
## Example

### Example Screenshots

This [e-ink display project](https://github.com/Nicxe/esphome) uses the sensors from this integration to show upcoming Formula 1 races, including race countdown and schedule.

<img src="https://github.com/user-attachments/assets/96185a06-ed0b-421a-afa6-884864baca63" width="500">

---

### Example: Announce next race and top standings via TTS

You can use this integration to generate a TTS message that announces how many days remain until the next race, along with the top 3 drivers and constructors.

#### Example automation / script using `tts.google_translate_say`

```yaml
service: tts.google_translate_say
data:
  entity_id: media_player.living_room_speaker
  message: >
    {% set next_race = state_attr('sensor.f1_next_race', 'race_name') %}
    {% set race_date = as_datetime(state_attr('sensor.f1_next_race', 'race_start')) %}
    {% set race_location = state_attr('sensor.f1_next_race', 'circuit_locality') %}
    {% set race_country = state_attr('sensor.f1_next_race', 'circuit_country') %}
    {% set days_left = (race_date.date() - now().date()).days %}
    {% set drivers = state_attr('sensor.f1_driver_standings', 'driver_standings') %}
    {% set constructors = state_attr('sensor.f1_constructor_standings', 'constructor_standings') %}

    The next Formula 1 race is the {{ next_race }} in {{ race_location }}, {{ race_country }}, happening in {{ days_left }} day{{ 's' if days_left != 1 else '' }}.

    The top 3 drivers right now are:
    Number 1: {{ drivers[0].Driver.givenName }} {{ drivers[0].Driver.familyName }} with {{ drivers[0].points }} points.
    Number 2: {{ drivers[1].Driver.givenName }} {{ drivers[1].Driver.familyName }} with {{ drivers[1].points }} points.
    Number 3: {{ drivers[2].Driver.givenName }} {{ drivers[2].Driver.familyName }} with {{ drivers[2].points }} points.

    In the constructor standings:
    Number 1: {{ constructors[0].Constructor.name }} with {{ constructors[0].points }} points.
    Number 2: {{ constructors[1].Constructor.name }} with {{ constructors[1].points }} points.
    Number 3: {{ constructors[2].Constructor.name }} with {{ constructors[2].points }} points.
```

---

### Example: Mobile notification with race info and standings

You can also send the same data as a mobile notification using notify.mobile_app_*:

#### Example using `notify.mobile_app_yourdevice`

```yaml
service: notify.mobile_app_yourdevice
data:
  title: "🏁 Formula 1 Update"
  message: >
    {% set race = state_attr('sensor.f1_next_race', 'race_name') %}
    {% set city = state_attr('sensor.f1_next_race', 'circuit_locality') %}
    {% set country = state_attr('sensor.f1_next_race', 'circuit_country') %}
    {% set race_time = as_datetime(state_attr('sensor.f1_next_race', 'race_start')) %}
    {% set days = (race_time.date() - now().date()).days %}
    {% set drivers = state_attr('sensor.f1_driver_standings', 'driver_standings') %}
    {% set constructors = state_attr('sensor.f1_constructor_standings', 'constructor_standings') %}
    Next race: {{ race }} in {{ city }}, {{ country }} — in {{ days }} day{{ 's' if days != 1 else '' }}.

    Top drivers:
    1. {{ drivers[0].Driver.familyName }} ({{ drivers[0].points }} pts)
    2. {{ drivers[1].Driver.familyName }} ({{ drivers[1].points }} pts)
    3. {{ drivers[2].Driver.familyName }} ({{ drivers[2].points }} pts)

    Top constructors:
    1. {{ constructors[0].Constructor.name }} ({{ constructors[0].points }} pts)
    2. {{ constructors[1].Constructor.name }} ({{ constructors[1].points }} pts)
    3. {{ constructors[2].Constructor.name }} ({{ constructors[2].points }} pts)
```
---

<br>

> [!NOTE] 
>### Support the API that makes this possible
>
>This integration relies entirely on the amazing [Jolpica-F1 API](https://github.com/jolpica/jolpica-f1), which provides high-quality and up-to-date Formula 1 data for free.
>
>If you find this integration useful, please consider supporting the creator of the API by donating to their Ko-fi page: https://ko-fi.com/jolpicaf1
>
>Without this API, this integration would not be possible, so any support helps keep it live and maintained. 🙏



### Contributing

Contributions, bug reports, and feedback are welcome. Please feel free to open issues or pull requests on GitHub.
