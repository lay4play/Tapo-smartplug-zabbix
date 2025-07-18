# Tapo SmartPlug Python Script for Zabbix
This Python script enables Zabbix to read data from TP-Link TAPO SmartPlugs.
**Note:** The script is designed to monitor only one SmartPlug at a time.

![zabbix_preview](picture0.png)

![zabbix_preview](picture1.png)

## Tested SmartPlug
- [x] Tapo P115
*(This is the only Tapo device I own, but the script should work with any TAPO SmartPlug featuring power monitoring.)*

## Usage
Configure these **environment variables**:
- `TAPO_USER`: Email address used for Tapo app login
- `TAPO_PASSWORD`: Password used for Tapo app login
- `PLUG_IP`: Local IPv4 address of the SmartPlug
- `ZABBIX_SERVER`: Zabbix server IP/Domain for data submission
- `ZABBIX_HOSTNAME`: Hostname configured in Zabbix WebUI for the device
- `RUN_INTERVAL` (Optional): Default=300 (5 minutes). Interval (in seconds) between data submissions.

## Dependencies
- [python-kasa](https://github.com/python-kasa/python-kasa)
- [zabbix_sender](https://www.zabbix.com/download)


## Data Sent to Zabbix
- [x] Device state
- [x] Current power consumption (Watts)
- [x] Current (Amps)
- [x] Voltage (Volts)
- [x] Today's energy consumption (kWh)
- [x] Current month's energy consumption (kWh)

## Docker Support
This project is available as a Docker image:

**📦 Image:** [`lay4play/tapo-smartplug-zabbix`](https://hub.docker.com/r/lay4play/tapo-smartplug-zabbix)

