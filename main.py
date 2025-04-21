import os
from fastapi import FastAPI, UploadFile, File
from PIL import Image
import io
from transformers import BlipProcessor, BlipForConditionalGeneration
from langchain_community.llms import OpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
from typing import List

load_dotenv()

app = FastAPI() 

processor = BlipProcessor.from_pretrained(
    "Salesforce/blip-image-captioning-base",
    use_fast=True  
)

model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")

llm = ChatGoogleGenerativeAI(
    model="models/gemini-1.5-pro-002",
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

prompt = PromptTemplate(
    input_variables=["caption"],
    template="Given the image caption: '{caption}', generate 3 relevant content tags or categories."
)

chain = prompt | llm 

@app.post("/upload/")
async def upload_image(file: UploadFile = File(...)):
    image_data = await file.read()
    image = Image.open(io.BytesIO(image_data)).convert('RGB')

    inputs = processor(images=image, return_tensors="pt")
    out = model.generate(**inputs)
    caption = processor.decode(out[0], skip_special_tokens=True)

   
    result = chain.invoke({"caption": caption}) 

    return {
        "caption": caption,
        "tags": result
    }