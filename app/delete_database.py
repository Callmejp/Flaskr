from app import app, models, db

posts = models.Post.query.all()
for p in posts:
    db.session.delete(p)

db.session.commit()