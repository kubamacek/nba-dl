from blog import db

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(20), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False)
    text = db.Column(db.UnicodeText, nullable=False)

    def __repr__(self):
        return "Post - {}".format(self.date_posted.strftime('%Y-%m-%d'))