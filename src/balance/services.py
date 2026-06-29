from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import DECIMAL, select
from datetime import datetime, timezone
from src.balance.models import BalanceModel


async def adjust_user_balance(session: AsyncSession, user_id: str, amount_delta: DECIMAL):
  """
    Adjusts  the user's balance by a specific delta (+ve or -ve).
    Uses row-level locking (SELECT FOR UPDATE) to ensure race-condition safety.
  """

  # Fetch the balance row an lock it for this transaction.
  stmt = select(BalanceModel).where(BalanceModel.user_id == user_id).with_for_update()
  balance = await session.scalar(stmt)

  if not balance:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User balance record not found. Please create a balance profile first.")
  
  # Apply the delta change
  balance.amount += amount_delta
  balance.updated_at = datetime(timezone.utc)