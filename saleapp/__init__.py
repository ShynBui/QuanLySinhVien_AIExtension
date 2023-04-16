from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from urllib.parse import quote
import cloudinary
from flask_login import LoginManager
from flask_socketio import SocketIO
from transformers import pipeline
from sentence_transformers import SentenceTransformer
from joblib import dump, load

app = Flask(__name__)

app.secret_key = '689567gh$^^&*#%^&*^&%^*DFGH^&*&*^*'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Admin123@localhost/quanlysinhvien?charset=utf8mb4'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['PAGE_SIZE'] = 8
app.config['COMMENT_SIZE'] = 8
app.config['PAGE_INF'] = 9999

cloudinary.config(
    cloud_name = "dhffue7d7",
    api_key = "215425482852391",
    api_secret = "a9xaGBMJr7KgKhJa-1RpSpx_AmU"
)

db = SQLAlchemy(app=app)
login = LoginManager(app=app)
socketio = SocketIO(app)

model_checkpoint = "ShynBui/bert-finetuned-squad"
question_answerer = pipeline("question-answering", model=model_checkpoint)
model_multiple = SentenceTransformer('sentence-transformers/bert-base-nli-mean-tokens')
model_gk_ck_nhapmon = load('model/model_gk_ck_nhapmon.joblib')
hub_model_id = "huggingface-course/mt5-small-finetuned-amazon-en-es"
summarizer = pipeline("summarization", model=hub_model_id)