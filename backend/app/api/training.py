from fastapi import APIRouter, UploadFile, File, Form
import shutil
import uuid
import random
import time
from pathlib import Path
from threading import Thread
from datetime import datetime


router = APIRouter(
    prefix="/api/training",
    tags=["Training"]
)


# ===============================
# Training Image Storage
# ===============================

UPLOAD_DIR = Path("uploads/training")

UPLOAD_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ===============================
# Fake Dataset Storage
# ===============================

DATASET = []


# ===============================
# Global Model Status
# Shared with Analytics + Training UI
# ===============================

training_status = {

    "model_name": "wheel_classifier",

    "model_version": "v1.0",

    "status": "Idle",

    "running": False,

    "completed": False,

    "progress": 0,

    "epoch": 0,

    "total_epochs": 10,

    "accuracy": 94.5,

    "loss": 0.12,

    "dataset_images": 0,

    "last_training": None

}



# ==================================================
# Upload Training Dataset Image
# ==================================================

@router.post("/upload")
async def upload_training_sample(

    image: UploadFile = File(...),

    product_id: str = Form(...),

    label: str = Form(...),

    notes: str = Form("")

):


    extension = (
        Path(image.filename).suffix
        or ".jpg"
    )


    filename = (
        f"{uuid.uuid4()}{extension}"
    )


    file_path = (
        UPLOAD_DIR / filename
    )


    with open(
        file_path,
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

        "image_url":
        f"/uploads/training/{filename}",

        "created_at":
        datetime.now().isoformat()

    })


    # update dataset count

    training_status["dataset_images"] = len(DATASET)



    return {

        "success": True,

        "message":
        "Training image uploaded",

        "total_images":
        len(DATASET)

    }





# ==================================================
# View Dataset
# ==================================================

@router.get("/dataset")
def list_dataset():


    return {

        "total_images":
        len(DATASET),

        "dataset":
        DATASET

    }





# ==================================================
# Fake Training Engine
# ==================================================

def fake_training_process():


    training_status["running"] = True

    training_status["completed"] = False


    training_status["status"] = (
        "Preparing Dataset"
    )


    training_status["progress"] = 10



    time.sleep(2)



    for epoch in range(1,11):


        training_status["status"] = (
            "Training Model"
        )


        training_status["epoch"] = epoch


        training_status["progress"] = (
            epoch * 10
        )



        training_status["accuracy"] = round(

            random.uniform(
                94,
                99
            ),

            2

        )



        training_status["loss"] = round(

            random.uniform(
                0.05,
                0.20
            ),

            3

        )


        time.sleep(1)




    training_status["status"] = (
        "Validation"
    )


    training_status["progress"] = 90


    time.sleep(2)




    training_status["status"] = (
        "Completed"
    )


    training_status["progress"] = 100


    training_status["running"] = False


    training_status["completed"] = True



    # fake new model version

    current_version = float(

        training_status["model_version"]
        .replace(
            "v",
            ""
        )

    )


    training_status["model_version"] = (

        f"v{current_version + 0.1:.1f}"

    )


    training_status["last_training"] = (

        datetime.now().isoformat()

    )





# ==================================================
# Start Retraining
# ==================================================

@router.post("/start")
def start_training():


    if training_status["running"]:

        return {

            "success":False,

            "message":
            "Training already running"

        }



    thread = Thread(

        target=fake_training_process

    )


    thread.start()



    return {

        "success":True,

        "message":
        "Fake model training started"

    }





# ==================================================
# Get Training Status
# Used by Training + Analytics
# ==================================================

@router.get("/status")
def training_progress():


    return training_status
