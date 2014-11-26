from app import db

class Word(db.Model):
    __tablename__ = 'word'
    id = db.Column(db.Integer, primary_key = True)
    created_at = db.Column(db.DateTime())
    word = db.Column(db.String(64))
    end_of_paragraph = db.Column(db.Boolean())
    generated = db.Column(db.Boolean())
    story_id = db.Column(db.Integer, db.ForeignKey('story.id'))

    def get_word(self):
        if self.word not in [',','.',':','?','!', ';']:
            return " " + self.word
        return self.word


class Story(db.Model):
    __tablename__ = 'story'
    id = db.Column(db.Integer, primary_key = True)
    created_at = db.Column(db.DateTime())
    words = db.relationship('Word', backref='story', lazy='dynamic')

    def get_paragraphs(self):
        paragraphs = []
        curr_p = []
        for word in self.words:
            curr_p.append(word.get_word())
            if word.end_of_paragraph:
                paragraphs.append(curr_p)
                curr_p = []
        paragraphs.append(curr_p)

        return [ ''.join(p) for p in paragraphs ]
