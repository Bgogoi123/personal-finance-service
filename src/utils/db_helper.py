from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError


async def get_or_create(
    session: AsyncSession,
    model,
    user_id: str,
    name: str,
    name_field: str = "name",
    extra_defaults: dict | None = None,

):
    """
    Looks up a row by case-insensitive name match (scoped to user_id).
    Creates it (with extra_defaults for any other required columns) if missing.
    Returns the row's id.
    """
    normalized = name.strip()

    stmt = select(model).where(
        model.user_id == user_id,
        func.lower(getattr(model, name_field)) == normalized.lower(),
    )
    result = await session.execute(stmt)
    existing = result.scalar_one_or_none()

    if existing:
        return existing.id

    new_row = model(**{name_field: normalized,
                    "user_id": user_id, **extra_defaults})
    session.add(new_row)
    try:
        await session.flush()
    except IntegrityError:
        await session.rollback()
        result = await session.execute(stmt)
        existing = result.scalar_one_or_none()
        if existing:
            return existing.id
        raise

    return new_row.id
