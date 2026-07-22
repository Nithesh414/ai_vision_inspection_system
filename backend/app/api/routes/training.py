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


# Temporary storage
DATASET = []

PRODUCTS = []



# ==========================================
# MODEL STATUS DISPLAY ONLY
# Inspection uses old model separately
# ==========================================

MODEL_STATUS = {

    "current_model":
    "Industrial_AI_Model_v1.0",

    "latest_model":
    "Industrial_AI_Model_v1.1",

    "status":
    "Completed",

    "accuracy":
    96.5,

    "dataset_images":
    0,

    "last_training":
    "2026-07-22"

}




# ==========================================
# CREATE PRODUCT
# ==========================================

@router.post("/product")
def create_product(
    name: str = Form(...),
    code: str = Form(...)
):

    product = {

        "id": str(uuid.uuid4()),

        "name": name,

        "code": code,

        "created_at": str(datetime.now())

    }


    PRODUCTS.append(product)


    return product





# ==========================================
# GET PRODUCTS
# ==========================================

@router.get("/products")
def get_products():

    return PRODUCTS





# ==========================================
# UPLOAD TRAINING IMAGE
# ==========================================

@router.post("/upload")
async def upload_training_sample(

    image: UploadFile = File(...),

    product_id: str = Form(...),

    label: str = Form(...),

    notes: str = Form("")

):


    filename = f"{uuid.uuid4()}.jpg"


    file_path = UPLOAD_DIR / filename



    with open(file_path, "wb") as buffer:

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



    # update image count

    MODEL_STATUS["dataset_images"] = len(DATASET)



    return {

        "success": True,

        "message":
        "Training image uploaded successfully",

        "total_images":
        len(DATASET)

    }





# ==========================================
# ANALYTICS MODEL CARD
# ==========================================

@router.get("/model-status")
def model_status():

    return MODEL_STATUS





# ==========================================
# DATASET VIEW
# ==========================================

@router.get("")
def dataset():

    return {

        "count":
        len(DATASET),

        "images":
        DATASET

    }
