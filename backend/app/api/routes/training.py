from fastapi import APIRouter, UploadFile, File, Form
from pathlib import Path
import shutil
import uuid
from datetime import datetime


router = APIRouter(
    prefix="/api/training",
    tags=["Training"]
)


UPLOAD_DIR = Path("uploads/training")
UPLOAD_DIR.mkdir(
    parents=True,
    exist_ok=True
)


DATASET = []


PRODUCTS = []


TRAINING_STATUS = {

    "model_name":"No Model",

    "status":"Idle",

    "progress":0,

    "accuracy":0,

    "loss":0,

    "dataset_images":0

}



# ==========================
# CREATE PRODUCT
# ==========================

@router.post("/product")
def create_product(
    name:str = Form(...),
    code:str = Form(...)
):

    product={

        "id":str(uuid.uuid4()),

        "name":name,

        "code":code,

        "created_at":
        str(datetime.now())

    }


    PRODUCTS.append(product)


    return product




# ==========================
# UPLOAD TRAINING IMAGE
# ==========================

@router.post("/upload")
async def upload_training_sample(

    image:UploadFile = File(...),

    product_id:str = Form(...),

    label:str = Form(...),

    notes:str = Form("")

):


    filename=f"{uuid.uuid4()}.jpg"


    path=UPLOAD_DIR / filename


    with open(path,"wb") as buffer:

        shutil.copyfileobj(
            image.file,
            buffer
        )



    DATASET.append({

        "id":str(uuid.uuid4()),

        "product_id":product_id,

        "label":label,

        "notes":notes,

        "image":
        f"/uploads/training/{filename}"

    })


    return {

        "success":True,

        "total_images":
        len(DATASET)

    }





# ==========================
# START FAKE TRAINING
# ==========================

@router.post("/start")
def start_training():


    TRAINING_STATUS.update({

        "model_name":
        "Industrial_AI_Model_v1",

        "status":
        "Training",

        "progress":50,

        "accuracy":94.5,

        "loss":0.08,

        "dataset_images":
        len(DATASET)

    })


    return TRAINING_STATUS




# ==========================
# TRAINING STATUS
# ==========================

@router.get("/status")
def training_status():

    return TRAINING_STATUS



# ==========================
# DATASET
# ==========================

@router.get("")
def dataset():

    return {

        "images":DATASET,

        "count":
        len(DATASET)

    }
