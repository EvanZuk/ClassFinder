from app import app
from app.utilities.env import devmode
from waitress import serve

if devmode: print('Running in dev mode')
else: print('Running in production mode')

if __name__ == '__main__':
    if devmode:
        app.run(host='0.0.0.0', port=5200, debug=True)
    else:
        serve(app, host='0.0.0.0', port=7842)