import os
from fastapi import FastAPI, UploadFile, File
from PIL import Image, UnidentifiedImageError
import io
from transformers import BlipProcessor, BlipForConditionalGeneration, CLIPProcessor, CLIPModel
from langchain_community.llms import OpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
from typing import List
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import torch

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


load_dotenv()


app = FastAPI()


app.mount("/uploads", StaticFiles(directory=UPLOAD_FOLDER), name="uploads")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load BLIP (caption model)
blip_processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base", use_fast=True)
blip_model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")

# Load CLIP (visual embedding model)
clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")


llm = ChatGoogleGenerativeAI(
    model="models/gemini-1.5-pro-002",
    google_api_key=os.getenv("GOOGLE_API_KEY")
)


group_prompt = PromptTemplate(
    input_variables=["captions"],
    template="""
You are helping to organize images based on their captions.

Here are the captions:
{captions}

Group them logically into categories. For each category, suggest a short group label (e.g., "dogs", "ski equipment", "sunsets"). 

Return the group label for each caption, in the same order.
Example format:
- Caption 1 => Group: Dogs
- Caption 2 => Group: Ski Equipment
"""
)

@app.post("/upload/")
async def upload_images(files: List[UploadFile] = File(...)):
    results = []
    captions = []

    for file in files:
        try:
            
            file_path = os.path.join(UPLOAD_FOLDER, file.filename)
            with open(file_path, "wb") as f:
                f.write(await file.read())

            
            image = Image.open(file_path).convert('RGB')

            # Caption the image
            blip_inputs = blip_processor(images=image, return_tensors="pt")
            blip_out = blip_model.generate(**blip_inputs)
            caption = blip_processor.decode(blip_out[0], skip_special_tokens=True)
            captions.append(caption)

            # Get CLIP embedding
            clip_inputs = clip_processor(images=image, return_tensors="pt")
            with torch.no_grad():
                embedding = clip_model.get_image_features(**clip_inputs)
                embedding = embedding / embedding.norm(p=2, dim=-1)
                embedding = embedding.squeeze(0).tolist()

            results.append({
                "filename": file.filename,
                "caption": caption,
                "embedding": embedding,
                "url": f"http://localhost:8000/uploads/{file.filename}"
            })

        except Exception as e:
            results.append({
                "filename": file.filename,
                "error": str(e)
            })

    
    if captions:
        combined_captions = "\n".join([f"- {cap}" for cap in captions])
        smart_prompt = group_prompt.format_prompt(captions=combined_captions).to_string()
        smart_response = llm.invoke(smart_prompt)

        
        lines = smart_response.content.splitlines()
        group_labels = []
        for line in lines:
            if "Group:" in line:
                group = line.split("Group:")[1].strip()
                group_labels.append(group)

        
        for i in range(len(results)):
            if i < len(group_labels):
                results[i]["group_label"] = group_labels[i]
            else:
                results[i]["group_label"] = "Uncategorized"

    return results
