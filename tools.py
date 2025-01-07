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

def time_conversion(time_str):
    """
    Converts a time string to an integer representing the total time in tenths of a second.

    Args:
        time_str (str): The time to convert, in the format '(hours:minutes:)seconds.tenth'.

    Returns:
        int: The total time in tenths of a second.

    Raises:
        ValueError: If the format of time_str is invalid or if the parts are not numbers.
    """
    try:
        parts = time_str.split(':')
        
        if len(parts) == 3:
            hours_str, minutes_str, seconds_tenth_str = parts
            hours = int(hours_str)
            minutes = int(minutes_str)
        elif len(parts) == 2:
            hours = 0
            minutes_str, seconds_tenth_str = parts
            minutes = int(minutes_str)
        elif len(parts) == 1:
            hours = 0
            minutes = 0
            seconds_tenth_str = parts[0]
        else:
            raise ValueError("Invalid time format.")
        
        seconds_str, tenth_str = seconds_tenth_str.split('.')
        seconds = int(seconds_str)
        tenth = int(tenth_str)
        
        if seconds < 0 or seconds >= 60 or tenth < 0 or tenth >= 10:
            raise ValueError("Invalid time format: seconds must be between 0 and 59, and tenths between 0 and 9.")
        if minutes < 0 or minutes >= 60:
            raise ValueError("Invalid time format: minutes must be between 0 and 59.")
        if hours < 0:
            raise ValueError("Invalid time format: hours cannot be negative.")
        
        total_time_in_tenth = hours * 36000 + minutes * 600 + seconds * 10 + tenth
        return total_time_in_tenth
    
    except ValueError:
        raise ValueError("Invalid time format. Use the format '(hours:minutes:)seconds.tenth' with numeric values.")


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