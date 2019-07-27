4 parts to the programe
Collect data (ht_sensor.py) -- collects a 10 second average and pushes that data to data.json in the {time: 'Humidity': h, 'Temperature': t}} format
Run main()

Three sub bots
1. Response bot -- looks for 'report' command on slack and replies with h and t. Run main()
2. Alert bot -- every 5 mins looks at the average and if outisde 70-80% range sends an alert Run main()
3. sheet bot -- at 1am upload the data to google sheets and re-set the data.json file
	the data to be pushed up is an hourly average of H and T along with a min and max for both. Run main()
