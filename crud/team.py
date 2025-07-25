from sqlalchemy.orm import Session
from typing import List, Optional
import models
import schemas


def create_team(db: Session, team: schemas.TeamCreate) -> models.Team:
    db_team = models.Team(**team.dict())
    db.add(db_team)
    db.commit()
    db.refresh(db_team)
    return db_team

def get_team(db: Session, team_id: int) -> Optional[models.Team]:
    return db.query(models.Team).filter(models.Team.id == team_id).first()

def get_teams(db: Session, skip: int = 0, limit: int = 100, shop_id: Optional[int] = None) -> List[models.Team]:
    query = db.query(models.Team)
    if shop_id:
        query = query.filter(models.Team.shop_id == shop_id)
    return query.offset(skip).limit(limit).all()

def update_team(db: Session, team_id: int, team: schemas.TeamUpdate) -> Optional[models.Team]:
    db_team = get_team(db, team_id)
    if db_team:
        update_data = team.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_team, field, value)
        db.commit()
        db.refresh(db_team)
    return db_team

def delete_team(db: Session, team_id: int) -> bool:
    db_team = get_team(db, team_id)
    if db_team:
        db.delete(db_team)
        db.commit()
        return True
    return False