# Reception Module's attached server

Here is implemented the functionality to read data from the TI CC1310 receiving module and write it to the database.

## Dependencies

The communication between the server and the CC1310 board is done over UART (serial communication). This project uses:

* PySerial v3.1.1


## Running

The following command runs this component:

```
python3 main.py --port <port that the device is attached to> --baud_rate <baud rate>
```