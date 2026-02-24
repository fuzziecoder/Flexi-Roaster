"""Governance APIs for registering metadata in Atlas and Amundsen."""
from fastapi import APIRouter, Depends

from backend.api.governance import GovernanceService
from backend.api.schemas import GovernanceDatasetRegistration, GovernanceRegistrationResponse
from backend.api.security import AuthContext, require_scopes

router = APIRouter(prefix="/governance", tags=["governance"])
service = GovernanceService()


@router.post(
    "/datasets",
    response_model=GovernanceRegistrationResponse,
    summary="Register dataset metadata in Atlas and Amundsen",
)
async def register_dataset(
    registration: GovernanceDatasetRegistration,
    auth: AuthContext = Depends(require_scopes(["governance:write"])),
):
    result = await service.register_dataset(registration.model_dump())
    return GovernanceRegistrationResponse(
        message="Governance registration processed",
        dataset=registration,
        atlas_status=result.atlas_status,
        amundsen_status=result.amundsen_status,
        requested_by=auth.subject,
    )
