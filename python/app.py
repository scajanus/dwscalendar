from flask import Flask,render_template
import calendar
app = Flask(__name__)

@app.route('/hello/')
@app.route('/hello/<name>')
def hello(name=None):
    return render_template('hello.html', name=name,)

@app.route('/calendar/')
def dwscalendar():
    cal = calendar.monthcalendar(2018,10)
    return render_template('calendar.html', calendar=cal,)

@app.route('/')
def hello_world():
    return 'Hello, World!'

if __name__ == "__main__":
    app.run(debug=True)
