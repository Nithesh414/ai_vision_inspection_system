from fastapi import APIRouter
import random
import time

router = APIRouter(
    prefix="/api/training",
    tags=["Training Engine"]
)

training_status = {
    "running": False,
    "progress": 0,
    "epoch": 0,
    "loss": 0,
    "accuracy": 0,
    "completed": False,
    "version": "v1.0"
}


@router.post("/start")
def start_training():

    training_status["running"] = True
    training_status["completed"] = False

    for epoch in range(1, 11):

        time.sleep(0.6)

        training_status["epoch"] = epoch
        training_status["progress"] = epoch * 10
        training_status["loss"] = round(random.uniform(0.05,0.4),3)
        training_status["accuracy"] = round(random.uniform(88,99),2)

    training_status["running"] = False
    training_status["completed"] = True
    training_status["version"] = "v1.1"

    return {
        "success":True
    }


@router.get("/status")
def get_status():

    return training_status
