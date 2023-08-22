#!/usr/bin/env python3

from models import db, Activity, Camper, Signup
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


class Index(Resource):
    def get(self):
        return "Hello"


api.add_resource(Index, "/")


class CamperAll(Resource):
    def get(self):
        campers = [c.to_dict() for c in Camper.query.all()]
        res = make_response(jsonify(campers), 200)
        return res

    def post(self):
        data = request.get_json()
        try:
            newCamper = Camper(name=data["name"], age=data["age"])
            db.session.add(newCamper)
            db.session.commit()

            return make_response(jsonify(newCamper.to_dict()), 201)
        except:
            return make_response({"errors": ["validation errors"]}, 403)


api.add_resource(CamperAll, "/campers")


class CamperById(Resource):
    def get(self, id):
        camper = Camper.query.filter_by(id=id).first().to_dict()
        if not camper:
            res = make_response({"error": "Camper not found"})
        else:
            res = make_response(jsonify(camper), 200)
        return res

    def patch(self, id):
        camper = Camper.query.filter_by(id=id).first()
        if not camper:
            res = make_response({"error": "Camper not found"})
            return res
        else:
            data = request.get_json()
            try:
                if data["name"]:
                    setattr(camper, "name", data["name"])
                if data["age"]:
                    setattr(camper, "age", data["age"])
                db.session.add(camper)
                db.session.commit()

                return make_response(jsonify(camper.to_dict()), 202)
            except:
                return make_response({"errors": ["validation errors"]}, 403)


api.add_resource(CamperById, "/campers/<int:id>")


class ActivitiesAll(Resource):
    def get(self):
        activities = [a.to_dict() for a in Activity.query.all()]
        return make_response(jsonify(activities), 200)


api.add_resource(ActivitiesAll, "/activities")


class AcivitiesById(Resource):
    def delete(self, id):
        activity = Activity.query.filter_by(id=id).first()
        if activity:
            db.session.delete(activity)
            db.session.commit()

            return make_response({"Message": "Activity has been deleted"}, 204)
        else:
            return make_response({"Error": "404: Activity not found"}, 404)


api.add_resource(AcivitiesById, "/activities/<int:id>")


class Signups(Resource):
    def post(self):
        data = request.get_json()
        if data["camper_id"] and data["activity_id"] and data["time"]:
            newSignup = Signup(
                camper_id=data["camper_id"],
                activity_id=data["activity_id"],
                time=data["time"],
            )
            db.session.add(newSignup)
            db.session.commit()

            return make_response(jsonify(newSignup.to_dict()), 201)
        else:
            return make_response({"errors": ["validation errors"]}, 403)


api.add_resource(Signups, "/signups")


if __name__ == "__main__":
    app.run(port=5555, debug=True)
