from app import app, models, db


sql = "DELETE FROM AttendGame"
db.session.execute(sql)
db.session.commit()

sql = "DELETE FROM Game"
db.session.execute(sql)
db.session.commit()