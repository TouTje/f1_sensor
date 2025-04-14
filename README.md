# F1 Sensor


### What is this integration?

This is a custom integration for Home Assistant that creates sensors using data from the [Jolpica-F1 API](https://github.com/jolpica/jolpica-f1). It is designed for users who want to build automations, scripts, notifications, TTS messages, or more advanced use cases such as generating dynamic dashboards, triggering race-day routines, syncing events to calendars, or integrating with external services based on upcoming Formula 1 events.


> [!TIP]
> If your goal is to *visually display* upcoming race information, current standings, and more in your Home Assistant dashboard, the [FormulaOne Card](https://github.com/marcokreeft87/formulaone-card) is the better choice for that purpose.


This integration **does not provide any UI components**. Instead, it creates:
- `sensor.f1_next_race` — Attributes include detailed information about the next race, such as when and where it takes place.
- `sensor.f1_season_calendar` — A list of all races in the current F1 season.

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


<a href="https://buymeacoffee.com/niklasv" target="_blank"><img src="https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png" alt="Buy Me A Coffee" style="height: auto !important;width: auto !important;" ></a>


## ☕ Support the API that makes this possible

This integration relies entirely on the amazing [Jolpica-F1 API](https://github.com/jolpica/jolpica-f1), which provides high-quality and up-to-date Formula 1 data for free.

If you find this integration useful, please consider supporting the creator of the API by donating to their Ko-fi page:

➡️ [https://ko-fi.com/jolpic](https://ko-fi.com/jolpic)

Without this API, this integration would not be possible, so any support helps keep it alive and maintained. 🙏


## Example Screenshots
[This display](https://github.com/Nicxe/esphome) uses the sensors from this integration to show upcoming Formula 1 races.

<img src="https://github.com/user-attachments/assets/96185a06-ed0b-421a-afa6-884864baca63" width="500">

## Contributing

Contributions, bug reports, and feedback are welcome. Please feel free to open issues or pull requests on GitHub.
