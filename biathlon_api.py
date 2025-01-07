# Copyright (C) 2024 KML_Style
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# Author: KML_Style
# Description: Script for processing biathlon competition data.

import requests

def get_json(url):
    """
    Sends a GET request to the specified URL and returns the response content in JSON format.
    
    Args:
    url (str): The URL to which the GET request is sent.
    
    Returns:
    dict: The JSON content of the URL's response, converted to a Python dictionary.
    
    Raises:
    requests.exceptions.RequestException: If the request fails.
    ValueError: If the response content is not valid JSON.
    """
    try:
        answer = requests.get(url)
        answer.raise_for_status()  
        text = answer.json()
    except requests.exceptions.RequestException as e:
        raise requests.exceptions.RequestException(f"Request error: {e}")
    except ValueError:
        raise ValueError("The response is not valid JSON.")
    return text

def get_url_analytics(Race_Id, Type_Id):
    """
    Generates the URL to retrieve a type of analytical results of a race.
    
    Args:
    Race_Id (str): The identifier of the race.
    Type_Id (str): The identifier of the type of analysis to retrieve (ex: "STTM", "CRST").
    
    Returns:
    str: The URL of the request to access the analytical results of the race.
    """
    return "https://www.biathlonresults.com/modules/sportapi/api/AnalyticResults?RaceId=" + Race_Id + "&TypeId=" + Type_Id

def get_url_results(Race_Id):
    """
    Generates the URL to retrieve the results of a race.

    Args:
    Race_Id (str): The race ID.
    
    Returns:
    str: The URL of the request to access the results of the race.
    """
    return "https://www.biathlonresults.com/modules/sportapi/api/Results?RT=385698&RaceId=" + Race_Id

def get_url_calendar(season):
    """
    Generates the URL to get the event calendar of a season.

    Args:
    season (str): The season using a two-digit year span format (eg. 2425 for the season 2024-2025)
    
    Returns:
    str: The URL of the request to access the calendar of the season.
    """
    return "https://www.biathlonresults.com/modules/sportapi/api/Events?RT=385698&SeasonId=" + season + "&Level=-1"

def get_url_event(Event_Id):
    """
    Generates the URL to get the races during an event.

    Args:
    Event_Id (str): The event ID.
    
    Returns:
    str: The URL of the request to access the event's races.
    """
    return "https://www.biathlonresults.com/modules/sportapi/api/Competitions?RT=385698&EventId=" + Event_Id