Take 5 minutes of readings every hour then post the average to the google sheets. 

Uses the Adafruit_DHT package to actually read the humidity and temperature. 


Project structure
humidor
    ht_sensor.py -> run with cron job every hour
Resources
    - sheet_id.txt - string for google sheets id
    - slack_id.txt - string for slack channel id
    - credentials.json - google sheets credentials

