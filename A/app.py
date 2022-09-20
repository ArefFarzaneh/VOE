from ast import main
from distutils.log import debug
from tkinter.ttk import Style
from flask import Flask,render_template,jsonify,send_file
import pandas as pd
import io
import base64
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.oauth2 import service_account
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import matplotlib.pyplot as plt
import seaborn as sns
sns.set()


SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = './keys.json'

creds = None
creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,scopes=SCOPES)

SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

SAMPLE_SPREADSHEET_ID = '1wMi1a_Igifrz4MtM4nsbXA-SAl7Mo9uO85nVpW-rL_Q'


service = build('sheets', 'v4', credentials=creds)


sheet = service.spreadsheets()
result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                    range='A:M').execute()
values = result.get('values', [])

df = pd.DataFrame(values[1:], columns=values[0])
#df = pd.read_csv('./df.csv')
#del df['Unnamed: 0']

df['Timestamp'] = pd.to_datetime(df['Timestamp'])
df['month']=df['Timestamp'].dt.month
df['day']=df['Timestamp'].dt.day
df['year']=df['Timestamp'].dt.year

try:
    df['name'] = df['لطفا نام خود را وارد نمائید'] 
    df['personal'] = df['لطفا کد پرسنلی خود را ثبت نمائید.'] 
    df['team'] = df['لطفا واحدی که در آن مشغول به فعالیت می باشید را انتخاب نمائید.']
    df['description'] = df['لطفا پیشنهاد خود را شرح دهید:']
    df['field'] = df["پیشنهاد شما در چه حوزه ای می باشد؟"]
    df['documentation'] = df['در صورت نیاز به بارگزاری مستندات برای شفافیت موضوع خود، میتوانید از این قسمت استفاده نمائید.']
    df['Timestamp'] = df['Timestamp'].dt.date


    df['name'] = df['name'].astype(str)
    df['team'] = df['team'].astype(str)
    df['field'] = df['field'].map({'پیشنهاد بهبود (اصلاح رویه- ایجاد رویه جدید)':'suggestion','تولید محتوا':'content','باگ':'bug'})

except Exception as e:
    print(e)
del df['لطفا پیشنهاد خود را شرح دهید:'],df['در صورت نیاز به بارگزاری مستندات برای شفافیت موضوع خود، میتوانید از این قسمت استفاده نمائید.'],df['پیشنهاد شما در چه حوزه ای می باشد؟'],df['لطفا واحدی که در آن مشغول به فعالیت می باشید را انتخاب نمائید.'],df['لطفا کد پرسنلی خود را ثبت نمائید.'],df['لطفا نام خود را وارد نمائید']

a = df.groupby('month',as_index=False)['field'].count()

d = pd.DataFrame(df.name.value_counts().sort_values(ascending=False)).head(10)
d.columns=['# of suggested items']
fig , ax = plt.subplots(1,3,figsize=(20,8))

app = Flask(__name__)



@app.route('/')
def root():
    return render_template('home.html')

@app.route('/table')
def table():
    return render_template('table.html',  tables=[df.to_html(classes='data')], titles =['na'])

@app.route('/Top10')
def Top10():
    return render_template('Top10.html',  tables=[d.to_html(classes='data')], titles = ['na'])


@app.route('/plots')
def home():
    return render_template('index.html')


@app.route('/visualize')
def visualize():
    
    sns.countplot(ax=ax[0],data = df,x = df.field,hue=df.team)
    sns.lineplot(ax=ax[1],x=a.month,y=a.field)
    sns.countplot(ax=ax[2],data = df,x = df.field)
    canvas=FigureCanvas(fig)
    img = io.BytesIO()
    fig.savefig(img)
    img.seek(0)
    
    return send_file(img,mimetype='img/png')


if __name__ == '__main__':
   app.run(host='127.0.0.1',port=6000,debug=True)