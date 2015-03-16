Release process:

- Change app.yaml version to higher version, upload
- Test:

All browsers (FF/IE/Chrome):
  * Submit an entry for a country that has states (AU)
  * Submit an entry for a country that doesn't have states (Italy, Milano, 20100)
  * Submit an entry for a country that doesn't have postcodes (Costa Rica)
  * Try to not specify a country (should fail)
  * Try to not specify a state for a country that has them (AU) (should fail)
  * Try to not specify a postcode for a country that has them (Italy) (should fail)

FF:
  * See if it works when you use geolocation in the browser (should fill in values)

- Set new version to default version in App Engine console if everything works