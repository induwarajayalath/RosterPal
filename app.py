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
 #    '/Users/induwarajayalath/Desktop/GenixLabs/Projects/RosterPal/US-SO-Roster.csv')
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
    day_of_year = date.timetuple().tm_yday + 4
    return day_of_year


@app.route('/getRoster/<int:year>/<int:month>/<int:date>/<name>', methods=['GET'])
def getRoster(name, year, month, date):
    name = extract_names(name)
    if len(name) > 1:
        print('There are multiple matches. Please select one and re run - ')
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
    else:
        print(f"Value '{name}' not found in the DataFrame")
    value = df.iloc[row_number, dayNumber]
    if value == 'm':
        value = 'Morning'
    elif value == 'a':
        value = 'Afternoon'
    elif value == 'n':
        value = 'Night'
    elif value == 'x':
        value = 'Shift Leave'
    else:
        value = 'No Data :('
    result = [{
        'Name': name,
        'Shift': value
    }]
    return result


@app.route('/listMembers/<int:year>/<int:month>/<int:date>/<verticle>/<shift>', methods=['GET'])
def listMembers(year, month, date, verticle, shift):
    team = extract_team(verticle)
    if len(team) > 1:
        return team
    dayNumber = returnDay(year, month, date)

    filtered_df = df[(df.iloc[:, dayNumber] == shift)
                     & (df.iloc[:, 0] == team[0])]

    role = filtered_df['Job Role']
    name = filtered_df['Name']
    result = [{'Verticle': team[0]}]
    for i in range(len(name)):
        result.append({
            'role': role.iloc[i],
            'name': name.iloc[i]
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
    else:
        print(f"Value '{name}' not found in the DataFrame")
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
