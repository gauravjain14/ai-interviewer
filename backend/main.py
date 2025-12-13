import os
from typing import Any, Dict, List, Optional

from fastapi import Depends, FastAPI, Header, HTTPException, status
from jose import JWTError, jwt
from pydantic import BaseModel, BaseSettings, Field, validator
from supabase import Client, create_client


class AppSettings(BaseSettings):
    supabase_url: str = Field(..., env="SUPABASE_URL")
    supabase_anon_key: str = Field(..., env="SUPABASE_ANON_KEY")
    supabase_service_role_key: str = Field(..., env="SUPABASE_SERVICE_ROLE_KEY")
    jwt_secret: str = Field(..., env="SUPABASE_JWT_SECRET")
    jwt_algorithm: str = Field("HS256")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


class Membership(BaseModel):
    user_id: str
    group_id: Optional[int] = None


class GroupCreate(BaseModel):
    name: str
    bot_persona_id: int
    members: List[Membership]

    @validator("members")
    def at_least_three_members(cls, value: List[Membership]) -> List[Membership]:
        if len(value) < 3:
            raise ValueError("Groups must have at least three members")
        return value


class Group(BaseModel):
    id: int
    name: str
    bot_persona_id: int
    members: List[Membership]


class Persona(BaseModel):
    id: int
    name: str
    description: Optional[str] = None


class SupabaseService:
    def __init__(self, client: Client):
        self.client = client

    def bootstrap(self) -> Dict[str, str]:
        return {
            "supabase_url": self.client.supabase_url,
            "supabase_anon_key": self.client.supabase_key,
        }

    def create_group(self, group: GroupCreate) -> Group:
        group_payload = {"name": group.name, "bot_persona_id": group.bot_persona_id}
        group_response = self.client.table("Groups").insert(group_payload).execute()
        if not group_response.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create group",
            )
        group_id = group_response.data[0]["id"]
        membership_payload = [
            {"user_id": member.user_id, "group_id": group_id}
            for member in group.members
        ]
        membership_response = (
            self.client.table("Memberships").insert(membership_payload).execute()
        )
        if membership_response.error:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to attach memberships",
            )
        return Group(
            id=group_id,
            name=group.name,
            bot_persona_id=group.bot_persona_id,
            members=group.members,
        )

    def list_groups(self) -> List[Group]:
        response = (
            self.client.table("Groups")
            .select("*, Memberships:user_id")
            .execute()
        )
        if response.error:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch groups",
            )

        groups: List[Group] = []
        for item in response.data:
            members = [
                Membership(user_id=membership["user_id"], group_id=item["id"])
                for membership in item.get("Memberships", [])
            ]
            groups.append(
                Group(
                    id=item["id"],
                    name=item["name"],
                    bot_persona_id=item.get("bot_persona_id"),
                    members=members,
                )
            )
        return groups

    def get_persona(self, persona_id: int) -> Persona:
        response = (
            self.client.table("Personas")
            .select("id, name, description")
            .eq("id", persona_id)
            .single()
            .execute()
        )
        if response.error:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Persona not found",
            )
        data = response.data
        return Persona(id=data["id"], name=data["name"], description=data.get("description"))


def build_supabase_service() -> SupabaseService:
    settings = AppSettings()
    client = create_client(settings.supabase_url, settings.supabase_service_role_key)
    return SupabaseService(client)


def verify_jwt(
    authorization: str = Header(..., description="Bearer token from Supabase"),
    settings: AppSettings = Depends(AppSettings),
) -> Dict[str, Any]:
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        return payload
    except JWTError as exc:  # pragma: no cover - pass-through for runtime
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc


app = FastAPI(title="AI Interviewer Backend")
supabase_service = build_supabase_service()


@app.get("/auth/bootstrap")
def auth_bootstrap() -> Dict[str, str]:
    """
    Provide Supabase connection info to the frontend.
    """
    return supabase_service.bootstrap()


@app.post("/groups", response_model=Group, dependencies=[Depends(verify_jwt)])
def create_group(group: GroupCreate) -> Group:
    return supabase_service.create_group(group)


@app.get("/groups", response_model=List[Group], dependencies=[Depends(verify_jwt)])
def list_groups() -> List[Group]:
    return supabase_service.list_groups()


@app.get("/personas/{persona_id}", response_model=Persona, dependencies=[Depends(verify_jwt)])
def persona_lookup(persona_id: int) -> Persona:
    return supabase_service.get_persona(persona_id)


if __name__ == "__main__":  # pragma: no cover
    import uvicorn

    port = int(os.environ.get("PORT", "8000"))
    uvicorn.run("backend.main:app", host="0.0.0.0", port=port, reload=True)
