from langchain_nimble import NimbleSearchTool
from langchain.tools import tool
from dotenv import load_dotenv
import requests
import os
from typing import List

load_dotenv()


search_tool = NimbleSearchTool(
    k= 5,
    deep_search= True,
    parsing_type="markdown"
)


@tool
def google_search_tool(query:str):
    """
    Search anything on google for real time information.
    Args:
        query - user search query for google search

    Return - result from google search 
    """
    res = search_tool.invoke(query)
    return res


@tool
def weather_tool(cities: List[str]):
    """
    Get real time weather details like temperature, humidity and others.
    Args:
        cities - A list of city names (e.g., ["Mumbai", "Delhi", "Lucknow"])
    Return -> A dictionary containing a brief summary of weather data for each city.
    """
    api_key = os.getenv('WEATHER_API_KEY')
    if not api_key:
        return "Error: WEATHER_API_KEY is missing from environment variables."

    results = {}
    
    for city in cities:
        clean_city = city.strip()
        # Added &units=metric to automatically get Celsius
        API_URL = f"https://api.openweathermap.org/data/2.5/weather?q={clean_city}&appid={api_key}&units=metric"
        
        try:
            res = requests.get(API_URL, timeout=5)
            
            if res.status_code == 200:
                data = res.json()
                
                # EXTRACT ONLY THE ESSENTIALS: This reduces a 100-line JSON down to 3 lines
                results[clean_city] = {
                    "temp_C": data['main']['temp'],
                    "condition": data['weather'][0]['description'],
                    "humidity_percent": data['main']['humidity']
                }
                
            elif res.status_code == 404:
                results[clean_city] = f"Error: City '{clean_city}' not found."
            else:
                results[clean_city] = f"Error: HTTP {res.status_code}."
                
        except requests.exceptions.RequestException as e:
            results[clean_city] = f"Error: Network failure - {str(e)}"
            
    return results


ALL_TOOLS = [google_search_tool, weather_tool]