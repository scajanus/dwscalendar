from flask import Flask,render_template,g,request
import sqlite3
import json
import calendar
from datetime import datetime,timedelta
app = Flask(__name__)

class DWSCalendar(calendar.Calendar):
    def dwsdayscalendar(self, year, month):
        """
        Return a matrix representing a month's calendar.
        Each row represents a week; days outside this month are zero.
        """
        db = get_db()
        cur = db.cursor()
        cur.execute("""
        SELECT cast(strftime('%d', date) as integer) as day, type FROM trip WHERE date >= date(?) AND date < date(?,'+1 month')
        """,
                    (datetime(year,month,1),
                    datetime(year,month,1),
                    ))
        db_days = dict(cur.fetchall())
        t = ['&nbsp;', 'AM', 'PM', 'All Day']
        days = list(self.itermonthdays(year, month))
        return [ [(day, t[db_days.get(day, 0)]) for day in days[i:i+7]] for i in range(0, len(days), 7) ]

myDWSCalendar = DWSCalendar()
DATABASE = '../../dwscalendar/tides.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


def query_db(query, args=()):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return rv if rv else None

@app.route('/hello/')
@app.route('/hello/<name>')
def hello(name=None):
    return render_template('hello.html', name=name,)

@app.route('/')
def dwscalendar():
    year, month, date = int(request.args.get('year',2018)), int(request.args.get('month',10)), int(request.args.get('date',1))
    cal = myDWSCalendar.dwsdayscalendar(year, month)
    return render_template('calendar.html',
            cal=cal,
            year=year,
            month=month,
            month_name=calendar.month_name[month])


@app.route('/plot')
def plot():
    year, month, date = int(request.args.get('year',2018)), int(request.args.get('month',10)), int(request.args.get('date',1))
    d = datetime(year, month, date)
    query = """
SELECT * FROM tide WHERE date > date(?) AND date < date(?)
"""
    data = query_db(query, [d, (d+timedelta(1))])
    xs, ys = [], []
    for x, y in data:
        xs.append(x)
        ys.append(y)

    graphs = dict(
            data=[
                dict(
                    line= {'shape': 'spline', 'smoothing': 1.3},
                    fill='tozeroy',
                    x=xs,
                    y=ys
                    )
                ],
            layout=dict(title='{}-{:02d}-{:02d}'.format(year, month, date),
                xaxis=dict(tickformat='%H:%M',
                    ),
                paper_bgcolor= 'rgba(245,246,249,1)',
                plot_bgcolor= 'rgba(245,246,249,1)',),
            config={
                'displayModeBar': False,
                'showLink': False
                }
            )

    # Convert the figures to JSON
    # PlotlyJSONEncoder appropriately converts pandas, datetime, etc
    # objects to their JSON equivalents
    #graphJSON = json.dumps(graphs, cls=plotly.utils.PlotlyJSONEncoder)
    graphJSON = json.dumps(graphs)

    return render_template('plot.html',
                           year=year,
                           month=month,
                           date=d.strftime('%Y-%m-%d'),
                           graphJSON=graphJSON)
    return resp

if __name__ == "__main__":
    app.run(debug=True)
