# Importing flask module in the project is mandatory
# An object of Flask class is our WSGI application.
from flask import Flask, jsonify, render_template
import datetime
from datetime import date, timedelta
import pandas as pd
import os

# Flask constructor takes the name of
# current module (__name__) as argument.
app = Flask(__name__)

# The route() function of the Flask class is a decorator,
# which tells the application which URL should call
# the associated function.


@app.route('/')
# ‘/’ URL is bound with home() fu nction.
def home():
    return render_template('index.html')


@app.route('/personal')
def personal():
    return render_template('personal.html')


@app.route('/team')
def team():
    return render_template('team.html')


# main driver function
if __name__ == '__main__':
    app.run(debug=False)

CSV_FILE_PATH = os.path.join(os.path.dirname(__file__), 'US-SO-Roster.csv')
print(CSV_FILE_PATH)
df = pd.read_csv(CSV_FILE_PATH)


def extract_names(search_param):
    matching_names = df['Name'][df['Name'].str.contains(
        search_param, case=False, na=False)].tolist()
    if not matching_names:
        return []
    else:
        return matching_names


def extract_team(search_param):
    matching_names = df['Team Name'][df['Team Name'].str.contains(
        search_param, case=False, na=False)].tolist()
    distinct_values = list(set(matching_names))
    if not distinct_values:
        return []
    else:
        return distinct_values


def returnDay(year, month, day):
    date = datetime.datetime(year, month, day)
    day_of_year = date.timetuple().tm_yday
    day_of_year += 175  # since the CSV is from 10th of JULY
    day_of_year += 4  # Since there are four columns to skip
    return day_of_year


def clean_shift(shift):
    if isinstance(shift, str):  # Check if shift is a string
        if 'm' in shift:
            return 'm'
        elif 'a' in shift:
            return 'a'
        elif 'n' in shift:
            return 'n'
    return None


def clean_shift_leave(shift):
    if isinstance(shift, str):  # Check if shift is a string
        if 'f' in shift:
            return 'Full Day'
        elif 'h' in shift:
            return 'Half Day'
        elif 's' in shift:
            return 'Short Leave'
    return ''


def determine_shift(value):
    if isinstance(value, str):
        if 'm' in value:
            return 'Morning'
        elif 'a' in value:
            return 'Afternoon'
        elif 'n' in value:
            return 'Night'
        elif 'x' in value:
            return 'Shift Leave'
        else:
            return 'No Data :('
    return ''


def determine_alarms(value):
    if value == 'm':
        alarm1 = '6:00'
        alarm2 = '6:59'
        shift = 'Morning'
    elif value == 'a':
        alarm1 = '14:00'
        alarm2 = '14:59'
        shift = 'Afternoon'
    elif value == 'n':
        alarm1 = '22:00'
        alarm2 = '22:59'
        shift = 'Night'
    else:
        alarm1 = 'null'
        alarm2 = 'null'
        shift = 'Shift Leave'
    return shift, alarm1, alarm2


@app.route('/getRoster/<int:year>/<int:month>/<int:date>/<name>', methods=['GET'])
def getRoster(name, year, month, date):
    name = extract_names(name)
    if len(name) > 1:
        # print('There are multiple matches. Please select one and re run - ')
        return name
    elif len(name) == 1:
        name = name[0]
    elif len(name) == 0:
        return 'Error occured'
    dayNumber = returnDay(year, month, date)
    result = df.isin([name])
    positions = list(zip(*result.to_numpy().nonzero()))
    if positions:
        for position in positions:
            row, col = position
            row_number = row
    to_return = [{
        'Name': name,
        'Roster': df.iloc[row_number, 1]
    }]
    # else:
    #     print(f"Value '{name}' not found in the DataFrame")
    for i in range(7):
        value = df.iloc[row_number, dayNumber+i]
        shift = determine_shift(value)
        leave = clean_shift_leave(value)
        original_date = datetime.date(int(year), int(month), int(date))
        new_date = original_date + timedelta(days=i)
        result = [{
            'Date': new_date.strftime("%A, %d/%b/%Y"),
            'Shift': shift,
            'Leave': leave
        }]
        to_return.append(result)
    return to_return


@app.route('/listMembers/<int:year>/<int:month>/<int:date>/<verticle>/<shift>', methods=['GET'])
def listMembers(year, month, date, verticle, shift):
    team = extract_team(verticle)
    if len(team) > 1:
        return team
    dayNumber = returnDay(year, month, date)

    # filtered_df = df[(df.iloc[:, dayNumber].apply(clean_shift) == shift)
    #                  & (df.iloc[:, 0] == team[0])]

    # filtered_df = df[df.iloc[:, dayNumber].apply(clean_shift) == shift
    #                  & (df.iloc[:, 0] == team[0])]

    filtered_df = df[df.iloc[:, dayNumber].apply(lambda x: clean_shift(x) == shift)
                     & (df.iloc[:, 0] == team[0])]

    role = filtered_df['Job Role']
    name = filtered_df['Name']
    cap = filtered_df['Capabilities'].fillna('')
    leave = filtered_df.iloc[:, dayNumber].apply(clean_shift_leave)
    result = [{'Verticle': team[0]}]
    for i in range(len(name)):
        result.append({
            'role': role.iloc[i],
            'name': name.iloc[i],
            'leave': leave.iloc[i],
            'cap': cap.iloc[i]
        })
    return jsonify(result)


@app.route('/getAlarms/<int:year>/<int:month>/<int:date>/<name>', methods=['GET'])
def getAlarms(name, year, month, date):
    name = extract_names(name)
    if len(name) == 1:
        name = name[0]
    else:
        result = [{
            'alarm1': '6:30',
            'alarm2': '6:59',
            'shift': 'Error Occured'
        }]
        return result
    dayNumber = returnDay(year, month, date)
    result = df.isin([name])
    positions = list(zip(*result.to_numpy().nonzero()))

    if positions:
        for position in positions:
            row, col = position
            row_number = row
    # else:
    #     print(f"Value '{name}' not found in the DataFrame")
    value = df.iloc[row_number, dayNumber]
    shift, alarm1, alarm2 = determine_shift(value)
    result = [{
        'alarm1': alarm1,
        'alarm2': alarm2,
        'shift': shift
    }]
    return result
