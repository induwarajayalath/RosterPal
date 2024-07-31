# Importing flask module in the project is mandatory
# An object of Flask class is our WSGI application.
from flask import Flask, jsonify, render_template
import datetime
import pandas as pd

# Flask constructor takes the name of
# current module (__name__) as argument.
app = Flask(__name__)

# The route() function of the Flask class is a decorator,
# which tells the application which URL should call
# the associated function.


@app.route('/')
# ‘/’ URL is bound with home() function.
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


# df = pd.read_csv(
    # '/Users/induwarajayalath/Desktop/GenixLabs/Projects/RosterPal/US-SO-Roster.csv')
df = pd.read_csv('/home/azureuser/RosterPal/US-SO-Roster.csv')


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
    # Since there are four columns to skip
    day_of_year = date.timetuple().tm_yday + 4
    day_of_year += 175  # since the CSV is from 10th of JULY
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
    # else:
    #     print(f"Value '{name}' not found in the DataFrame")
    value = df.iloc[row_number, dayNumber]
    value_for_leave = value
    leave = ''
    if 'm' in value:
        value = 'Morning'
    elif 'a' in value:
        value = 'Afternoon'
    elif 'n' in value:
        value = 'Night'
    elif 'x' in value:
        value = 'Shift Leave'
        leave = '-'
    else:
        value = 'No Data :('

    if 'h' in value_for_leave:
        leave = 'Half Day'
    elif 's' in value_for_leave:
        leave = 'Short Leave'
    elif 'f' in value_for_leave:
        leave = 'Full Day'
    result = [{
        'Name': name,
        'Shift': value,
        'Leave': leave
    }]
    return result


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
    alarm1 = ''
    alarm2 = ''
    if value == 'm':
        alarm1 = '6:00'
        alarm2 = '6:59'
        value = 'Morning'
    elif value == 'a':
        alarm1 = '14:00'
        alarm2 = '14:59'
        value = 'Afternoon'
    elif value == 'n':
        alarm1 = '22:00'
        alarm2 = '22:59'
        value = 'Night'
    else:
        alarm1 = 'null'
        alarm2 = 'null'
        value = 'Shift Leave'
    result = [{
        'alarm1': alarm1,
        'alarm2': alarm2,
        'shift': value
    }]
    return result
