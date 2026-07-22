from fastapi import APIRouter, UploadFile, File, Form
from pathlib import Path
import shutil
import uuid
import time
import random
from datetime import datetime
from threading import Thread

from app.db.session import SessionLocal
from app.models.models import ModelVersion


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



# ==========================
# GLOBAL MODEL STATUS
# ==========================

TRAINING_STATUS = {


    "model_name":
    "No Model",


    "model_version":
    "v0.0",


    "status":
    "Idle",


    "progress":
    0,


    "epoch":
    0,


    "total_epochs":
    10,


    "accuracy":
    0,


    "loss":
    0,


    "dataset_images":
    0,


    "last_training":
    None

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

        "id":
        str(uuid.uuid4()),


        "name":
        name,


        "code":
        code,


        "created_at":
        str(datetime.now())

    }


    PRODUCTS.append(product)


    return product





# ==========================
# PRODUCT LIST
# ==========================

@router.get("/products")
def get_products():

    return PRODUCTS





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


    filename = (
        f"{uuid.uuid4()}.jpg"
    )


    path = (
        UPLOAD_DIR / filename
    )


    with open(
        path,
        "wb"
    ) as buffer:

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


    TRAINING_STATUS["dataset_images"] = len(DATASET)



    return {


        "success":
        True,


        "message":
        "Image saved",


        "total_images":
        len(DATASET)

    }





# ==========================
# TRAINING PROCESS
# ==========================


def fake_training():


    TRAINING_STATUS["status"] = "Preparing Dataset"

    TRAINING_STATUS["progress"] = 10


    time.sleep(2)



    for epoch in range(1,11):


        TRAINING_STATUS["status"] = (
            "Training Model"
        )


        TRAINING_STATUS["epoch"] = epoch


        TRAINING_STATUS["progress"] = (
            epoch * 10
        )


        TRAINING_STATUS["accuracy"] = round(

            random.uniform(
                94,
                99
            ),

            2
        )


        TRAINING_STATUS["loss"] = round(

            random.uniform(
                0.05,
                0.2
            ),

            3
        )


        time.sleep(1)



    TRAINING_STATUS["status"] = "Completed"


    TRAINING_STATUS["progress"] = 100



    TRAINING_STATUS["model_name"] = (
        "Industrial_AI_Model"
    )


    TRAINING_STATUS["model_version"] = (
        "v1.0"
    )


    TRAINING_STATUS["last_training"] = (
        str(datetime.now())
    )






# ==========================
# START TRAINING
# ==========================


@router.post("/start")
def start_training():

    db = SessionLocal()


    new_version = "v1.1"


    model = ModelVersion(

        model_name="Industrial_AI_Model",

        version=new_version,

        accuracy=96.8,

        loss=0.05,

        path="ai_models/weights/model_v1_1.pt",

        active=True

    )


    # deactivate old models

    db.query(ModelVersion).update(
        {
            "active":False
        }
    )


    db.add(model)

    db.commit()

    db.refresh(model)


    TRAINING_STATUS.update({

        "model_name":
        model.model_name,

        "status":
        "Completed",

        "progress":
        100,

        "accuracy":
        model.accuracy,

        "loss":
        model.loss,

        "dataset_images":
        len(DATASET)

    })


    db.close()


    return {

        "success":True,

        "model_version":
        new_version,

        "accuracy":
        model.accuracy

    }

# ==========================
# STATUS
# ==========================


@router.get("/status")
def get_training_status():


    return TRAINING_STATUS






# ==========================
# DATASET
# ==========================


@router.get("")
def dataset():


    return {


        "images":
        DATASET,


        "count":
        len(DATASET)

    }
