from sqlalchemy.sql import select


cte = select([]).cte()

reveal_type(cte)
