import random

from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

##Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


##Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)

    def to_json_dict(self):
        # dictionary = {}
        #
        # for column in self.__table__.columns:
        #     dictionary[column.name] = getattr(self, column.name)
        # return dictionary

        ## using a comprehension dictionary
        # return {new_key: new_value for item in list if test}
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}



@app.route("/")
def home():
    """This Home page"""
    return render_template("index.html")
    

## HTTP GET - Read Record
@app.route("/random")
def get_random_cafe():
    """This function gives a random cafe"""

    cafes = db.session.query(Cafe).all()
    random_cafe = random.choice(cafes)

    return jsonify(cafe=random_cafe.to_json_dict())

@app.route("/all")
def get_all_cafe():
    """This function gives all cafes"""

    all_cafes = db.session.query(Cafe).all()
    # cafes = []
    # for cafe in all_cafes:
    #     cafe_item = cafe.to_json_dict()
    #     cafes.append(cafe_item)

    return jsonify(cafes=[cafe.to_json_dict() for cafe in all_cafes])

@app.route("/search")
def get_cafes_at_location():
    """This function gives cafes at certain location"""

    query_location = request.args.get('loc')
    cafes = db.session.query(Cafe).all()
    cafes_at_location = [cafe.to_json_dict() for cafe in cafes if cafe.location == query_location]
    if cafes_at_location != "":
        return jsonify(cafes=cafes_at_location)
    else:
        return jsonify(error={'Not found': "Sorry,we don't have a cafe at that location"})

## HTTP POST - Create Record
@app.route("/add", methods=['POST'])
def post_new_cafe():
    """This function Post new cafes"""

    api_key = request.args.get("api_key")
    if api_key == 'TopSecretAPIKey':
        try:
            new_cafe = Cafe(
                name=request.form.get("cafe_name"),
                # name=request.args.get("name"),
                map_url=request.form.get("map_url"),
                img_url=request.form.get("img_url"),
                location=request.form.get("loc"),
                seats=request.form.get("seats"),

                has_sockets=int(bool(request.form.get("sockets"))),
                has_toilet=int(bool(request.form.get("toilet"))),
                has_wifi=int(bool(request.form.get("wifi"))),
                can_take_calls=int(bool(request.form.get("calls"))),

                coffee_price=request.form.get("coffee_price"), # This null able, it is optional to type in the form
                # coffee_price=request.args.get("coffee_price"),
            )

            db.session.add(new_cafe)  # Write to database
            db.session.commit()
            return {"response": {"success": "Successfully added the new cafe."}}, 200

        except Exception as error:
            return {"response": {"error": "{}".format(error)}}
    else:
        return jsonify(error={"Forbidden": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403


## HTTP PUT/PATCH - Update Record
@app.route("/update-price/<int:cafe_id>", methods=['PATCH'])
def update_cafe(cafe_id):
    """This function update cafes by Patch method, that means only edit certain part or information"""

    new_coffee_price = request.args.get('new_price')
    cafe = db.session.query(Cafe).get(cafe_id)
    if cafe:
        cafe.coffee_price = new_coffee_price
        db.session.commit()
        # Just add the code after the jsonify method. 200 = Ok
        return jsonify(response={"success": "Successfully updated the price."}), 200
    else:
        # 404 = Resource not found
        return jsonify(error={"Not Found": "Sorry a cafe with that id was not found in the database."}), 404


## HTTP DELETE - Delete Record
@app.route("/report-closed/<int:cafe_id>", methods=['DELETE'])
def delete_cafe(cafe_id):
    """This function Delete specific cafe by id"""

    api_key = request.args.get("api_key")
    if api_key == "TopSecretAPIKey":
        cafe = db.session.query(Cafe).get(cafe_id)
        if cafe:
            db.session.delete(cafe)
            db.session.commit()
            return jsonify(response={"success": "Successfully deleted the cafe from the database."}), 200

        else:
            return jsonify(error={"Not Found": "Sorry a cafe with that id was not found in the database."}), 404
    else:
        return jsonify(error={"Forbidden": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403


if __name__ == '__main__':
    app.run(debug=True)
