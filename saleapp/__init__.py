from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from urllib.parse import quote
import cloudinary
from flask_login import LoginManager
from flask_socketio import SocketIO
from transformers import pipeline
from sentence_transformers import SentenceTransformer
from joblib import dump, load
from langchain.text_splitter import CharacterTextSplitter

app = Flask(__name__)

app.secret_key = '689567gh$^^&*#%^&*^&%^*DFGH^&*&*^*'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:123456@localhost/quanlysinhvien?charset=utf8mb4'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['PAGE_SIZE'] = 4
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

import os

current_directory = os.getcwd()

#**load txt

from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
#model_checkpoint = "vinai/phobert-base-v2"
# model_checkpoint = "nguyenvulebinh/vi-mrc-base"
model_checkpoint = "sentence-transformers/all-MiniLM-L6-v2"

tokenizer = AutoTokenizer.from_pretrained(model_checkpoint, token= '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')
from langchain.document_loaders import TextLoader

document = TextLoader(
    os.path.join(current_directory,'data/22.8.2022-So-tay-SV-2022.txt'), encoding= 'utf-8'
).load()

text_splitter = CharacterTextSplitter.from_huggingface_tokenizer(
    tokenizer, chunk_size=512, chunk_overlap=0
)
texts = text_splitter.split_documents(document)

#vector-store
from langchain.embeddings import HuggingFaceEmbeddings
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
from langchain.vectorstores import Chroma
retriever = Chroma.from_documents(texts, embedding=embeddings).as_retriever(
    search_kwargs={"k": 5}
)

#question-anwsering
from transformers import pipeline
question_answerer = pipeline("question-answering", model="deepset/bert-large-uncased-whole-word-masking-squad2",
                             tokenizer="deepset/bert-large-uncased-whole-word-masking-squad2")

#translate
model_name = "VietAI/envit5-translation"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model_translate = AutoModelForSeq2SeqLM.from_pretrained(model_name)