

import urllib.request
import json


# print(url)



def get_current_temp(city, country):
    APIKEY = ''
    city = 'Boston'
    country_code = 'us'
    url = f'http://api.openweathermap.org/data/2.5/weather?q={city},{country_code}&APPID={APIKEY}'
    f = urllib.request.urlopen(url)
    response_text = f.read().decode('utf-8')
    response_data = json.loads(response_text)
    x = (response_data['main']['temp'])
    return('{:.2f}'.format(x - 273.15),city)

    """
    Returns current temperature in Celsius in your hometown
     from api.openweathermap.org

    Notice: the temperature returned from the API is in Kelvin.
    Below is the conversion formula form Kelvin to Celsius:
    T(°C) = T(°K) - 273.15
    """
print(get_current_temp('boston',"USA"))

