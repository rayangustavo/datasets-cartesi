import logging
import time
from flask import Flask, render_template, request, redirect, flash, url_for
from models.forms import InsertForm, SelectForm, UpdateForm, DeleteForm
from controllers.config import getAddress, getABI
from controllers.query import inspect

app = Flask(__name__)
app.config["SECRET_KEY"] = "secretkey"
app.config["DEBUG"] = True
app.logger.setLevel(logging.INFO)

def hex2str(hex):
    return bytes.fromhex(hex[2:]).decode("utf-8")

def str2hex(str):
    return "0x" + str.encode("utf-8").hex()

@app.route("/")
@app.route("/index")
def index():
    return render_template("index.html")

@app.route('/insert', methods=['GET', 'POST'])
def insert():
    insert_form = InsertForm()
    statement = ''
    rollups_address = getAddress()
    input_abi = getABI()

    if insert_form.validate_on_submit():
        print("eae man")
        statement = str2hex(insert_form.insert_statement())

    return render_template('insert.html', insert_form=insert_form, statement=statement, rollups_address=rollups_address, input_abi=input_abi)

@app.route('/select', methods=['GET', 'POST'])
def select():
    select_form = SelectForm()
    payload_list = select_form.inspect(select_form.select_statement())
    if (payload_list == 0):
        payload_list = 'NOTFOUND'

    return render_template('select.html', select_form=select_form, payload_list=payload_list)


@app.route('/update', methods=['GET', 'POST'])
def update():
    update_form = UpdateForm()
    statement = ''
    rollups_address = getAddress()
    input_abi = getABI()
    payload_list = None

    if update_form.validate_on_submit():
        statement = str2hex(update_form.update_statement())
        payload_list = update_form.inspect()
        if (payload_list == 0):
            payload_list = 'NOTFOUND'

    return render_template('update.html', update_form=update_form, statement=statement, rollups_address=rollups_address, input_abi=input_abi, payload_list=payload_list)


##
# ?????????????
##
# @app.route('/delete', methods=['GET', 'POST'])
# def delete():
#     delete_form = DeleteForm()
#     statement = ''
#     rollups_address = getAddress()
#     input_abi = getABI()
#     print("oi")
#     if request.method == 'POST': ##### ????????
#         print("io")
#         statement = str2hex(delete_form.delete_statement())

#     return render_template('delete.html', delete_form=delete_form, statement=statement, rollups_address=rollups_address, input_abi=input_abi)

@app.route('/delete', methods=['GET', 'POST'])
def delete():
    delete_form = DeleteForm()
    statement = ''
    rollups_address = getAddress()
    input_abi = getABI()
    payload_list = None

    if request.method == 'POST':
        statement = str2hex(delete_form.delete_statement())
        payload_list = delete_form.inspect()
        if (payload_list == 0):
            payload_list = 'NOTFOUND'

    return render_template('delete.html', delete_form=delete_form, statement=statement, rollups_address=rollups_address, input_abi=input_abi, payload_list=payload_list)


@app.route("/train")
def train():
    return render_template("train.html")