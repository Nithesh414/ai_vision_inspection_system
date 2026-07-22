from fastapi import APIRouter, UploadFile, File, Form
from pathlib import Path
import shutil
import uuid
import time
import random
from datetime import datetime
from threading import Thread


router = APIRouter(
    prefix="/api/training",
    tags=["Training"]
)


UPLOAD_DIR = Path("uploads/training")

UPLOAD_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# Temporary storage
DATASET = []

PRODUCTS = []



# =================================================
# DISPLAY MODEL STATUS ONLY
# Inspection will continue using old model
# =================================================

MODEL_STATUS = {

    "current_model":
    "Industrial_AI_Model_v1.0",


    "latest_model":
    "Industrial_AI_Model_v1.1",


    "status":
    "Idle",


    "progress":
    0,


    "accuracy":
    0,


    "loss":
    0,


    "dataset_images":
    0,


    "last_training":
    None

}




# =================================================
# CREATE PRODUCT
# =================================================

@router.post("/product")
def create_product(
    name:str = Form(...),
    code:str = Form(...)
):

    product = {

        "id": str(uuid.uuid4()),

        "name": name,

        "code": code,

        "created_at": str(datetime.now())

    }


    PRODUCTS.append(product)


    return product




# =================================================
# GET PRODUCTS
# =================================================

@router.get("/products")
def get_products():

    return PRODUCTS





# =================================================
# UPLOAD TRAINING IMAGE
# =================================================

@router.post("/upload")
async def upload_training_sample(

    image:UploadFile = File(...),

    product_id:str = Form(...),

    label:str = Form(...),

    notes:str = Form("")

):


    filename = f"{uuid.uuid4()}.jpg"


    file_path = UPLOAD_DIR / filename



    with open(file_path,"wb") as buffer:

        shutil.copyfileobj(
            image.file,
            buffer
        )



    DATASET.append({

        "id":
        str(uuid.uuid4()),


        "product_id":
        product_id,


        "label":
        label,


        "notes":
        notes,


        "image":
        f"/uploads/training/{filename}",


        "created_at":
        str(datetime.now())

    })



    MODEL_STATUS["dataset_images"] = len(DATASET)



    return {

        "success":True,

        "message":
        "Training image uploaded",

        "total_images":
        len(DATASET)

    }





# =================================================
# TRAINING SIMULATION
# =================================================

def train_model():


    MODEL_STATUS["status"] = "Training"

    MODEL_STATUS["progress"] = 0



    for step in range(1,6):


        time.sleep(1)



        MODEL_STATUS["progress"] = step * 20



        MODEL_STATUS["accuracy"] = round(
            random.uniform(95,98),
            2
        )


        MODEL_STATUS["loss"] = round(
            random.uniform(0.05,0.12),
            3
        )




    MODEL_STATUS["status"] = "Completed"


    MODEL_STATUS["progress"] = 100


    MODEL_STATUS["latest_model"] = (
        "Industrial_AI_Model_v1.1"
    )


    MODEL_STATUS["last_training"] = (
        str(datetime.now())
    )


    MODEL_STATUS["dataset_images"] = (
        len(DATASET)
    )





# =================================================
# START RETRAINING
# =================================================

@router.post("/start")
def start_training():


    thread = Thread(
        target=train_model
    )


    thread.start()



    return {


        "success":True,


        "message":
        "Retraining started"

    }





# =================================================
# TRAINING STATUS
# =================================================

@router.get("/status")
def training_status():

    return MODEL_STATUS





# =================================================
# ANALYTICS MODEL CARD
# =================================================

@router.get("/model-status")
def model_status():

    return {


        "current_model":
        MODEL_STATUS["current_model"],


        "latest_model":
        MODEL_STATUS["latest_model"],


        "status":
        MODEL_STATUS["status"],


        "accuracy":
        MODEL_STATUS["accuracy"],


        "loss":
        MODEL_STATUS["loss"],


        "dataset_images":
        MODEL_STATUS["dataset_images"],


        "last_training":
        MODEL_STATUS["last_training"]

    }





# =================================================
# DATASET
# =================================================

@router.get("")
def dataset():

    return {


        "count":
        len(DATASET),


        "images":
        DATASET

    }
