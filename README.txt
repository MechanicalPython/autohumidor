4 parts to the programe
Collect data (ht_sensor.py) -- collects a 10 second average and pushes that data to data.json in the {time: 'Humidity': h, 'Temperature': t}} format
Run main()

__init__ contails send_message method
sheet_bot pushes data to google sheets
ht_sensor reads and saves the HDT raw data
alert_bot gets past 24 hours of data and sends a message to slack for it

Project strucutre
autohumidor
    - alert_bot.py
    - ht_sensor.py
    - response_bot.py -- Depreciated
    - sheet_bot.py
Resources
    - data.pkl
    - sheet_id.txt - string for google sheets id
    - slack_id.txt - string for slack channel id
    - credentials.json - google sheets credentials
Test change
Test change 2
Test change 3



