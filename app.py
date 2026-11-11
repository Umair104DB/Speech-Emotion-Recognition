import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
try:
    import librosa
except Exception:
    librosa=None
st.set_page_config(page_title='Speech Emotion Lab',page_icon='🎙️',layout='wide')
st.title('🎙️ Speech Emotion Recognition')
st.caption('MFCC feature workflow with a reproducible demo model.')
df=pd.read_csv(Path(__file__).parent/'data/speech_mfcc_demo.csv')
features=[c for c in df if c.startswith('mfcc_')]
X=df[features]; y=df.emotion
Xtr,Xte,ytr,yte=train_test_split(X,y,test_size=.25,random_state=42,stratify=y)
model=RandomForestClassifier(n_estimators=200,random_state=42).fit(Xtr,ytr)
pred=model.predict(Xte)
a,b=st.columns(2); a.metric('Demo audio feature rows',len(df)); b.metric('Holdout accuracy',f'{accuracy_score(yte,pred):.1%}')
st.dataframe(df.head(15),use_container_width=True)
st.subheader('Upload an audio clip')
file=st.file_uploader('WAV or supported audio file',type=['wav','mp3','ogg','flac'])
if file:
    st.audio(file)
    if librosa is None:
        st.error('Install librosa and its audio dependencies to extract MFCCs: pip install librosa soundfile')
    else:
        try:
            audio,sr=librosa.load(file,sr=22050,duration=10)
            mfcc=librosa.feature.mfcc(y=audio,sr=sr,n_mfcc=13)
            vector=np.mean(mfcc,axis=1).reshape(1,-1)
            st.info('MFCCs extracted from your clip.')
            st.metric('Demo model prediction',model.predict(vector)[0].title())
            st.warning('This prediction uses synthetic demonstration features. Train with labelled RAVDESS, TESS or EMO-DB audio before interpreting real emotion.')
        except Exception as exc: st.error(f'Could not process audio: {exc}')
st.subheader('Model report'); st.text(classification_report(yte,pred))
st.info('The 100-row CSV contains synthetic MFCC-like features, not measurements from real speakers. For a valid research model, replace it with MFCC features extracted from a labelled speech dataset and split by speaker.')
