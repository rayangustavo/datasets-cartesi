from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, DecimalField, RadioField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired, NumberRange
import requests
import json


def hex2str(hex):
    return bytes.fromhex(hex[2:]).decode("utf-8")

def str2hex(str):
    return "0x" + str.encode("utf-8").hex()

class InsertForm(FlaskForm):
    age = IntegerField("Age", validators=[DataRequired(), NumberRange(min=0, max=100)], render_kw={'class':'option'})
    sex = SelectField("Sex", choices=["Male", "Female"], validators=[DataRequired()], render_kw={'class':'option'})
    bmi = DecimalField("BMI", validators=[DataRequired(), NumberRange(min=0, max=100)], render_kw={'class':'option'})
    children = IntegerField("Children", validators=[DataRequired()], render_kw={'class':'option'})
    smoker = SelectField("Smoker", choices=["Yes", "No"], validators=[DataRequired()], render_kw={'class':'option'})
    region = SelectField("Region", choices=["Northeast", "Northwest", "Southeast", "Southwest"], validators=[DataRequired()], render_kw={'class':'option'})
    charges = DecimalField("Charges", validators=[DataRequired()], render_kw={'class':'option'})
    submit = SubmitField("Submit")

    def insert_statement(form):
        data = []
        for field in form:
            data.append(str(field.data).lower())
        statement = f"INSERT INTO Medical VALUES ({str(data[:-2])[1:-1]})"
        return str(statement)

class SelectForm(FlaskForm):   
    age = IntegerField("age", validators=[NumberRange(min=0, max=100)], render_kw={'class':'option'})
    sex = SelectField("sex", choices=["-", "Male", "Female"], render_kw={'class':'option'})
    bmi = DecimalField("bmi", validators=[NumberRange(min=0, max=100)], render_kw={'class':'option'})
    children = IntegerField("children", render_kw={'class':'option'}) # when is 0, dont work (TO DO)
    smoker = SelectField("smoker", choices=["-", "Yes", "No"], render_kw={'class':'option'})
    region = SelectField("region", choices=["-", "Northeast", "Northwest", "Southeast", "Southwest"], render_kw={'class':'option'})
    charges = DecimalField("charges", render_kw={'class':'option'})

    submit = SubmitField("Submit")

    def select_statement(form):
        statement = "SELECT * FROM Medical" 
        data = []
        if form.sex.data == "-":
            form.sex.data = None
        if form.smoker.data == "-":
            form.smoker.data = None
        if form.region.data == "-":
            form.region.data = None
        for field in form:
            if field.data:
                data_field = (field.name, str(field.data).lower())
                data.append(data_field)
                print(data)
        data = data[:-2]
        if(data):
            statement += " WHERE "
            for d in data:
                statement += d[0] + "=" + "'" + d[1] + "'" + " AND "
            statement = statement[0:-5]
        return str(statement)

    def inspect(form, statement):
        report = requests.get(f"http://localhost:5005/inspect/{statement}")
        # report = report.json()["reports"]
        if(report.json()["reports"] == []):
            return 0
        else:
            payload = hex2str(report.json()["reports"][0]["payload"])
            payload = json.loads(payload)
            return payload

class UpdateForm(FlaskForm):
    attribute = SelectField("Attribute", choices=["Age", "Sex", "BMI", "Children", "Smoker", "Region", "Charges"], validators=[DataRequired()], render_kw={'class':'option'})
    new_value = StringField("New Value", validators=[DataRequired()], render_kw={'class':'option'})
    from_attribute = SelectField("From Attribute", choices=["Age", "Sex", "BMI", "Children", "Smoker", "Region", "Charges"], validators=[DataRequired()], render_kw={'class':'option'})
    from_value = StringField("From Value", validators=[DataRequired()], render_kw={'class':'option'})
    submit = SubmitField("Submit")

    def update_statement(form):
        statement = f"UPDATE Medical SET {(form.attribute.data).lower()}='{(form.new_value.data).lower()}' WHERE {(form.from_attribute.data).lower()}='{(form.from_value.data).lower()}'" 
        return str(statement)

    def inspect(form):
        statement = f"SELECT * FROM Medical WHERE {(form.from_attribute.data).lower()}='{(form.from_value.data).lower()}'"
        report = requests.get(f"http://localhost:5005/inspect/{statement}")
        if(report.json()["reports"] == []):
            return 0
        else:
            payload = hex2str(report.json()["reports"][0]["payload"])
            payload = json.loads(payload)
            return payload


class DeleteForm(FlaskForm):    
    age = IntegerField("Age", validators=[NumberRange(min=0, max=100)], render_kw={'class':'option'})
    sex = SelectField("Sex", choices=["-", "Male", "Female"], render_kw={'class':'option'})
    bmi = DecimalField("BMI", validators=[NumberRange(min=0, max=100)], render_kw={'class':'option'})
    children = IntegerField("Children", render_kw={'class':'option'})
    smoker = SelectField("Smoker", choices=["-", "Yes", "No"], render_kw={'class':'option'})
    region = SelectField("Region", choices=["-", "Northeast", "Northwest", "Southeast", "Southwest"], render_kw={'class':'option'})
    charges = DecimalField("Charges", render_kw={'class':'option'})
    submit = SubmitField("Submit")

    def delete_statement(form):
        form.submit.data = None
        statement = "DELETE FROM Medical" 
        data = []
        for field in form:
            if field.data:
                if field.data != '-':
                    data_field = (field.name, str(field.data).lower())
                    data.append(data_field)
        data = data[:-1]
        if(data):
            statement += " WHERE "
            for d in data:
                statement += d[0] + "=" + "'" + d[1] + "'" + " AND "
            statement = statement[0:-5]
        return str(statement)

    def inspect(form):
        statement = "SELECT * FROM Medical" 
        data = []
        if form.sex.data == "-":
            form.sex.data = None
        if form.smoker.data == "-":
            form.smoker.data = None
        if form.region.data == "-":
            form.region.data = None
        for field in form:
            if field.data:
                data_field = (field.name, str(field.data).lower())
                data.append(data_field)
        data = data[:-1]
        if(data):
            statement += " WHERE "
            for d in data:
                statement += d[0] + "=" + "'" + d[1] + "'" + " AND "
            statement = statement[0:-5]
        statement = str(statement)
        report = requests.get(f"http://localhost:5005/inspect/{statement}")
        if(report.json()["reports"] == []):
            return 0
        else:
            payload = hex2str(report.json()["reports"][0]["payload"])
            payload = json.loads(payload)
            return payload