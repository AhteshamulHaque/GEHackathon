from app import db

class File(db.Model):
   
   _id = db.Column(db.Integer, primary_key=True)
   key = db.Column(db.String(80), nullable=False, unique=True)
   filename = db.Column(db.String(80), nullable=False)
 
   def __repr__(self):
      return '<File %s>'%self.filename