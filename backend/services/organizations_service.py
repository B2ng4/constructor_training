import secrets
import string
from typing import List

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from models.organizations import Organization, OrganizationEmployee
from models.users import UserRole
from models.trainings import Training
from repositories.organizations_repository import OrganizationsRepository
from repositories.trainings_repository import TrainingRepository
from core.config import public_passage_link
from repositories.users_repository import UserRepository
from schemas.organizations import (
    AssignedTrainingResponse,
    GeneratedAccountResponse,
    OrganizationCreate,
    OrganizationDetailResponse,
    OrganizationEmployeeBulkCreate,
    OrganizationEmployeeCreate,
    OrganizationEmployeeResponse,
    OrganizationListResponse,
    OrganizationTrainingBrief,
    OrganizationUpdate,
    ProvisionAccountsRequest,
    ProvisionAccountsResponse,
    ProvisionedAccountResponse,
)
from services.temp_employee_accounts_service import (
    TempEmployeeAccountsService,
    temp_account_expires_at,
)
from utils.security import get_password_hash


def _split_full_name(full_name: str) -> tuple[str, str]:
    parts = (full_name or "").strip().split()
    if not parts:
        return "Сотрудник", ""
    if len(parts) == 1:
        return parts[0], ""
    return parts[0], " ".join(parts[1:])


def _generate_temp_password(length: int = 10) -> str:
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


def _generate_login_id(length: int = 8) -> str:
    alphabet = string.ascii_lowercase + string.digits
    suffix = "".join(secrets.choice(alphabet) for _ in range(length))
    return f"emp_{suffix}"


class OrganizationsService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repo = OrganizationsRepository(session)
        self.trainings_repo = TrainingRepository(session)
        self.users_repo = UserRepository(session)
        self.temp_accounts = TempEmployeeAccountsService(session)

    async def _cleanup_expired_temp_accounts(self) -> None:
        await self.temp_accounts.cleanup_expired()

    async def _require_org_owner(self, org_id: int, owner_id: int) -> Organization:
        org = await self.repo.get_by_id(org_id)
        if not org:
            raise HTTPException(status_code=404, detail="Организация не найдена")
        if org.owner_id != owner_id:
            raise HTTPException(status_code=403, detail="Нет доступа к организации")
        return org

    async def _require_owned_training(self, training_uuid, owner_id):
        training = await self.trainings_repo.get_by_uuid(training_uuid)
        if not training:
            raise HTTPException(status_code=404, detail="Тренинг не найден")
        if training.creator_id != owner_id:
            raise HTTPException(status_code=403, detail="Тренинг не принадлежит вам")
        return training

    async def _maybe_set_employee_role(self, user) -> None:
        if user.role == UserRole.EMPLOYEE:
            return
        training_count = await self.session.scalar(
            select(func.count()).select_from(Training).where(Training.creator_id == user.id)
        )
        org_owner_count = await self.session.scalar(
            select(func.count()).select_from(Organization).where(Organization.owner_id == user.id)
        )
        if (training_count or 0) == 0 and (org_owner_count or 0) == 0:
            user.role = UserRole.EMPLOYEE

    def _training_brief(self, training) -> OrganizationTrainingBrief:
        link = None
        pubs = getattr(training, "publications", None) or []
        active = next((p for p in pubs if getattr(p, "is_active", False)), None)
        if active:
            link = public_passage_link(active.access_token)
        return OrganizationTrainingBrief(
            uuid=training.uuid,
            title=training.title,
            publish=bool(training.publish),
            public_link=link,
        )

    async def create_organization(
        self, data: OrganizationCreate, owner_id: int
    ) -> OrganizationListResponse:
        org = Organization(name=data.name.strip(), owner_id=owner_id)
        created = await self.repo.create(org)
        await self.session.commit()
        return OrganizationListResponse(
            id=created.id,
            name=created.name,
            created_at=created.created_at,
            employees_count=0,
            trainings_count=0,
        )

    async def list_organizations(self, owner_id: int) -> List[OrganizationListResponse]:
        orgs = await self.repo.list_by_owner(owner_id)
        return [
            OrganizationListResponse(
                id=o.id,
                name=o.name,
                created_at=o.created_at,
                employees_count=len(o.employees or []),
                trainings_count=len(o.trainings or []),
            )
            for o in orgs
        ]

    async def get_organization(
        self, org_id: int, owner_id: int
    ) -> OrganizationDetailResponse:
        await self._require_org_owner(org_id, owner_id)
        await self._cleanup_expired_temp_accounts()
        org = await self.repo.get_by_id(org_id)
        if not org:
            raise HTTPException(status_code=404, detail="Организация не найдена")
        return OrganizationDetailResponse(
            id=org.id,
            name=org.name,
            created_at=org.created_at,
            trainings=[self._training_brief(t) for t in org.trainings or []],
            employees=[
                OrganizationEmployeeResponse.model_validate(e) for e in org.employees or []
            ],
        )

    async def update_organization(
        self, org_id: int, data: OrganizationUpdate, owner_id: int
    ) -> OrganizationDetailResponse:
        org = await self._require_org_owner(org_id, owner_id)
        if data.name is not None:
            org.name = data.name.strip()
        await self.session.flush()
        await self.session.commit()
        return await self.get_organization(org_id, owner_id)

    async def delete_organization(self, org_id: int, owner_id: int) -> None:
        await self._require_org_owner(org_id, owner_id)
        await self.repo.delete(org_id)
        await self.session.commit()

    async def add_training(self, org_id: int, training_uuid, owner_id: int) -> OrganizationDetailResponse:
        await self._require_org_owner(org_id, owner_id)
        await self._require_owned_training(training_uuid, owner_id)
        await self.repo.add_training(org_id, training_uuid)
        await self.session.commit()
        return await self.get_organization(org_id, owner_id)

    async def remove_training(
        self, org_id: int, training_uuid, owner_id: int
    ) -> OrganizationDetailResponse:
        await self._require_org_owner(org_id, owner_id)
        await self.repo.remove_training(org_id, training_uuid)
        await self.session.commit()
        return await self.get_organization(org_id, owner_id)

    async def add_employee(
        self, org_id: int, data: OrganizationEmployeeCreate, owner_id: int
    ) -> OrganizationEmployeeResponse:
        await self._require_org_owner(org_id, owner_id)
        created = await self.repo.add_employees_bulk(
            org_id,
            [
                {
                    "email": data.email.lower().strip(),
                    "full_name": data.full_name.strip(),
                    "position": (data.position or "").strip() or None,
                }
            ],
        )
        await self.session.commit()
        return OrganizationEmployeeResponse.model_validate(created[0])

    async def add_employees_bulk(
        self, org_id: int, data: OrganizationEmployeeBulkCreate, owner_id: int
    ) -> List[OrganizationEmployeeResponse]:
        await self._require_org_owner(org_id, owner_id)
        if not data.employees:
            return []
        rows = [
            {
                "email": e.email.lower().strip(),
                "full_name": e.full_name.strip(),
                "position": (e.position or "").strip() or None,
            }
            for e in data.employees
        ]
        created = await self.repo.add_employees_bulk(org_id, rows)
        await self.session.commit()
        return [OrganizationEmployeeResponse.model_validate(x) for x in created]

    async def delete_employee(
        self, org_id: int, employee_id: int, owner_id: int
    ) -> None:
        await self._require_org_owner(org_id, owner_id)
        ok = await self.repo.delete_employee(org_id, employee_id)
        if not ok:
            raise HTTPException(status_code=404, detail="Сотрудник не найден")
        await self.session.commit()

    async def delete_all_employees(self, org_id: int, owner_id: int) -> int:
        await self._require_org_owner(org_id, owner_id)
        count, user_ids = await self.repo.delete_all_employees(org_id)
        if not count:
            raise HTTPException(status_code=400, detail="Список сотрудников пуст")
        for user_id in user_ids:
            user = await self.users_repo.get_by_id(user_id)
            if user and user.role == UserRole.EMPLOYEE:
                await self.session.delete(user)
        await self.session.commit()
        return count

    async def generate_accounts(
        self, org_id: int, owner_id: int, *, regenerate: bool = False, ttl_days: int
    ) -> List[GeneratedAccountResponse]:
        await self._require_org_owner(org_id, owner_id)
        await self._cleanup_expired_temp_accounts()
        if regenerate:
            pending = await self.repo.list_employees(org_id)
        else:
            pending = await self.repo.employees_pending_accounts(org_id)
        if not pending:
            detail = (
                "Нет сотрудников для перегенерации"
                if regenerate
                else "Нет сотрудников для генерации"
            )
            raise HTTPException(status_code=400, detail=detail)

        expires_at = temp_account_expires_at(ttl_days=ttl_days)
        results: List[GeneratedAccountResponse] = []
        for emp in pending:
            temp_password = _generate_temp_password()
            first_name, last_name = _split_full_name(emp.full_name)
            user = await self.users_repo.find_one_or_none(emp.email.lower().strip())
            if user:
                user.first_name = first_name or user.first_name
                user.last_name = last_name or user.last_name
                user.password = get_password_hash(temp_password)
                await self._maybe_set_employee_role(user)
                if user.role != UserRole.EMPLOYEE:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Email {emp.email} уже занят пользователем с другой ролью",
                    )
                user.expires_at = expires_at
            else:
                user = await self.users_repo.create_user_with_password(
                    email=emp.email,
                    password=temp_password,
                    first_name=first_name,
                    last_name=last_name,
                    role=UserRole.EMPLOYEE,
                    expires_at=expires_at,
                )
            emp.user_id = user.id
            emp.account_generated = True
            emp.account_expires_at = expires_at
            results.append(
                GeneratedAccountResponse(
                    employee_id=emp.id,
                    email=emp.email,
                    full_name=emp.full_name,
                    temp_password=temp_password,
                    account_expires_at=expires_at,
                    ttl_days=ttl_days,
                )
            )

        await self.session.commit()
        return results

    async def _generate_unique_login_id(self) -> str:
        for _ in range(20):
            login_id = _generate_login_id()
            existing = await self.users_repo.find_one_or_none(login_id)
            if not existing:
                return login_id
        raise HTTPException(status_code=500, detail="Не удалось сгенерировать login ID")

    async def provision_accounts(
        self, org_id: int, owner_id: int, data: ProvisionAccountsRequest
    ) -> ProvisionAccountsResponse:
        await self._require_org_owner(org_id, owner_id)
        await self._cleanup_expired_temp_accounts()
        expires_at = temp_account_expires_at(ttl_days=data.ttl_days)
        results: List[ProvisionedAccountResponse] = []

        for slot in data.slots:
            emp = await self.repo.get_employee_by_provision_ref(org_id, slot.provision_ref)
            if not emp:
                emp = await self.repo.create_provision_slot(org_id, slot.provision_ref)

            login_id = emp.login_id or await self._generate_unique_login_id()
            temp_password = _generate_temp_password()
            user = None
            if emp.user_id:
                user = await self.users_repo.get_by_id(emp.user_id)
            if user:
                user.password = get_password_hash(temp_password)
                user.expires_at = expires_at
                if user.role != UserRole.EMPLOYEE:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Login {login_id} уже занят пользователем с другой ролью",
                    )
            else:
                user = await self.users_repo.create_user_with_password(
                    email=login_id,
                    password=temp_password,
                    first_name="Сотрудник",
                    last_name="",
                    role=UserRole.EMPLOYEE,
                    expires_at=expires_at,
                )

            emp.user_id = user.id
            emp.login_id = login_id
            emp.email = login_id
            emp.account_generated = True
            emp.account_expires_at = expires_at
            results.append(
                ProvisionedAccountResponse(
                    provision_ref=slot.provision_ref,
                    slot_id=emp.id,
                    login_id=login_id,
                    temp_password=temp_password,
                    user_id=user.id,
                    account_expires_at=expires_at,
                    ttl_days=data.ttl_days,
                )
            )

        await self.session.commit()
        return ProvisionAccountsResponse(accounts=results)

    async def assigned_trainings_for_user(
        self, user_id: int
    ) -> List[AssignedTrainingResponse]:
        user = await self.users_repo.get_by_id(user_id)
        if user and await self.temp_accounts.cleanup_user_if_expired(user):
            return []
        rows = await self.repo.get_assigned_trainings_for_user(user_id)
        out: List[AssignedTrainingResponse] = []
        seen = set()
        for org, training in rows:
            key = (org.id, training.uuid)
            if key in seen:
                continue
            seen.add(key)
            pub = await self.repo.get_active_publication(training.uuid)
            link = public_passage_link(pub.access_token) if pub else None
            out.append(
                AssignedTrainingResponse(
                    organization_id=org.id,
                    organization_name=org.name,
                    training_uuid=training.uuid,
                    title=training.title,
                    public_link=link,
                )
            )
        return out
