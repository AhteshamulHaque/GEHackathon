from app import db

class File(db.Model):
   
   _id = db.Column(db.Integer, primary_key=True)
   key = db.Column(db.String(80), nullable=False, unique=True)
   filename = db.Column(db.String(80), nullable=False)
   _date = db.relationship('Date', backref='key', lazy='dynamic')
   PersonName = db.relationship('PersonName', backref='key', lazy='dynamic')
   adharCard = db.relationship('AdharCard', backref='key', lazy='dynamic')
   drivingLicense = db.relationship('DrivingLicense', backref='key', lazy='dynamic')
 
   def __repr__(self):
      return '<File %s>'%self.filename


class Date(db.Model):
   _id = db.Column(db.Integer, primary_key=True)
   date = db.Column(db.String(15), nullable=False)
   start_index = db.Column(db.Integer, nullable=False)
   end_index = db.Column(db.Integer, nullable=False)
   key_id = db.Column(db.Integer, db.ForeignKey('file.key'))

   def __repr__(self):
      return '<Date %s(%d, %d)>'%(self.date, self.start_index, self.end_index)
   
   
class PersonName(db.Model):
   _id = db.Column(db.Integer, primary_key=True)
   name = db.Column(db.String(40), nullable=False)
   start_index = db.Column(db.Integer, nullable=False)
   end_index = db.Column(db.Integer, nullable=False)
   key_id = db.Column(db.Integer, db.ForeignKey('file.key'),
        nullable=False)

   def __repr__(self):
      return '<Person %s(%d, %d)>'%(self.name, self.start_index, self.end_index)


class AdharCard(db.Model):
   _id = db.Column(db.Integer, primary_key=True)
   adhar_no = db.Column(db.String(40), nullable=False)
   start_index = db.Column(db.Integer, nullable=False)
   end_index = db.Column(db.Integer, nullable=False)
   key_id = db.Column(db.Integer, db.ForeignKey('file.key'),
        nullable=False)

   def __repr__(self):
      return '<AdharCard Number: %s(%d, %d)>'%(self.adhar_no, self.start_index, self.end_index)


class DrivingLicense(db.Model):
   _id = db.Column(db.Integer, primary_key=True)
   license_no = db.Column(db.String(40), nullable=False)
   start_index = db.Column(db.Integer, nullable=False)
   end_index = db.Column(db.Integer, nullable=False)
   key_id = db.Column(db.Integer, db.ForeignKey('file.key'),
        nullable=False)
   
   def __repr__(self):
      return '<License Number: %s(%d, %d)>'%(self.license_no, self.start_index, self.end_index)
