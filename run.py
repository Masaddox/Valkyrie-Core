import os


os.environ['FLASK_APP'] = 'main.py'
os.environ['FLASK_ENV'] = 'venv'

for file in os.listdir(f"{os.getcwd()}"):
    if file == "cert.pem":

        print("start https")
        os.system("flask run --cert=cert.pem --key=key.pem")
        break
else:

    print("start http")
    os.system("flask run")
