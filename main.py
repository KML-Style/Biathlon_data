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


## --- USED LIBRARIES --- ##
import requests
import os
import os.path as op
import pandas  as pd

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

def events_id(season, competition):
    """
    Retrieves a list of event IDs for a specific competition within a given season.

    Args:
        season (str): The season year for which to retrieve the event IDs.
        competition (list of str): The name or description of the competition to filter events by.

    Returns:
        list of int: A list of event IDs corresponding to the specified competition within the season.

    Raises:
        ValueError: If the season isn't in the right format.
        ValueError: If no events are found for the specified competition in the given season.

    Notes:
        - This function calls `get_url_calendar` and `get_json`.
    """
    if len(season) == 4 and (int(season[0]) * 10 + int(season[1]) + 1 == int(season[2]) * 10 + int(season[3])) :
        calendar = get_json(get_url_calendar(season))
        events = []
        for event in calendar:
            if event["Description"] in competition:
                events.append(event["EventId"])
        return events
    else:
        raise ValueError("The season isn't in the right format. Must be Y1Y2 (eg. 2324 for 2023-2024).")

def races_id(season, competition):
    """
    Retrieves lists of race IDs for women, men, and relay races within a specific competition and season.
    
    Args:
        season (str): The season year for which to retrieve race IDs.
        competition (list of str): The name or description of the competition to filter races by.
    
    Returns:
        list: A list containing three lists:
            - `women_races` (list of int): Race IDs for individual women’s races.
            - `men_races` (list of int): Race IDs for individual men’s races.
            - `relay_races` (list of int): Race IDs for relay races (both genders including mixed relays).
    
    Raises:
        ValueError: If no events or races are found for the specified competition in the given season.
    
    Notes:
        - The function is using `events_id`.
        - The function excludes relay races from individual women and men’s races lists.
"""
    events = events_id(season, competition)
    women_races = []
    men_races = []
    relay_races = []
    for event in events:
        races = get_json(get_url_event(event))
        for race in races:
            if race["catId"] == "SW" and race["DisciplineId"] != "RL":
                women_races.append(race["RaceId"])
            elif race["catId"] == "SM" and race["DisciplineId"] != "RL":
                men_races.append(race["RaceId"])
            else:
                relay_races.append(race["RaceId"])
    return [women_races, men_races, relay_races]
        

def shooting_stats(Discipline_Id, shootings):
    """
    Calculates shooting statistics based on the discipline and shooting results in a race.
    
    Args:
    Discipline_Id (str): Discipline identifier (e.g. "IN", "SI", "SP", "PU", "MS").
    shootings (str): String representing the athlete's faults for each shot in the race, separated by +
    
    Returns:
    list of int: Shooting statistics in the form [prone shooting, total target, standing shooting, total target].
    
    Raises:
    ValueError: If the number of entries in `shootings` does not match the expected format
    for the specified discipline.
    ValueError: If `Discipline_Id` is not recognized.
    
    Notes :
        - The actual version of the function doesn't accept relays' discipline Id.
   """
    if Discipline_Id == "IN" or Discipline_Id == "SI":
        if len(shootings) != 7:
            raise ValueError("Inconsistency: 'IN' and 'SI' disciplines require a length of 7 (4 shots) in `shootings`.")
        else:
            return [10 - (int(shootings[0]) + int(shootings[4])), 10, 10 - (int(shootings[2]) + int(shootings[6])), 10]
    elif Discipline_Id == "SP":
        if len(shootings) != 3:
            raise ValueError("Inconsistency: 'IN' and 'SI' disciplines require a length of 3 (2 shots) in `shootings`.")
        else:
            return [5 - int(shootings[0]), 5, 5 - int(shootings[2]), 5]
    elif Discipline_Id == "PU" or Discipline_Id == "MS":
        if len(shootings) != 7:
            raise ValueError("Inconsistency: 'IN' and 'SI' disciplines require a length of 7 (4 shots) in `shootings`.")
        else:
            return [10 - (int(shootings[0]) + int(shootings[2])), 10, 10 - (int(shootings[4]) + int(shootings[6])), 10]
    else:
        raise ValueError("Unrecognized race format for 'Discipline_Id'.")

def time_conversion(time_str):
    """
    Converts a time string to an integer representing the total time in tenth of a second.

    Args:
        time_str (str): The time to convert, in the format '(minutes:)seconds.tenth'.

    Returns:
        int: The total time in tenth of a second.

    Raises:
        ValueError: If the format of time_str is invalid or if the parts are not numbers.
    """
    try:
        if len(time_str) > 4:
            minutes_str, seconds_tenth_str = time_str.split(':')
            seconds_str, tenth_str = seconds_tenth_str.split('.')
            
            minutes = int(minutes_str)
            seconds = int(seconds_str)
            tenth = int(tenth_str)
        else:
            seconds_str, tenth_str = time_str.split('.')
            seconds = int(seconds_str)
            tenth = int(tenth_str)
            minutes = 0
        
        if seconds < 0 or seconds >= 60 or tenth < 0 or tenth >= 10:
            raise ValueError("Invalid time format: seconds must be between 0 and 59, and tenths between 0 and 9.")
        
        total_time_in_tenth = minutes * 600 + seconds * 10 + tenth
        return total_time_in_tenth
    
    except ValueError:
        raise ValueError("Invalid time format. Use the format '(minutes:)seconds.tenth' with numeric values.")

def time_conversion2(total_time_in_tenth):
   """
   Converts a time integer representing the time in tenth of a second to a string.

   Args:
       total_time_in_tenth (int): The time in thenth of a second.

   Returns:
       str : The time converted, in the format '(minutes:)seconds.tenth'.
   """
   minutes = int(total_time_in_tenth // 600)
   seconds = int((total_time_in_tenth % 600) // 10)
   tenth = int(total_time_in_tenth % 10)
   
   if minutes > 0:
       return f"{minutes}:{seconds:02d}.{tenth}"
   else:
       return f"{seconds}.{tenth}"
    

def skiing_stats(skiing):
    """
    Calculates and returns reference skiing times, in thenth of a second, of a race, based on a list of skier data, 
    including the best time, the time for the 10th place skier, and the median time. 

    Args:
        skiing (list of dict): A list of dictionaries where each dictionary represents a skier's 
                               data with a "TotalTime" key indicating their total skiing time as a string.

    Returns:
        list: A list containing three times in tenth of a second:
            - Best_time (int): The fastest time.
            - T10_time (int): The time for the 10th place skier.
            - Median_time (int): The median time.

    Note:
        Assumes the list `skiing` is sorted in ascending order by "TotalTime".
   """
    Median_time = time_conversion(skiing[int(len(skiing)/2)]["TotalTime"])
    T10_time = time_conversion(skiing[9]["TotalTime"])
    Best_time = time_conversion(skiing[0]["TotalTime"])
    return [Best_time, T10_time, Median_time]

def get_race_data(Race_Id): 
    """
    Retrieves and processes data for a specific race, using the race ID, to compile
    information on athletes' performances, including shooting and skiing statistics.
    
    Args:
        Race_Id (int): The ID of the race to retrieve data for.
    
    Returns:
        dict: A dictionary where each key is an athlete's IBU ID and each value is a dictionary
              containing the following information about the athlete:
              - "Name" (str): The athlete's last name.
              - "Firstname" (str): The athlete's first name.
              - "Rank" (int): The athlete's race rank.
              - "Prone" (int): Prone hits.
              - "Prone_shooted" (int): Prone shots.
              - "Standing" (int): Standing hits.
              - "Standing_shooted" (int): Standing shots.
              - "Skiing time" (str): Total skiing time in the original time format.
              - "Skiing rank" (int): Rank in skiing performance.
              - "BFB" (float): Percentage difference from the best skiing time.
              - "BFM" (float): Percentage difference from the median skiing time.
              - "BFT10" (float): Percentage difference from the 10th place skiing time.
              - "Shooting time" (int): Total shooting time in tenth of a second (per shooting)
              - "Total shooting time" : Total shooting time in the original time format.
    
    Raises:
        ValueError: If the race has not taken place or analysis data is unavailable.
    
    Notes:
        - This function fetches race data using helper functions like `get_url_analytics`, `get_url_results`,
          `get_json`, `shooting_stats`, `skiing_stats`, and `time_conversion`.
        - This function only works with individual races. For relays a function 'get_relay_data' will further be available.
"""
    shooting_time_request = get_url_analytics(Race_Id, "STTM")
    course_time_request = get_url_analytics(Race_Id, "CRST")
    results_request = get_url_results(Race_Id)
    shooting_time = get_json(shooting_time_request)
    course_time = get_json(course_time_request)
    results = get_json(results_request)
    
    if results["IsResult"] == False or results["Competition"]["HasAnalysis"] == False:
        raise ValueError("La course n'a pas eu lieu ou les données ne sont pas disponibles")
    else:
        competition_type = results["Competition"]["DisciplineId"]
        data = {}
        for athlete in results["Results"]:
            shootings = athlete["Shootings"]
            if athlete["Rank"] is not None:
                data[athlete["IBUId"]] = {"Id" : athlete["IBUId"],"Name": athlete["FamilyName"], "Firstname": athlete["GivenName"], "Rank": int(athlete["Rank"]), "Prone": shooting_stats(competition_type, shootings)[0], "Prone_shooted": shooting_stats(competition_type, shootings)[1], "Standing": shooting_stats(competition_type, shootings)[2], "Standing_shooted": shooting_stats(competition_type, shootings)[3]}
        
        Reference_times = skiing_stats(course_time["Results"])      
        for athlete in course_time["Results"]:
            if athlete["IBUId"] in data:
                data[athlete["IBUId"]]["Skiing time"] = athlete["TotalTime"]
                data[athlete["IBUId"]]["Skiing rank"] = int(athlete["Rank"])
                data[athlete["IBUId"]]["BFB"] = round(((time_conversion(athlete["TotalTime"]) - Reference_times[0]) / Reference_times[0]) * 100, 2)
                data[athlete["IBUId"]]["BFM"] =  round(((time_conversion(athlete["TotalTime"]) - Reference_times[2]) / Reference_times[2]) * 100, 2)
                data[athlete["IBUId"]]["BFT10"] = round(((time_conversion(athlete["TotalTime"]) - Reference_times[1]) / Reference_times[1]) * 100, 2)
    
        for athlete in shooting_time["Results"]:
            if athlete["IBUId"] in data:
                data[athlete["IBUId"]]["Shooting time"] = int(time_conversion(athlete["TotalTime"])/((data[athlete["IBUId"]]["Prone_shooted"] + data[athlete["IBUId"]]["Standing_shooted"])/5))
                data[athlete["IBUId"]]["Total shooting time"] = athlete["TotalTime"]
        return data
    
def create_csv_race_data(Race_Id, path = r"C:/", file = None):
    """
    Generates a CSV file containing race data for a specified race ID, with details for each athlete,
    and saves it to the specified directory.

    Args:
        Race_Id (int): The ID of the race to retrieve data for.
        path (str, optional): The directory path where the CSV file will be saved.
                              Defaults to "C:/".
        file (str, optional): The name of the CSV file to be created. If not provided,
                              defaults to the Race_Id as the file name.

    Returns:
        None

    Raises:
        ValueError: If the race data is not available or the race has not occurred.

    Notes:
        - This function calls `get_race_data` to retrieve the race data, so only works with individual races.
        - The CSV is saved with a semicolon (';') separator.
    """    
    if file == None:
        file = Race_Id + ".csv"
    data = get_race_data(Race_Id)
    
    columns = list(data[next(iter(data))].keys())
    df = pd.DataFrame(columns=columns)
    
    i = 0
    for athlete in data:
        for key in list(data[athlete].keys()):
            df.loc[i,key] = data[athlete][key]
        i += 1
    df.to_csv(op.join(path,file),sep=';',index=False)
   
def get_all_races(season, competition, path):
    """
    Retrieves and saves biathlon race data for a specified season and competition.
    The function creates directories for each category (women and men) including all the races' data in CSV format
    in the given path.


    Args:
        season (str): The season for which to retrieve races in the format Y1/Y2 (eg.,"2324" for "2023/2024").
        competition (list of str): The competitions' name. To make it easier, you can also use "1" for World Cup competitions,
                                   "2" for IBU Cup competitions or "3" for junior competitions
        path (str): The base path where 'women' and 'men' folders will be created to 
                    store race data.

    Notes:
        - The commented section will be further used for handling relay data,
          but this relies on a function that has not yet been developed.

    """    
    if competition == "1":
        competition = ["BMW IBU World Cup Biathlon", "IBU World Championships Biathlon"]
    if competition == "2":
        competition = ["IBU Cup Biathlon", "IBU Open European Championships Biathlon"]
    if competition == "3":
        competition = ["IBU Junior Cup Biathlon", "IBU Junior Open European Championships", "IBU Youth/Junior World Championships"]
    races = races_id(season, competition)
    for race in races[0]:
        print("Extract data from <", race, ">")
        os.makedirs(op.join(path, "women"), exist_ok=True)
        try:
            create_csv_race_data(race, op.join(path, "women"))   
        except ValueError: 
            continue
    for race in races[1]:
        print("Extract data from <", race, ">")
        os.makedirs(op.join(path, "men"), exist_ok=True)
        try:
            create_csv_race_data(race, op.join(path, "men"))  
        except ValueError: 
            continue
    #for race in races[2]:
    #    os.makedirs(op.join(path, "relays"), exist_ok=True)
    #    try:
    #       create_csv_relay_data(race, op.join(path, "relays")) 
    #    except ValueError: 
    #       continue
   
def data_synthesis(path):
    combined_data = {}
    number_of_races = {}
    for file in os.listdir(path):
        if file.endswith(".csv") and file != "combined_data.csv":
            df = pd.read_csv(op.join(path,file),sep=';') 
            df = df.drop(["Total shooting time", "Skiing time"], axis = 1)
            for athlete in df.index:
                numeric_data = df.loc[athlete].apply(pd.to_numeric, errors='coerce').dropna()
                numeric_columns = df.select_dtypes(include=['number']).columns
                
                key = df.loc[athlete, "Id"]
                if key in combined_data.keys():
                    for col in numeric_data.index:
                        combined_data[key][col] += numeric_data[col]
                    number_of_races[key] += 1
                else:
                    combined_data[key] = df.loc[athlete]
                    number_of_races[key] = 1
    for key in combined_data:
        for col in numeric_columns:
            if col in combined_data[key]:
                if col != "Prone" and col != "Prone_shooted" and col != "Standing" and col != "Standing_shooted":
                    combined_data[key][col] /= number_of_races[key]
        combined_data[key]['Races'] = number_of_races[key]
    combined_df = pd.DataFrame.from_dict(combined_data, orient='index')
    combined_df.reset_index(drop=True, inplace=True)
    
    combined_df.to_csv(op.join(path, "combined_data.csv"), sep=';', index=False)
    return combined_df
            
def final_df(df):
    """
    Processes and refines a biathlon DataFrame by calculating shooting accuracy, 
    formatting shooting time, and rounding numerical data.
    
    This function takes a DataFrame containing biathlon performance data, calculates 
    shooting accuracy as a percentage for both prone and standing positions, formats 
    the shooting time, and rounds all numeric values to two decimal places and then 
    returns the modified DataFrame.
    
    Parameters
    ----------
    df (pandas.DataFrame) :
        A DataFrame containing biathlon data including columns including "Prone", "Prone_shooted",
        "Standing", "Standing_shooted", and "Shooting time". 
    
    Returns
    -------
    pandas.DataFrame
        A processed DataFrame with new shooting accuracy columns, formatted "Shooting time", and all numeric values 
        rounded to two decimal places. Columns used for calculating accuracy are removed.
    
    Notes
    - The function uses `time_conversion2` to format values in the "Shooting time" column.
"""
    df["Prone_shooting"] = ((df["Prone"] / df["Prone_shooted"]) * 100).round(2)
    df["Standing_shooting"] = ((df["Standing"] / df["Standing_shooted"]) * 100).round(2)
    df = df.drop(["Prone", "Prone_shooted", "Standing", "Standing_shooted"], axis = 1)
    df["Shooting time"] = df["Shooting time"].apply(time_conversion2)
    df = df.round(2)
    return df

def season_data(season, competition, path):
    """
    Collects, processes, and exports biathlon data for a specified season.

    This function coordinates the retrieval and processing of biathlon race data
    for a given season and competition. It then generates CSV files for individual
    athlete data (for both women and men) after processing.

    Parameters
    ----------
    season : str
        The competition season in format Y1Y2 (e.g., "2324" for "2023-2024").
    competition : list of str
        List of the type of competition you want to get the data from.
        You can use:
            - "1" for World Cup and World Championships.
            - "2" for IBU Cup and European Championships.
            - "3" for Junior Cup and Junior Championships.
            
        Available competitions are "BMW IBU World Cup Biathlon", "IBU World Championships Biathlon", "IBU Cup Biathlon",
        "IBU Open European Championships Biathlon", "IBU Junior Cup Biathlon", "IBU Junior Open European Championships", 
        "IBU Youth/Junior World Championships", "IBU Summer Biathlon World Championships"
    path : str
        The directory path where the race data and resulting CSV files will be stored.

    Returns
    -------
    None
        Saves CSV files for women and men athletes in the specified directory.
        Does not return any value.

    Notes
    -----
    - This function relies on two helper functions: `get_all_races` and `data_synthesis`.
      `get_all_races` fetches the race data, while `data_synthesis` aggregates and processes
      the data before it is saved as individual records for each athlete.
    - Processed CSV files are saved with the names "women individual data.csv" and
      "men individual data.csv" in the provided path.
    """
    print("Extract race data.")
    get_all_races(season, competition, path) 
    print("Build women final csv file.")
    final_df(data_synthesis(op.join(path, "women"))).to_csv(op.join(path, "women individual data.csv"), sep = ';', index = False)
    print("Build men final csv file.")
    final_df(data_synthesis(op.join(path, "men"))).to_csv(op.join(path, "men individual data.csv"), sep = ';', index = False)
    print("Data is retrieved")

## EXAMPLE OF USE ##
#season_data("2324","1",r"C:\Users\KML_Style\Documents\test") #: get the data for 2023-2024 WC/WCH in the path folder test
#season_data("2324","2",r"C:\Users\KML_Style\Documents\test") #: get the data for 2023-2024 IBUCup/ECH in the path folder test
