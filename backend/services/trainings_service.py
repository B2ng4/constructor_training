from typing import List

from repositories.trainings_repository import TrainingRepository

from schemas.trainings import TrainingCreate, TrainingResponse, TrainingDetailResponse, TrainingUpdate




class TrainingsService:
    def __init__(self, repo: TrainingRepository):
        self.repo = repo

    async def create_training(self, Training_data: TrainingCreate)->bool:
        return await self.repo.create(Training_data)

    async def get_training(self, Training_id: int) -> TrainingResponse:
        Training = await self.repo.get_by_id(Training_id)
        if not Training:
            return None
        return TrainingResponse.model_validate(Training)

    async def get_training_with_details(self, Training_id: int) -> TrainingDetailResponse:
        Training_data = await self.repo.get_with_type_details(Training_id)
        if not Training_data:
            return None
        Training_response = TrainingResponse.model_validate(Training_data["Training"])

        return TrainingDetailResponse(
            **Training_response.model_dump(),
            type_name=Training_data["type_name"],
            type_data=Training_data["type_data"]
        )

    async def get_trainings(self, skip: int = 0, limit: int = 100) -> List[TrainingResponse]:
        Trainings = await self.repo.get_all(skip, limit)
        return [TrainingResponse.model_validate(Training) for Training in Trainings]

    async def update_training(self, Training_id: int, Training_data: TrainingUpdate) -> TrainingResponse:
        Training = await self.repo.update(Training_id, Training_data)
        if not Training:
            return None
        return TrainingResponse.model_validate(Training)

    async def delete_training(self, Training_id: int) -> bool:
        return await self.repo.delete(Training_id)