from flask import Flask,render_template,g,request,redirect,url_for
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
DATABASE = '../tides.db'

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
    today = datetime.now()
    year, month, date = int(request.args.get('year',today.year)), int(request.args.get('month',today.month)), int(request.args.get('date',today.day))
    delta = int(request.args.get('delta', 0))
    if delta == -1:
        year=year if month>1 else year-1
        month=month-1 if month>1 else 12
        d = datetime(year, month, date)
        return redirect(url_for('dwscalendar', year=d.year, month=d.month, date=d.day))
    elif delta == 1:
        year=year if month<12 else year+1
        month=month+1 if month<12 else 1
        d = datetime(year, month, date)
        return redirect(url_for('dwscalendar', year=d.year, month=d.month, date=d.day))
    cal = myDWSCalendar.dwsdayscalendar(year, month)
    return render_template('calendar.html',
            cal=cal,
            year=year,
            month=month,
            month_name=calendar.month_name[month])


@app.route('/plot')
def plot():
    year, month, date = int(request.args.get('year',2018)), int(request.args.get('month',10)), int(request.args.get('date',1))
    delta = int(request.args.get('delta', 0))
    if delta != 0:
        d = datetime(year, month, date) + timedelta(delta)
        return redirect(url_for('plot', year=d.year, month=d.month, date=d.day))
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
                    fill='tozeroy',
                    x=xs,
                    y=ys
                    )
                ],
            layout=dict(
                margin=dict(l=30,r=10,b=30,t=20),
                xaxis=dict(tickformat='%H:%M',
                    fixedrange=True,
                    gridcolor='#644536',
                    gridwidth=1,
                    ),
                yaxis=dict(fixedrange=True,
                    gridcolor='#644536'
                    ),
                paper_bgcolor= 'rgba(235,236,239,0)',
                plot_bgcolor= 'rgba(235,236,239,0)',),
            config={
                'displayModeBar': False,
                'showLink': False,
                'responsive': True
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
