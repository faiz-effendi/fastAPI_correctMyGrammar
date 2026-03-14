import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from openai import AsyncOpenAI
from dotenv import load_dotenv

# Load API key dari file .env
load_dotenv()

# Inisialisasi aplikasi FastAPI
app = FastAPI(title="Grammar Fixer API")

# Setup OpenAI Client
# Otomatis ngambil dari variabel OPENAI_API_KEY di .env
client = AsyncOpenAI()

# Definisikan format payload/body yang diterima API
class TextInput(BaseModel):
    text: str

@app.post("/fix-grammar")
async def fix_grammar(data: TextInput):

    if not data.text.strip():
        raise HTTPException(status_code=400, detail="Teks tidak boleh kosong ya")

    try:
        # Tembak ke API OpenAI
        response = await client.chat.completions.create(
            model="gpt-4o-mini", # Lo bisa ganti ke gpt-4o-mini kalau mau lebih murah/cepat
            messages=[
                {
                    "role": "system", 
                    "content": "You are a strict grammar corrector. Your ONLY task is to return the corrected version of the user's English text. Fix grammatical, spelling, and punctuation errors. Do NOT add explanations, conversational filler, or quotes. If the text is correct, return it exactly as is."
                },
                {
                    "role": "user", 
                    "content": data.text
                }
            ],
            temperature=0.0 # Bikin 0 biar AI gak halusinasi dan fokus benerin teks aja
        )
        
        # Ambil hasil teks yang udah dibenerin
        corrected_text = response.choices[0].message.content.strip()
        
        # Kembalikan response dalam bentuk JSON
        return {
            "status": "success",
            "original": data.text, 
            "corrected": corrected_text
        }
        
    except Exception as e:
        # Kalau saldo habis atau server OpenAI down, errornya ditangkap di sini
        raise HTTPException(status_code=500, detail=str(e))