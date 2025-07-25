from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import schemas
import crud
from permissions import team_read, team_create, team_update, team_delete
from databases.database import get_db

router = APIRouter(prefix="/teams", tags=["teams"])

@router.post("/", response_model=schemas.Team)
def create_team(
    team: schemas.TeamCreate,
    db: Session = Depends(get_db),
    current_employee = Depends(team_create)
):
    return crud.create_team(db=db, team=team)

@router.get("/", response_model=List[schemas.Team])
def read_teams(
    skip: int = 0,
    limit: int = 100,
    shop_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_employee = Depends(team_read)
):
    return crud.get_teams(db, skip=skip, limit=limit, shop_id=shop_id)

@router.get("/{team_id}", response_model=schemas.Team)
def read_team(
    team_id: int,
    db: Session = Depends(get_db),
    current_employee = Depends(team_read)
):
    db_team = crud.get_team(db, team_id=team_id)
    if db_team is None:
        raise HTTPException(status_code=404, detail="Team not found")
    return db_team

@router.put("/{team_id}", response_model=schemas.Team)
def update_team(
    team_id: int,
    team: schemas.TeamUpdate,
    db: Session = Depends(get_db),
    current_employee = Depends(team_update)
):
    db_team = crud.update_team(db, team_id=team_id, team=team)
    if db_team is None:
        raise HTTPException(status_code=404, detail="Team not found")
    return db_team

@router.delete("/{team_id}")
def delete_team(
    team_id: int,
    db: Session = Depends(get_db),
    current_employee = Depends(team_delete)
):
    success = crud.delete_team(db, team_id=team_id)
    if not success:
        raise HTTPException(status_code=404, detail="Team not found")
    return {"message": "Team deleted successfully"}
