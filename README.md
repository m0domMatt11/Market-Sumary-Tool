# Market-Sumary-Tool
Create a Python application that reads historical prices from a CSV file and produces a market summary.

# Installation

Requires a python IDE and python interpreter to run.

1. Pull the code or copy the code and file structure from the git hub repository
2. Identify the "target folder" variable this is set to "Output" by default. Feel free to edit the name of the folder you would like the results to be inputted to by: changing the variable "main.py" and changing the name of the "Output" folder accordingly
3. Place the CSV file of daily data into the "Data" folder with the format of (Year-Month-Day) purely numerical: for example "2026-08-07.csv" for the 7th of August 2026.
4. Run market-summary-pdf-gen.py first to ensure the functions that are to be imported by main.py are recogniseable
5. Run main.py
6. Find results with the designated output folder under todays date

# For multiple use

Simply add the days data into the Data file along with the all the other files as the code will recognise it - no need to delete anything

It should be known that if the days data is inputted on a different day then it won't be recognised by the code and an error will arise
If you wish to change this then all code referring to pd.datetime.today should be looked into being "yesterday" - I will not be advising on how to modify my code like this within this article and if you wish to perform such an action you do so at your own risk and should be advised to thoroughly check each python file.
