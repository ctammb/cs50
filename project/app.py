import numpy as np
import datetime
import random
import string

#from cs50 import SQL
import sqlite3
from flask import Flask, flash, redirect, render_template, request, session, url_for, jsonify, send_file
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import date
from datetime import datetime
from datetime import timedelta

from helpers import apology, login_required, usd

# Configure application
app = Flask(__name__)


# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
#db = SQL("sqlite:///turningpoints.db")

def convert_to_displaydate(date_string):
    if date_string is not None:
        """(takes string and converts to datetime)"""
        new_date = datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S")
        """takes datetime and formats as specific string """
        return datetime.strftime(new_date, "%m/%d/%Y")
    else:
        return None

def create_client_record(csis_number):

        conn = sqlite3.connect('turningpoints.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        """ establish entry_id and date """
        entry_id = session["user_id"]
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        session["date"] = now

        last_update_id = entry_id
        last_update_date = now
        download = cursor.execute("SELECT * FROM csis_download WHERE csis_number = ?", (csis_number,)).fetchone()

        alert = ""
        firstname = download["csis_firstname"]
        lastname = download["csis_lastname"]
        middlename = download["csis_middlename"]
        dob = download["csis_dob"]
        ssn = download["csis_ssn"]
        email = download["csis_email"]
        phone = download["csis_phone"]
        emergency_phone = download["csis_emergency_phone"]
        veteran = download["csis_veteran"]
        if veteran:
            veteran = "yes"
        else:
            veteran = "no"
        dd214 = download["csis_dd214"]
        emergency_name = download["csis_emergency_name"]
        client_location_addr1 = download["csis_client_location_addr1"]
        client_location_addr2 = download["csis_client_location_addr2"]
        client_location_city = download["csis_client_location_city"]
        client_location_state = download["csis_client_location_state"]
        client_location_zip = download["csis_client_location_zip"]
        client_location_county = download["csis_client_location_county"]
        home_phone = download["csis_phone"]
        emergency_address = download["csis_emergency_address"]
        med_text = download["csis_med_text"]
        race_othertext = download["csis_race_othertext"]
        gender_id = download["csis_gender_id"]
        gender_othertext = download["csis_gender_othertext"]

        cursor.execute("""INSERT INTO client (csis_number, alert, firstname, lastname, middlename, dob, ssn, email, phone, emergency_phone,
                    veteran, dd214, emergency_name, client_location_addr1, client_location_addr2, client_location_city, client_location_state,
                    client_location_zip, client_location_county, home_phone, emergency_address, med_text, race_othertext, gender_id, gender_othertext,
                    entry_id, last_update_date, last_update_id)
                    VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (csis_number, alert, firstname, lastname, middlename, dob, ssn, email, phone, emergency_phone,
                    veteran, dd214, emergency_name, client_location_addr1, client_location_addr2, client_location_city, client_location_state,
                    client_location_zip, client_location_county, home_phone, emergency_address, med_text, race_othertext, gender_id, gender_othertext,
                    entry_id, last_update_date, last_update_id))
        conn.commit()

        client_id = cursor.lastrowid
        print(client_id)
        session["client_id"] = client_id
        client = cursor.execute("SELECT * FROM client WHERE id = ?", (client_id,)).fetchone()

        conn.close()
        return client


def generate_temp_client_id(user_id):

    # Ensure user_id is a 3-digit number (zero-padded)
    user_id_str = f"{int(user_id):03d}"

    # Get today's date in MMDD format
    today = datetime.now().strftime("%d%H")

    # Generate a random alphanumeric character
    random_char = random.choice(string.ascii_uppercase + string.digits)

    # Combine into the final ID
    temp_id = f"T{today}{random_char}{user_id_str}"
    return temp_id

def create_temp_csis():

    conn = sqlite3.connect('turningpoints.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    """ establish entry_id and date """
    entry_id = session["user_id"]
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    temp_id = generate_temp_client_id(entry_id)
    session["date"] = now

    csis_number = temp_id
    session["csis_number"] = csis_number
    csis_alert = "new client"
    session["csis_alert"] = csis_alert
    requires_roi = True
    requires_intake = True
    session["requires_roi"] = requires_roi
    session["requires_intake"] = requires_intake
    firstname = session["firstname"]
    middlename = session["middlename"]
    lastname = session["lastname"]
    dob = session["dob"]
    ssn = session["ssn"]
    if dob:
        dob_dt = datetime.strptime(dob, "%Y-%m-%d")
        cursor.execute("""INSERT INTO csis_download (csis_number, csis_firstname,
            csis_lastname, csis_middlename, csis_dob, csis_ssn, entry_id) VALUES(?, ?, ?, ?,
            ?, ?, ?)""", (csis_number, firstname, lastname, middlename, dob_dt, ssn, entry_id))
    else:
        cursor.execute("""INSERT INTO csis_download (csis_number, csis_firstname,
            csis_lastname, csis_middlename, csis_ssn, entry_id) VALUES(?, ?, ?,
            ?, ?, ?)""", (csis_number, firstname, lastname, middlename, ssn, entry_id))
    conn.commit()
    csis_select = cursor.execute("SELECT * FROM csis_download WHERE csis_number = ?", (csis_number,)).fetchone()
    conn.close()
    return csis_select

def create_log_entries(csis_number, services, firstname):

    conn = sqlite3.connect('turningpoints.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    i = 0
    """ establish entry_id and date """
    entry_id = session["user_id"]
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    session["date"] = now

    while i < len(services):
        service_selection = services[i]["service_shortname"]
        service_id = services[i]["id"]
        status_id = services[i]["default_status_id"]
        form_return = request.form.get(service_selection)
        if form_return == None:
            form_return = 0
        else:
            form_return = int(form_return)

        if form_return == service_id:
            now = datetime.now()
            service_category_id = services[i]["service_category_id"]
            print(service_category_id)
            cursor.execute("""INSERT INTO log (csis_number, firstname, service_category_id, service_id, status_id,
                           entry_id, last_update_date, last_update_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                           (csis_number, firstname, service_category_id, service_id, status_id, entry_id, now, entry_id))
            conn.commit()
        else:
            print("not equal")

        i = i + 1
    flash('Client Log services added successfully')
    conn.close()

def date_check(csis_select):

    """ establish entry_id and date """
    entry_id = session["user_id"]
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    session["date"] = now
    now_time = datetime.strptime(now,'%Y-%m-%d %H:%M:%S')

    session["requires_roi"] = False
    session["requires_intake"] = False

    if csis_select["last_roi_date"] is None:
        requires_roi = True
        session["requires_roi"] = True
        roi_limit = datetime(1, 1, 1, 0, 0)
        session["roi_limit"] = f"{roi_limit.year:04d}-{roi_limit.month:02d}-{roi_limit.day:02d} {roi_limit.hour:02d}:{roi_limit.minute:02d}:{roi_limit.second:02d}"
    else:
        csis_last_roi = datetime.strptime((csis_select["last_roi_date"]), "%Y-%m-%d %H:%M:%S")
        roi_delta = timedelta(days=730)
        roi_limit = csis_last_roi + roi_delta
        session["roi_limit"] = roi_limit.strftime('%Y-%m-%d %H:%M:%S')

    if csis_select["last_intake_date"] is None:
        requires_intake = True
        session["requires_intake"] = True
        intake_limit = datetime(1, 1, 1, 0, 0)
        session["intake_limit"] = f"{intake_limit.year:04d}-{intake_limit.month:02d}-{intake_limit.day:02d} {intake_limit.hour:02d}:{intake_limit.minute:02d}:{intake_limit.second:02d}"
    else:
        csis_last_intake = datetime.strptime((csis_select["last_intake_date"]), "%Y-%m-%d %H:%M:%S")
        intake_delta = timedelta(days=1826)
        intake_limit = csis_last_intake + intake_delta
        session["intake_limit"] = intake_limit.strftime('%Y-%m-%d %H:%M:%S')

    if roi_limit <= now_time:
        requires_roi = True
        session["requires_roi"] = requires_roi
    else:
        requires_roi = False
        session["requires_roi"] = requires_roi

    if intake_limit <= now_time:
        requires_intake = True
        session["requires_intake"] = requires_intake
    else:
        requires_intake = False
        session["requires_intake"] = requires_intake



def prep_contact(client):

    conn = sqlite3.connect('turningpoints.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    csis_number = session["csis_number"]

    requires_roi = session["requires_roi"]
    requires_intake = session["requires_intake"]
    csis_alert = session["csis_alert"]
    dob = client["dob"]
    session["client_id"] = client["id"]

    race_ethnicities = cursor.execute("SELECT id, race_ethnicity FROM race_ethnicity").fetchall()
    medical_conditions = cursor.execute("SELECT id, condition FROM medical_conditions").fetchall()
    states = cursor.execute("SELECT * FROM states").fetchall()
    genders = cursor.execute("SELECT * FROM gender").fetchall()
    relationships = cursor.execute("SELECT * FROM relationships").fetchall()
    races = cursor.execute("SELECT * FROM race_link WHERE csis_number = ?", (csis_number,)).fetchall()
    med_conds = cursor.execute("SELECT * FROM med_conditions_link WHERE csis_number = ?", (csis_number,)).fetchall()
    conn.close()
    return render_template("contact.html", requires_roi=requires_roi, requires_intake=requires_intake, \
                            csis_number=csis_number, csis_alert=csis_alert, states=states, \
                            medical_conditions=medical_conditions, race_ethnicities=race_ethnicities, \
                            genders=genders, dob=dob, client=client, races=races, med_conds=med_conds, \
                            relationships=relationships)


def prep_approvals(csis_select, client):

    conn = sqlite3.connect('turningpoints.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    csis_number = csis_select["csis_number"]

    requires_roi = session["requires_roi"]
    requires_intake = session["requires_intake"]

    if requires_roi:
        prep_contact(client)

    if requires_intake:
        prep_intake(client)

    date_check(csis_select)
    roi_limit = session["roi_limit"]
    print(roi_limit)
    intake_limit = session["intake_limit"]
    print(intake_limit)
    csis_alert = session["csis_alert"]

    firstname = client["firstname"]
    middlename = client["middlename"]
    lastname= client["lastname"]
    dob_short = convert_to_displaydate(csis_select["csis_dob"])
    first_card = convert_to_displaydate(csis_select["ctid_first"])
    last_card = convert_to_displaydate(csis_select["ctid_last"])
    last_roi = convert_to_displaydate(csis_select["last_roi_date"])
    last_intake = convert_to_displaydate(csis_select["last_intake_date"])
    roi_expiration = convert_to_displaydate(roi_limit)
    intake_expiration = convert_to_displaydate(intake_limit)
    last_bike = convert_to_displaydate(csis_select["last_bike_date"])
    last_nav = convert_to_displaydate(csis_select["last_navigator_date"])
    last_backpack = convert_to_displaydate(csis_select["last_backpack_date"])
    med_conds = cursor.execute("SELECT * FROM med_conditions_link WHERE csis_number = ?", (csis_number,)).fetchall()
    conditions = cursor.execute("SELECT * FROM medical_conditions").fetchall()
    intake = "Intake"
    intake_services = cursor.execute("""SELECT s.id, s.service_name, s.service_shortname, s.service_category_id FROM services as s JOIN service_category as sc
                                                ON s.service_category_id = sc.id WHERE sc.service_category_name = ?""", (intake,)).fetchall()
    services_pending_approval = cursor.execute("""SELECT log.*, s.service_name, s.service_shortname FROM log JOIN services AS s ON log.service_id = s.id
                                            WHERE status_id = ? AND log.service_category_id = ? AND csis_number = ?""", ('10', '4', csis_number)).fetchall()

    conn.close()
    return render_template("approvals.html", date=now, conditions=conditions, requires_roi=requires_roi, requires_intake=requires_intake, \
            first_card=first_card, last_card=last_card, last_roi=last_roi, last_intake=last_intake, roi_limit=roi_expiration, intake_limit=intake_expiration, \
            last_bike=last_bike, last_nav=last_nav, last_backpack=last_backpack,\
            csis_number=csis_number, csis_alert=csis_alert, download=csis_select, intake_services=intake_services, \
            services_pending_approval=services_pending_approval, dob=dob_short, client=client, med_conds=med_conds)



def prep_intake(client):

    conn = sqlite3.connect('turningpoints.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    csis_number = session["csis_number"]
    csis_alert = session["csis_alert"]
    dob_short = convert_to_displaydate(client["dob"])
    services = cursor.execute("SELECT * FROM services").fetchall()
    genders = cursor.execute("SELECT * from gender").fetchall()
    situations = cursor.execute("SELECT * FROM situations WHERE input_type_id = ?", (1,)).fetchall()
    circumstances = cursor.execute("SELECT * FROM circumstances").fetchall()
    relationships = cursor.execute("SELECT * FROM relationships").fetchall()
    conn.close()
    return render_template("intake.html", csis_number=csis_number, csis_alert=csis_alert, client=client, \
                            services=services, genders=genders, situations=situations, \
                            circumstances=circumstances, dob=dob_short, relationships=relationships)


def generate_roi(client):

    conn = sqlite3.connect('turningpoints.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    csis_number = session["csis_number"]

    last_roi_date = cursor.execute("""SELECT last_roi_date FROM csis_download
                    WHERE csis_number = ?""", (csis_number,)).fetchone()
    conn.close
    return render_template("roi.html", client=client, last_roi_date=last_roi_date)


@app.route("/", methods = ["GET"])
@login_required
def index():

    """Homepage"""
    if request.method == "GET":
        return render_template("index.html")

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/alacarte", methods = ["GET", "POST"])
@login_required
def alacarte():

    """ establish entry_id and date """
    entry_id = session["user_id"]
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    session["date"] = now
    today = datetime.today().strftime('%Y-%m-%d')

    if request.method == "POST":

        csis_number = request.form.get("csis_number")

        if csis_number:
            conn = sqlite3.connect('turningpoints.db')
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            result = cursor.execute("""SELECT * FROM csis_download WHERE csis_number = ? OR retired_client_number = ?""", (csis_number, csis_number))
            csis_select = result.fetchone()
            conn.close()

            if csis_select:
                session["csis_number"] = csis_select["csis_number"]
                session["csis_alert"] = csis_select["csis_alert"]
                session["firstname"] = csis_select["csis_firstname"]
                date_check(csis_select)

                conn = sqlite3.connect('turningpoints.db')
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                client = cursor.execute("""SELECT * FROM client WHERE csis_number = ? AND create_date = ? ORDER BY id DESC LIMIT 1""", (csis_number, today,)).fetchone()
                conn.close()
                if client == None:
                    client = create_client_record(csis_number)
                trigger = request.form.get("trigger")

                if client:
                    if trigger == "roi":
                        return prep_contact(client)

                    elif trigger == "print_roi":
                        return generate_roi(client)

                    elif trigger == "intake":
                        return prep_intake(client)

                    elif trigger == "approvals":
                        return prep_approvals(csis_select, client)

                    else:
                        flash('Client validated, please select request')
                        return render_template("alacarte.html", csis_number=csis_number)

                else:
                    print("client record empty")
                    return render_template("alacarte.html")

            else:
                print("Not found")
                flash("Client not found, please enter valid CSIS number or retired client number")
                return render_template("alacarte.html")

        else:
            flash("CSIS number required, please enter valid number")
            return render_template("alacarte.html")

    else:
        return render_template("alacarte.html")


@app.route("/approvals", methods = ["GET", "POST"])
@login_required
def approvals():

    """ establish entry_id and date """
    entry_id = session["user_id"]
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    session["date"] = now

    if request.method == "POST":

        conn = sqlite3.connect('turningpoints.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()


        """ get contact information """
        csis_number = session["csis_number"]
        client_id = session["client_id"]
        emergencyname = request.form.get("emergencyname")
        emergencyphone = request.form.get("emergencyphone")
        medical_conditions = request.form.getlist("condition")
        othermedtext = request.form.get("othermedtext")
        veteran = request.form.get("veteran")

        """ update medical conditions"""
        cursor.execute("DELETE FROM med_conditions_link WHERE csis_number = ?", (csis_number,))
        conn.commit()

        count_i = 0
        count_i = len(medical_conditions)
        for i in range(count_i):
            cursor.execute("""INSERT INTO med_conditions_link (condition_id, csis_number)
                VALUES(?, ?)""", (medical_conditions[i], csis_number,))
            conn.commit()
            i = i + 1

        last_update_id = entry_id
        last_update_date = now

        """ update contact information in the client record """
        cursor.execute("""UPDATE client SET emergency_name = ?, emergency_phone = ?, veteran = ?, last_update_id = ?,
                   last_update_date = ?, med_text = ? WHERE id = ?""", (emergencyname, emergencyphone, veteran, last_update_id,
                   last_update_date, othermedtext, client_id))
        conn.commit()

        status = cursor.execute("SELECT id FROM status WHERE status_name = ?", ('Pending Approval',)).fetchone()
        status_id = status["id"]
        service_category =  cursor.execute("SELECT id FROM service_category WHERE service_category_name = ?", ('Intake',)).fetchone()
        service_category_id = service_category["id"]

        services_pending_approval = cursor.execute("""SELECT log.*, s.service_name, s.service_shortname FROM log JOIN services AS s ON log.service_id = s.id
                                                WHERE status_id = ? AND log.service_category_id = ? AND csis_number = ?""",
                                                (status_id, service_category_id, csis_number)).fetchall()
        i = 0
        while i < len(services_pending_approval):
            service_selection = services_pending_approval[i]["service_shortname"]
            form_return = request.form.get(service_selection)

            if form_return == None:
                form_return = 0
            else:
                form_return = int(form_return)
                log_id = services_pending_approval[i]["id"]
                now = datetime.now()
                cursor.execute("""UPDATE log SET status_id = ?, last_update_date = ?, last_update_id = ? WHERE id = ?""",
                        ('9', now, entry_id, log_id))
                conn.commit()
            i = i + 1

        flash('Logs updated successfully')
        conn.close()
        return render_template("identify.html")

    else:
        return render_template("identify.html")


@app.route("/checkin", methods = ["GET", "POST"])
@login_required
def checkin():

    """ establish entry_id and date """
    entry_id = session["user_id"]
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    session["date"] = now

    if request.method == "POST":

        """ check for no csis_number input """
        csis_number = request.form.get("csis_number")

        if csis_number:

            conn = sqlite3.connect('turningpoints.db')
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            """ establish entry_id and date """
            csis_select = cursor.execute("""SELECT * FROM csis_download WHERE csis_number = ? OR retired_client_number = ?""",
                                 (csis_number, csis_number)).fetchone()

        else:
            flash("CSIS number required, please enter valid number")
            return render_template("checkin.html")


        """ if CSIS SQL query returns result """

        if csis_select:
            csis_number = csis_select["csis_number"]
            session["csis_number"] = csis_number
            csis_alert = csis_select["csis_alert"]
            session["csis_alert"] = csis_alert

            """ check for current ROI and Intake """
            date_check(csis_select)

            """ if ROI or Intake not current, return message, else go to checkin2 """

            if session["requires_roi"] == True or session["requires_intake"] == True:
                session["intake"] = True
                flash('Clarity needs update, please direct client to Intake')
                conn.close()
                return render_template("checkin.html", csis_number_display=csis_number, csis_alert=csis_alert)
            else:
                flash('Client validated')
                firstname = csis_select["csis_firstname"]
                session["firstname"] = firstname
                middlename = csis_select["csis_middlename"]
                lastname = csis_select["csis_lastname"]
                dob_short = convert_to_displaydate(csis_select["csis_dob"])
                services = cursor.execute("SELECT * FROM services").fetchall()
                conn.close()
                session["intake"] = False
                return render_template('checkin2.html', csis_alert=csis_alert, \
                                       firstname=firstname, middlename=middlename, lastname=lastname, \
                                       services=services, csis_number=csis_number, dob=dob_short)

        else:
            flash("Client not found, please direct client to Intake")
            conn.close()
            return render_template("checkin.html")

    else:
        return render_template("checkin.html")

@app.route("/checkin2", methods = ["GET", "POST"])
@login_required
def checkin2():

    """ establish entry_id and date """
    entry_id = session["user_id"]
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    session["date"] = now
    today = datetime.today().strftime('%Y-%m-%d')

    if request.method == "POST":

        conn = sqlite3.connect('turningpoints.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        """ establish entry_id and date """""" prep for log entries """
        csis_number = session.get("csis_number")
        firstname = session["firstname"]
        services = cursor.execute("""SELECT s.*, sc.service_category_name FROM services s
                                  JOIN service_category sc ON s.service_category_id = sc.id""").fetchall()
        conn.close()
        """ create log entries from selected services """
        create_log_entries(csis_number, services, firstname)

        if session["intake"] == True:
            conn = sqlite3.connect('turningpoints.db')
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            csis_select = cursor.execute("SELECT * FROM csis_download WHERE csis_number = ?", (csis_number,)).fetchone()
            client = cursor.execute("""SELECT * FROM client WHERE csis_number = ? AND create_date = ? ORDER BY id DESC LIMIT 1""", (csis_number, today,)).fetchone()
            conn.close()
            if client == None:
                client = create_client_record(csis_number)

            return prep_approvals(csis_select, client)

        else:
             return render_template("checkin.html")

    else:
        flash("processing error, please try again")
        return render_template("checkin.html")


@app.route('/csis_select', methods = ["POST"])
@login_required
def csis_select():

    """ establish entry_id and date """
    entry_id = session["user_id"]
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    session["date"] = now
    today = datetime.today().strftime('%Y-%m-%d')

    if request.method == "POST":

        """ retrieve selection(s) """
        select = request.form.get("select")
        print(select)
        merge = request.form.getlist("merge")
        """ print(merge) """

        if select:
            """ establish db connection """
            conn = sqlite3.connect('turningpoints.db')
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            csis_select = cursor.execute("SELECT * FROM csis_download WHERE id = ?", (select,)).fetchone()
            csis_number = csis_select["csis_number"]
            session["csis_number"] = csis_number
            csis_alert = csis_select["csis_alert"]
            session["csis_alert"] = csis_alert
            firstname = csis_select["csis_firstname"]
            session["firstname"] = firstname
            middlename = csis_select["csis_middlename"]
            session["middlename"] = middlename
            lastname = csis_select["csis_lastname"]
            session["lastname"] = lastname
            dob = csis_select["csis_dob"]
            session["dob"] = dob
            ssn = csis_select["csis_ssn"]
            session["ssn"] = ssn
            conn.close()

            date_check(csis_select)

            """ establish db connection """
            conn = sqlite3.connect('turningpoints.db')
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            client = cursor.execute("""SELECT * FROM client WHERE csis_number = ? AND create_date = ? ORDER BY id DESC LIMIT 1""", (csis_number, today,)).fetchone()
            conn.close()
            if client == None:
                client = create_client_record(csis_number)

            if session["requires_roi"] == True:
                """ send to contact.html """
                flash("ROI required")
                return prep_contact(client)

            else:
                if session["requires_intake"] == True:
                    flash("Intake required")
                    return prep_intake(client)
                else:
                    return prep_approvals(csis_select,client)

        else:
            csis_select = create_temp_csis()
            csis_number = session["csis_number"]
            client = create_client_record(csis_number)
            """ send to contact.html """
            return prep_contact(client)
    else:
        return render_template("identify.html")

@app.route("/contact", methods = ["GET", "POST"])
@login_required
def contact():

    """Contact Information Form"""
    if request.method == "POST":

        """ establish entry_id and date """
        entry_id = session["user_id"]
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        session["date"] = now

        csis_number = session["csis_number"]
        client_id = session["client_id"]

        """Contact Info - retrieve data"""
        alert = request.form.get("alert")
        firstname = request.form.get("firstname")
        middlename = request.form.get("middlename")
        lastname = request.form.get("lastname")
        dob = request.form.get("dob")
        ssn = request.form.get("ssn")

        """ dob_dt puts dob(YYYY-mm-dd) in datetime format """
        if dob:
            dob_dt = datetime.strptime(dob, "%Y-%m-%d")
        else:
            dob_dt = None

        email= request.form.get("client_email")
        cell = request.form.get("cell")
        home = request.form.get("home")
        address1 = request.form.get("address1")
        address2 = request.form.get("address2")
        city = request.form.get("city")
        state = request.form.get("state")
        zip = request.form.get("zip")
        county = request.form.get("county")
        emergencyname = request.form.get("emergencyname")
        emergencyphone = request.form.get("emergencyphone")

        emergencyaddress = request.form.get("emergencyaddress")
        medical_conditions = request.form.getlist("medical_condition")
        othermedtext = request.form.get("othermedtext")
        veteran = request.form.get("veteran")
        dd214 = request.form.get("DD214")

        race_ethnicities = request.form.getlist("race_ethnicity")
        race_othertext = request.form.get("race_othertext")

        gender = request.form.get("gender")
        gender_othertext = request.form.get("gender_othertext")

        last_update_id = entry_id
        last_update_date = now

        """ establish db connection """
        conn = sqlite3.connect('turningpoints.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        """ update client record """

        cursor.execute("""UPDATE client SET csis_number = ?, alert = ?, firstname = ?, lastname = ?,
                middlename = ?, dob = ?, ssn = ?, email = ?, phone = ?, emergency_phone = ?, veteran = ?,
                dd214 = ?, entry_id = ?, last_update_date = ?, last_update_id = ?, emergency_name = ?, client_location_addr1 = ?,
                client_location_addr2 = ?, client_location_city = ?, client_location_state = ?, client_location_zip = ?, client_location_county = ?,
                home_phone = ?, emergency_address = ?, med_text = ?, race_othertext = ?, gender_id = ?, gender_othertext = ?
                WHERE id = ?""", (csis_number,
                alert, firstname, lastname, middlename, dob_dt, ssn, email, cell, emergencyphone,
                veteran, dd214, entry_id, last_update_date, last_update_id, emergencyname, address1,
                address2, city, state, zip, county, home, emergencyaddress, othermedtext,
                race_othertext, gender, gender_othertext, client_id))
        conn.commit()

        """ update medical conditions and race """

        count_i = 0
        i = 0

        cursor.execute("DELETE FROM med_conditions_link WHERE csis_number = ?", (csis_number,))
        conn.commit()

        count_i = len(medical_conditions)
        for i in range(count_i):
            condition_id = medical_conditions[i]
            cursor.execute("""INSERT INTO med_conditions_link (condition_id, csis_number)
                VALUES(?, ?)""", (condition_id, csis_number,))
            conn.commit()
            i = i + 1

        count_i = 0
        i = 0
        count_i = len(race_ethnicities)

        cursor.execute("DELETE FROM race_link WHERE csis_number = ?", (csis_number,))
        conn.commit()

        for i in range(count_i):
            race_id = race_ethnicities[i]
            cursor.execute("""INSERT INTO race_link (client_id, race_id, csis_number)
                            VALUES(?, ?, ?)""", (client_id, race_id, csis_number))
            conn.commit()
            i = i + 1

        """Dependent Information"""
        cursor.execute("DELETE FROM dependents WHERE csis_number = ?", (csis_number,))
        conn.commit()

        i = 0
        row_count = request.form.get("hh_row_count")
        if row_count is not None and row_count.isdigit():
            print(row_count, type(row_count), i, type(i))
            row_count = int(row_count)

            while i < row_count:
                row = i + 1
                print(f"row-{row}")
                hh_firstname = request.form.get(f"firstname-{row}")
                print(f"firstname-{row}")

                hh_lastname = request.form.get(f"lastname-{row}")
                hh_dob = request.form.get(f"dob-{row}")
                hh_ssn = request.form.get(f"ssn-{row}")
                hh_gender_id = request.form.get(f"gender-{row}")
                print(f"gender-{row}")
                hh_relationship = request.form.get(f"relationship-{row}")
                print(f"relationship-{row}")
                cursor.execute("""INSERT INTO dependents (client_id, csis_number, hh_firstname, hh_lastname, hh_dob, hh_ssn, hh_gender_id, hh_relationship, entry_id)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""", (client_id, csis_number, hh_firstname, hh_lastname, hh_dob, hh_ssn, hh_gender_id, hh_relationship, entry_id))
                conn.commit()
                i = i + 1

        """ roi completion """
        requires_roi = False
        session["requires_roi"] = requires_roi
        cursor.execute("""UPDATE csis_download SET last_roi_date = ? WHERE csis_number = ?""",
                       (now, csis_number,))
        conn.commit()

        requires_intake = session.get("requires_intake", False)
        client = cursor.execute("SELECT * FROM client WHERE id = ?", (client_id,)).fetchone()

        if requires_intake == True:
            flash("contact information successfully updated - Intake required - ")
            conn.close()
            return prep_intake(client)

        else:
            flash("contact information successfully updated - updated Intake not required - ")
            cursor.execute("""INSERT INTO log (csis_number, firstname, service_category_id, service_id, status_id,
                           entry_id, last_update_date, last_update_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                           (csis_number, firstname, '4', '23', '10', entry_id, now, entry_id))
            conn.commit()

            csis_select = cursor.execute("SELECT * FROM csis_download WHERE csis_number = ?", (csis_number,)).fetchone()
            conn.close
            return prep_approvals(csis_select, client)

    else:

        return render_template("identify.html")


@app.route("/identify", methods = ["GET","POST"])
@login_required
def identify():

    if request.method == "POST":

        """ establish date """
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        session["date"] = now
        today = datetime.today().strftime('%Y-%m-%d')

        """ retrieve data """
        csis_number = request.form.get("csis_number")
        firstname = request.form.get("firstname")
        session["firstname"] = firstname
        middlename = request.form.get("middlename")
        session["middlename"] = middlename
        lastname = request.form.get("lastname")
        session["lastname"] = lastname
        dob = request.form.get("DOB")
        session["dob"] = dob
        ssn = request.form.get("SSN")
        session["ssn"] = ssn

        """ dob_dt puts dob in datetime format """
        if dob:
            dob_dt = datetime.strptime(dob, "%Y-%m-%d")

        """searches for matches in csis_download """
        """ searches by csis_number and first 3 of firstname and first 3 of lastname in combo with dob and ssn """

        firstname3 = firstname[0:3]
        lastname3 = lastname[0:3]
        firstname3 += '%'
        lastname3 += '%'

        """ establish db connection """
        conn = sqlite3.connect('turningpoints.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        """ establish entry_id and date """

        if firstname or lastname:
            if csis_number:
                if (dob == "" and ssn == ""):
                    csis_select = cursor.execute("""SELECT * FROM csis_download WHERE (csis_firstname LIKE ? AND
                    csis_lastname LIKE ?) OR csis_number = ? OR retired_client_number = ?""",
                    (firstname3, lastname3, csis_number, csis_number)).fetchall()
                elif dob == "":
                    csis_select = cursor.execute("""SELECT * FROM csis_download WHERE (csis_firstname LIKE ? AND
                    csis_lastname LIKE ?) OR csis_ssn = ? OR csis_number = ? OR retired_client_number = ?""",
                    (firstname3, lastname3, ssn, csis_number, csis_number)).fetchall()
                elif ssn == "":
                    csis_select = cursor.execute("""SELECT * FROM csis_download WHERE (csis_firstname LIKE ? AND
                    csis_lastname LIKE ? AND csis_dob = ?) OR csis_number = ? OR retired_client_number = ?""",
                    (firstname3, lastname3, dob_dt, csis_number, csis_number)).fetchall()
                else:
                    csis_select = cursor.execute("""SELECT * FROM csis_download WHERE (csis_firstname LIKE ? AND
                    csis_lastname LIKE ? AND csis_dob = ? AND csis_ssn = ?) OR csis_number = ? OR retired_client_number = ?""",
                    (firstname3, lastname3, dob_dt, ssn, csis_number, csis_number)).fetchall()
            else:
                if (dob == "" and ssn == ""):
                    csis_select = cursor.execute("""SELECT * FROM csis_download WHERE (csis_firstname LIKE ? AND
                    csis_lastname LIKE ?)""", (firstname3, lastname3)).fetchall()
                elif dob == "":
                    csis_select = cursor.execute("""SELECT * FROM csis_download WHERE (csis_firstname LIKE ? AND
                    csis_lastname LIKE ?) OR csis_ssn = ?""", (firstname3, lastname3, ssn)).fetchall()
                elif ssn == "":
                    csis_select = cursor.execute("""SELECT * FROM csis_download WHERE (csis_firstname LIKE ? AND
                    csis_lastname LIKE ? AND csis_dob = ?)""", (firstname3, lastname3, dob_dt)).fetchall()
                else:
                    csis_select = cursor.execute("""SELECT * FROM csis_download WHERE (csis_firstname LIKE ? AND
                    csis_lastname LIKE ? AND csis_dob = ? AND csis_ssn = ?)""", (firstname3, lastname3, dob_dt, ssn)).fetchall()

        else:

            if csis_number:
                if (dob == "" and ssn == ""):
                    csis_select = cursor.execute("""SELECT * FROM csis_download WHERE csis_number = ? OR retired_client_number = ?""",
                    (csis_number, csis_number,)).fetchall()
                elif dob == "":
                    csis_select = cursor.execute("""SELECT * FROM csis_download WHERE csis_ssn = ? OR csis_number = ? OR retired_client_number = ?""",
                    (ssn, csis_number, csis_number,)).fetchall()
                elif ssn == "":
                    csis_select = cursor.execute("""SELECT * FROM csis_download WHERE csis_dob = ?) OR csis_number = ? OR retired_client_number = ?""",
                    (dob_dt, csis_number, csis_number)).fetchall()
                else:
                    csis_select = cursor.execute("""SELECT * FROM csis_download WHERE csis_dob = ? AND csis_ssn = ?) OR csis_number = ? OR retired_client_number = ?""",
                    (dob_dt, ssn, csis_number, csis_number)).fetchall()
            else:
                if (dob == "" and ssn == ""):
                    flash("Not enough information, please enter at least one item")
                    conn.close()
                    return render_template("identify.html")
                elif dob == "":
                    csis_select = cursor.execute("""SELECT * FROM csis_download WHERE csis_ssn = ?""",
                    (ssn,)).fetchall()
                elif ssn == "":
                    csis_select = cursor.execute("""SELECT * FROM csis_download WHERE csis_dob = ?)""",
                    (dob_dt,)).fetchall()
                else:
                    csis_select = cursor.execute("""SELECT * FROM csis_download WHERE csis_dob = ? AND csis_ssn = ?)""",
                    (dob_dt, ssn,)).fetchall()

        match_count = len(csis_select)
        print(match_count)
        conn.close()

        """ if no matches, assign temp csis_number and create csis_download record and client record, set requires ROI and Intake to True"""

        if match_count == 0:
            if not (firstname and lastname) or not (dob or ssn):
                flash('CSIS number not found, must enter name and date of birth or social security number')
                return render_template("identify.html")
            flash('no matches found temporary CSIS number created - ')
            csis_select = create_temp_csis()
            csis_number = session["csis_number"]

            client = create_client_record(csis_number)

            """ prep for contact.html """
            return prep_contact(client)

        else:

                flash(" matches found: ", match_count)
                formatted_data = []
                for row in csis_select:
                    formatted_row = dict(row)

                    formatted_row["csis_dob"] = convert_to_displaydate(row["csis_dob"])
                    formatted_row["ctid_first"] = convert_to_displaydate(row["ctid_first"])
                    formatted_row["ctid_last"] = convert_to_displaydate(row["ctid_last"])
                    formatted_row["last_roi_date"] = convert_to_displaydate(row["last_roi_date"])
                    formatted_row["last_intake_date"] = convert_to_displaydate(row["last_intake_date"])
                    formatted_row["last_bike_date"] = convert_to_displaydate(row["last_bike_date"])
                    formatted_row["last_navigator_date"] = convert_to_displaydate(row["last_navigator_date"])
                    formatted_row["last_backpack_date"] = convert_to_displaydate(row["last_backpack_date"])
                    formatted_row["last_bike_date"] = convert_to_displaydate(row["last_bike_date"])
                    formatted_row["last_navigator_date"] = convert_to_displaydate(row["last_navigator_date"])
                    formatted_row["last_backpack_date"] = convert_to_displaydate(row["last_backpack_date"])

                    formatted_data.append(formatted_row)


                return render_template("csis.html", formatted_data=formatted_data)

    else:
        return render_template("identify.html")


@app.route("/intake", methods = ["GET", "POST"])
@login_required
def intake():

    """ establish db connection """
    conn = sqlite3.connect('turningpoints.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    """ establish entry_id and date """
    entry_id = session["user_id"]
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    session["date"] = now

    if request.method == "POST":
        csis_number = session["csis_number"]
        firstname = session["firstname"]
        client_id = session["client_id"]

        """ Retrieve Household Information"""
        i = 0
        row_count = request.form.get("hh_row_count")
        print(row_count, type(row_count))
        if row_count is not None and row_count.isdigit():
            row_count = int(row_count)

            while i < row_count:
                row = i + 1
                hh_firstname = request.form.get(f"firstname-{row}")
                hh_lastname = request.form.get(f"lastname-{row}")
                hh_dob = request.form.get(f"dob-{row}")
                hh_ssn = request.form.get(f"ssn-{row}")
                hh_gender_id = request.form.get(f"gender-{row}")
                hh_relationship = request.form.get(f"relationship-{row}")
                cursor.execute("""INSERT INTO households (client_id, csis_number, hh_firstname, hh_lastname, hh_dob, hh_ssn, hh_gender_id, hh_relationship, entry_id)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""", (client_id, csis_number, hh_firstname, hh_lastname, hh_dob, hh_ssn, hh_gender_id, hh_relationship, entry_id))
                conn.commit()
                i = i + 1


        """ Retrieve Situations """

        situations = cursor.execute("SELECT sit.* FROM situations as sit").fetchall()
        for row in situations:
            print(dict(row))
        i = 0
        while i < len(situations):
            situation_selection = situations[i]["situation"]
            situation_id = situations[i]["id"]
            form_return = request.form.get(situation_selection)

            cursor.execute("""INSERT INTO client_situation (client_id, client_situation_id, client_response, csis_number)
                       VALUES (?, ?, ?, ?)""", (client_id, situation_id, form_return, csis_number))
            conn.commit()
            i = i + 1


        """ Retrieve Circumstances """

        circumstances = cursor.execute("SELECT * FROM circumstances").fetchall()
        i = 0
        form_return = int(request.form.get("circumstance"))
        print(form_return, type(form_return))
        while i < len(circumstances):
            circumstance_id = circumstances[i]["id"]
            print(circumstance_id, type(circumstance_id))
            if form_return == circumstance_id:
                cursor.execute("INSERT INTO client_circumstances (csis_number, circumstances_id) VALUES (?, ?)", (csis_number, circumstance_id,))
                conn.commit()
            i = i + 1

        flash('client Intake updated - ')

        requires_intake = False
        session["requires_intake"] = requires_intake
        cursor.execute("UPDATE csis_download SET last_intake_date = ? WHERE csis_number = ?", (now, csis_number,))
        conn.commit()

        csis_select = cursor.execute("SELECT * FROM csis_download WHERE csis_number = ?", (csis_number,)).fetchone()
        client = cursor.execute("SELECT * FROM client WHERE csis_number = ? ORDER by id DESC", (csis_number,)).fetchone()
        client_id = client["id"]
        session["client_id"] = client_id


        """ Retrieve TP Service Requests and create log entries """

        services = cursor.execute("SELECT * FROM services").fetchall()
        conn.close()
        create_log_entries(csis_number, services, firstname)
        return prep_approvals(csis_select, client)

    else:
        csis_select = cursor.execute("SELECT * FROM csis_download WHERE csis_number = ?", (csis_number,)).fetchone()
        client = cursor.execute("SELECT * FROM client WHERE id = ? ORDER BY id DESC LIMIT 1", (client_id,)).fetchone()
        conn.close()
        return prep_intake(client)

@app.route("/log", methods = ["GET","POST"])
@login_required
def log():

    """ establish entry_id and date """
    entry_id = session["user_id"]
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    session["date"] = now

    """ establish db connection """
    conn = sqlite3.connect('turningpoints.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    categories = cursor.execute("SELECT id, service_category_name FROM service_category ORDER BY service_category_name ASC").fetchall()
    statuses = cursor.execute("SELECT id, status_name FROM status ORDER BY status_name ASC").fetchall()
    log_statuses = cursor.execute("SELECT id, status_name FROM status WHERE status_name != ? ORDER BY status_name ASC", ("all",)).fetchall()
    area_filter = "all"
    status_filter = "all"

    if request.method == "POST":

        date_filter = request.form.get("date")
        set_date = datetime.strptime(date_filter, "%Y-%m-%d")
        set_day = set_date.date()

        area_filter_id = int(request.form.get("service_category_filter_id"))

        status_filter_id = int(request.form.get("status_filter_id"))

        area = cursor.execute("SELECT service_category_name FROM service_category WHERE id = ?", (area_filter_id,)).fetchone()
        area_filter = area["service_category_name"]
        status = cursor.execute("SELECT status_name FROM status WHERE id = ?", (status_filter_id,)).fetchone()
        status_filter = status["status_name"]

        if (area_filter == "all" and status_filter == "all"):
            checkin_clients = cursor.execute(""" SELECT l.id, l.entry_date, date(l.entry_date) AS log_date, l.csis_number,
                                l.firstname, sc.service_category_name, s.service_name, ss.status_name
                                    FROM log l
                                    JOIN service_category sc ON l.service_category_id = sc.id
                                    JOIN services s ON l.service_id = s.id
                                    JOIN status ss ON l.status_id = ss.id
                                    WHERE log_date = ? """, (set_day,)).fetchall()
        else:
            if status_filter == "all":
                checkin_clients = cursor.execute(""" SELECT l.id, l.service_category_id, l.service_id, l.status_id, l.entry_date, date(l.entry_date) AS log_date,
                    l.csis_number, l.firstname, sc.service_category_name, s.service_name, ss.status_name
                    FROM log l
                    JOIN service_category sc ON l.service_category_id = sc.id
                    JOIN services s ON l.service_id = s.id
                    JOIN status ss ON l.status_id = ss.id
                    WHERE log_date = ? AND l.service_category_id = ?""", (set_day, area_filter_id,)).fetchall()
            else:
                if area_filter == "all":
                    checkin_clients = cursor.execute(""" SELECT l.id, l.service_category_id, l.service_id, l.status_id, l.entry_date, date(l.entry_date) AS log_date,
                        l.csis_number, l.firstname, sc.service_category_name, s.service_name, ss.status_name
                        FROM log l
                        JOIN service_category sc ON l.service_category_id = sc.id
                        JOIN services s ON l.service_id = s.id
                        JOIN status ss ON l.status_id = ss.id
                        WHERE log_date = ? AND l.status_id = ?""", (set_day, status_filter_id,)).fetchall()
                else:
                        checkin_clients = cursor.execute(""" SELECT l.id, l.service_category_id, l.service_id, l.status_id, l.entry_date, date(l.entry_date) AS log_date,
                            l.csis_number, l.firstname, sc.service_category_name, s.service_name, ss.status_name
                            FROM log l
                            JOIN service_category sc ON l.service_category_id = sc.id
                            JOIN services s ON l.service_id = s.id
                            JOIN status ss ON l.status_id = ss.id
                            WHERE log_date = ? AND l.service_category_id = ? AND l.status_id = ?""", (set_day, area_filter_id, status_filter_id)).fetchall()
        conn.close()
        return render_template("dailylog.html", checkin_clients=checkin_clients, categories=categories, statuses=statuses, log_statuses=log_statuses, date=set_date, service_category_filter_id=area_filter_id, status_filter_id=status_filter_id)
    else:
        print('get')
        checkin_clients = cursor.execute(""" SELECT l.id, l.entry_date, date(l.entry_date) AS log_date, l.csis_number, l.firstname, sc.service_category_name,
                                         s.service_name, ss.status_name
            FROM log l
            JOIN service_category sc ON l.service_category_id = sc.id
            JOIN services s ON l.service_id = s.id
            JOIN status ss ON l.status_id = ss.id
            WHERE log_date = current_date """).fetchall()

        area = cursor.execute("SELECT id FROM service_category WHERE service_category_name = ?", ("all",)).fetchone()
        area_filter_id = area["id"]
        status = cursor.execute("SELECT id FROM status WHERE status_name = ?", ("all",)).fetchone()
        status_filter_id = status["id"]
        conn.close()
        return render_template("dailylog.html", checkin_clients=checkin_clients, categories=categories, statuses=statuses, log_statuses=log_statuses, date=now, service_category_filter_id=area_filter_id, status_filter_id=status_filter_id)


@app.route("/log_update", methods = ["POST"])
@login_required
def log_update():

    """ establish db connection """
    conn = sqlite3.connect('turningpoints.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    """ establish entry_id and date """
    entry_id = session["user_id"]
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    session["date"] = now

    log_id = int(request.values.get("log_id"))
    status_change = int(request.values.get("status_change"))

    categories = cursor.execute("SELECT id, service_category_name FROM service_category").fetchall()
    statuses = cursor.execute("SELECT id, status_name FROM status").fetchall()
    log_statuses = cursor.execute("SELECT id, status_name FROM status WHERE status_name != ? ORDER BY status_name ASC", ("all",)).fetchall()
    cursor.execute("UPDATE log SET status_id = ?  WHERE id = ?", (status_change, log_id,))
    conn.commit()
    date_filter = request.values.get("date")
    set_date = datetime.strptime(date_filter, "%Y-%m-%d")
    set_day = set_date.date()

    area_filter_id = int(request.values.get("sc_id"))
    area = cursor.execute("SELECT service_category_name FROM service_category WHERE id = ?", (area_filter_id,)).fetchone()
    area_filter = area["service_category_name"]

    status_filter_id = int(request.values.get("ss_id"))
    status = cursor.execute("SELECT status_name FROM status WHERE id = ?", (status_filter_id,)).fetchone()
    status_filter = status["status_name"]

    if (area_filter == "all" and status_filter == "all"):
        checkin_clients = cursor.execute(""" SELECT l.id, l.entry_date, date(l.entry_date) AS log_date, l.csis_number, l.firstname, sc.service_category_name,
                                         s.service_name, ss.status_name
                                FROM log l
                                JOIN service_category sc ON l.service_category_id = sc.id
                                JOIN services s ON l.service_id = s.id
                                JOIN status ss ON l.status_id = ss.id
                                WHERE log_date = ? """, (set_day,)).fetchall()
    else:
        if status_filter == "all":
            checkin_clients = cursor.execute(""" SELECT l.id, l.entry_date, date(l.entry_date) AS log_date, l.csis_number, l.firstname, sc.service_category_name,
                                             s.service_name, ss.status_name
                FROM log l
                JOIN service_category sc ON l.service_category_id = sc.id
                JOIN services s ON l.service_id = s.id
                JOIN status ss ON l.status_id = ss.id
                WHERE log_date = ? AND l.service_category_id = ?""", (set_day, area_filter_id,)).fetchall()
        else:
            if area_filter == "all":
                checkin_clients = cursor.execute(""" SELECT l.id, l.entry_date, date(l.entry_date) AS log_date, l.csis_number, l.firstname,
                                                 sc.service_category_name, s.service_name, ss.status_name
                    FROM log l
                    JOIN service_category sc ON l.service_category_id = sc.id
                    JOIN services s ON l.service_id = s.id
                    JOIN status ss ON l.status_id = ss.id
                    WHERE log_date = ? AND l.status_id = ?""", (set_day, status_filter_id,)).fetchall()
            else:
                    checkin_clients = cursor.execute(""" SELECT l.id, l.entry_date, date(l.entry_date) AS log_date, l.csis_number, l.firstname,
                                                     sc.service_category_name, s.service_name, ss.status_name
                        FROM log l
                        JOIN service_category sc ON l.service_category_id = sc.id
                        JOIN services s ON l.service_id = s.id
                        JOIN status ss ON l.status_id = ss.id
                        WHERE log_date = ? AND l.service_category_id = ? AND l.status_id = ?""", (set_day, area_filter_id, status_filter_id)).fetchall()

    conn.close()
    return render_template("dailylog.html", checkin_clients=checkin_clients, categories=categories, statuses=statuses, log_statuses=log_statuses, date=set_date, service_category_filter_id=area_filter_id, status_filter_id=status_filter_id)


@app.route("/login", methods=["GET", "POST"])
def login():

    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            flash("must provide username")
            return render_template("login.html")

        # Ensure password was submitted
        elif not request.form.get("password"):
            flash("must provide password")
            return render_template("login.html")

        """ establish db connection """
        conn = sqlite3.connect('turningpoints.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Query database for username
        rows = cursor.execute("SELECT * FROM users WHERE username = ?", (request.form.get("username"),)).fetchone()

        # Ensure username exists and password is correct
        if not rows or not check_password_hash(rows["hash"], request.form.get("password")):
            flash("invalid username and/or password")
            conn.close()
            return render_template("login.html")
        else:
            conn.close()

        # Remember which user has logged in
        session["user_id"] = rows["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")




@app.route("/plan", methods = ["GET","POST"])
@login_required
def plan():

    """ establish db connection """
    conn = sqlite3.connect('turningpoints.db', timeout=10)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    """ establish entry_id and date """
    entry_id = session["user_id"]
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    session["date"] = now
    short_date = datetime.now().strftime("%Y-%m-%d")
    today = datetime.today().strftime('%Y-%m-%d')

    """Plan Setup"""
    if request.method == "POST":

        """Retrieve CSIS number"""
        csis_number = request.form.get("csis_number")
        session["csis_number"] = csis_number

        """ Retrieve client record and client needs """
        date = request.form.get("plan_date")
        session["plan_data_date"] = date
        print(date, type(date))
        print(csis_number)
        plan_create_date = datetime.now().strftime('%Y-%m-%d')
        print(plan_create_date, type(plan_create_date))

        plan = cursor.execute("""SELECT * FROM plans WHERE csis_number = ? AND data_date = ?""", (csis_number, date,)).fetchone()

        if plan:
            flash("plan already exists, please select from Access Plans")
            plans = cursor.execute("""SELECT p.id, p.csis_number, date(p.last_update) as shortlast_update, date(p.entry_date) as shortplan_date, p.status, s.status_name, cd.csis_firstname, cd.csis_lastname
                        FROM plans p
                        JOIN csis_download cd ON p.csis_number = cd.csis_number
                        JOIN status s ON p.status = s.id
                        WHERE p.csis_number = ?""", (csis_number,)).fetchall()
            conn.close()
            return render_template("clientplans.html", plans=plans)
        else:
            client = cursor.execute("SELECT * FROM client WHERE csis_number = ? AND create_date = ? ORDER BY id DESC LIMIT 1", (csis_number, plan_create_date,)).fetchone()

            if not client:
                conn.close()
                client = create_client_record(csis_number)

                conn = sqlite3.connect('turningpoints.db', timeout=10)
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

            client_id = client["id"]
            session["client_id"] = client_id
            session["firstname"] = client["firstname"]
            dob_short = convert_to_displaydate(client["dob"])
            veteran = client["veteran"]

            circumstance = cursor.execute("""SELECT cc.*, c.circumstance FROM client_circumstances cc
                        JOIN circumstances c ON cc.circumstances_id = c.id WHERE csis_number = ? ORDER BY cc.id DESC LIMIT 1""", (csis_number,)).fetchone()
            if circumstance:
                if circumstance["expired_date"]:
                    client_circumstance = "None"
                    session["circumstance"] = client_circumstance
                else:
                    client_circumstance = circumstance["circumstance"]
                    session["circumstance"] = client_circumstance
                    circumstance_id = circumstance["circumstances_id"]
            else:
                client_circumstance = "None"
                session["circumstance"] = client_circumstance
                circumstance_id = 4


            cursor.execute("""INSERT INTO plans (csis_number, last_update, last_update_user_id, status,
                        navigator_id, data_date, plan_circumstance) VALUES(?, ?, ?, ?, ?, ?, ?)""", (csis_number, now, entry_id,
                                                        "1", entry_id, date, circumstance_id))
            conn.commit()
            plan_id = cursor.lastrowid
            print(plan_id)
            session["plan_id"] = plan_id
            plan_notes = ""

            client_plan_services = cursor.execute("""SELECT DISTINCT l.service_id, l.service_category_id, date(l.entry_date) AS log_date, sc.service_category_name, s.service_name,
                                        ss.status_name, l.status_id, s.resource_category_id, c.category_name, s.service_shortname
                                        FROM log l
                                        JOIN service_category sc ON l.service_category_id = sc.id
                                        JOIN services s ON l.service_id = s.id
                                        JOIN status ss ON l.status_id = ss.id
                                        JOIN category c ON s.resource_category_id = c.id
                                        WHERE csis_number = ? AND (log_date = ? OR log_date = ?) ORDER BY l.service_id""", (csis_number, date, plan_create_date)).fetchall()

            services = cursor.execute("SELECT * FROM services ORDER BY id").fetchall()
            print(client_plan_services)

            if client_plan_services:
                seen_values = set()
                unique_services = []
                i = 0
                for service in client_plan_services:
                    service_dict = dict(service)
                    value = service_dict["service_id"]
                    if value not in seen_values:
                        seen_values.add(value)
                for service in services:
                    service_dict = dict(service)
                    value = service_dict["id"]
                    if value not in seen_values:
                        unique_services.append(service_dict)

            if client_plan_services:
                for i, service in enumerate(client_plan_services):
                    service_dict = dict(service)
                    category = service["resource_category_id"]
                    resource_list = cursor.execute("""SELECT crl.resource_id, r.* FROM category_resource_link crl
                                        JOIN resource r ON crl.resource_id = r.id
                                        WHERE category_id =?""", (category,)).fetchall()
                    service_dict["resources"] = [dict(resource) for resource in resource_list]
                    client_plan_services[i] = service_dict
                print("csis:", csis_number, "now:", now)

                for row in client_plan_services:
                    pp_service_id = row["service_id"]
                    service_priority = 3
                    service_status = 1
                    cursor.execute("""INSERT INTO plan_priorities (plan_id, service_id, service_priority, plan_service_status) VALUES(?, ?, ?, ?)""",
                                (plan_id, pp_service_id, service_priority, service_status))
                    conn.commit()


            statuses = cursor.execute("SELECT * FROM status").fetchall()

            client_situations = cursor.execute("""SELECT cs.id, cs.client_situation_id, s.situation, s.input_type_id, cs.client_response,
                                        s.situation_question, s.resource_category_id, s.associated_service_id FROM client_situation cs
                                        JOIN situations as s ON cs.client_situation_id = s.id
                                        WHERE csis_number = ? AND date(cs.entry_date) = ?""", (csis_number, date,)).fetchall()

            for situation in client_situations:
                situation_id = situation["id"]

                cursor.execute("""UPDATE client_situation SET plan_id = ? WHERE id = ?""", (plan_id, situation_id,))
                conn.commit()

            flash("client plan created")
            conn.close()
            return render_template("plan2.html", plan_id=plan_id, plan_notes=plan_notes, client_plan_services=client_plan_services, client=client, date=date, dob=dob_short, veteran=veteran, \
                                    client_circumstance=client_circumstance, situations=client_situations, services=unique_services, now=now, statuses=statuses)

    else:
        navigation_clients = cursor.execute("""SELECT DISTINCT csis_number, firstname FROM log WHERE service_category_id = ? AND date(entry_date) = ?""",
                                            ("7", short_date,)).fetchall()
        conn.close()
        return render_template("plan.html", clients=navigation_clients, date=short_date)


@app.route("/print_roi", methods = ["GET", "POST"])
@login_required
def print_roi():

    """ establish entry_id and date """
    entry_id = session["user_id"]
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    session["date"] = now

    if request.method == "POST":

        conn = sqlite3.connect('turningpoints.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()


@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    """Profile"""

    """ establish db connection """
    conn = sqlite3.connect('turningpoints.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    """ establish entry_id and date """
    entry_id = session["user_id"]
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    session["date"] = now

    if request.method == "POST":
        user_profile = cursor.execute("SELECT * FROM users WHERE id = ?", (session["user_id"],)).fetchone()

        user_id = user_profile["id"]
        user_name = user_profile["username"]
        conn.close()
        return render_template("update.html", user_id=user_id, user_name=user_name)


    # User reached route via GET (as by clicking a link or via redirect)

    else:
        user_profile = cursor.execute("""SELECT u.*, s.*, r.* FROM users as u
                              JOIN status as s ON u.status_id = s.id
                              JOIN roles as r ON u.role_id = r.id
                              WHERE u.id = ?""", (session["user_id"],)).fetchone()

        roles = cursor.execute("SELECT * from roles").fetchall()
        statuses = cursor.execute("SELECT * from status").fetchall()
        conn.close()
        return render_template("profile.html", user_profile=user_profile, roles=roles, statuses=statuses)

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register"""

    # Forget any user_id
    session.clear()

    """ establish entry_id and date """

    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    session["date"] = now

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        """ establish db connection """
        conn = sqlite3.connect('turningpoints.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # add to user table
        username = request.form.get("username")
        firstname = request.form.get("firstname")
        lastname = request.form.get("lastname")
        email = request.form.get("email")
        role_id = request.form.get("role_id")
        status_id = 1
        phone = request.form.get("phone")
        hash = generate_password_hash(request.form.get("password"))

        cursor.execute("""INSERT INTO users (username, firstname, lastname, email, role_id, status_id, phone, hash)
                       VALUES(?, ?, ?, ?, ?, ?, ?, ?)""", (username, firstname, lastname, email, role_id, status_id, phone, hash))
        conn.commit()

        flash('Registration successful')

        # Redirect user to home page
        # return redirect("/")
        conn.close()
        return render_template("login.html")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


@app.route("/resources", methods = ["GET", "POST"])
@login_required
def resources():

    """Resources"""
    """ establish db connection """
    conn = sqlite3.connect('turningpoints.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    """ establish entry_id and date """
    entry_id = session["user_id"]
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    session["date"] = now

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # add to user table
        category_id = request.form.getlist("category_id")
        resource_name = request.form.get("resource_name")
        parent_resource_id = request.form.get("parent_resource_id")
        resource_description = request.form.get("resource_description")
        website = request.form.get("website")
        primary_phone = request.form.get("primary_phone")
        instructions = request.form.get("instructions")
        instruction_path = request.form.get("instruction_path")
        primary_contact = request.form.get("primary_contact")
        email = request.form.get("email")
        resource_type = request.form.get("resource_type")
        entry_id = session["user_id"]

        cursor.execute("""INSERT INTO resource (resource_name, resource_description, website, phone, instructions,
                       instruction_path, entry_id, parent_resource_id, contact_name, contact_email, resource_type_id)
                       VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", (resource_name, resource_description, website, primary_phone,
                       instructions, instruction_path, entry_id, parent_resource_id, primary_contact, email, resource_type))
        conn.commit()
        resource = cursor.execute("SELECT id from resource WHERE resource_name = ?", (resource_name,)).fetchone()
        resource_id = resource["id"]

        i=0
        count = len(category_id)
        while i < count:
            cursor.execute("INSERT INTO category_resource_link (resource_id, category_id) VALUES(?, ?)", (resource_id, category_id[i],))
            conn.commit()
            i = i + 1

        flash('Resource added successfully')

        # Redirect user to resources page
        conn.close()
        return redirect("/resources")

    # User reached route via GET (as by clicking a link or via redirect)
    else:

        categories = cursor.execute("SELECT id, category_name FROM category").fetchall()
        resources = cursor.execute("SELECT id, resource_name FROM resource").fetchall()
        resource_types = cursor.execute("SELECT id, resource_type_name FROM resource_type").fetchall()
        conn.close()
        return render_template("resources.html", categories=categories, resources=resources, resource_types=resource_types)


@app.route("/resourcelist", methods = ["GET"])
@login_required
def resourcelist():

    """ establish db connection """
    conn = sqlite3.connect('turningpoints.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    """Resource List"""
    resources = cursor.execute("SELECT * FROM resource").fetchall()
    categories = cursor.execute("SELECT * FROM category").fetchall()
    conn.close()
    return render_template("resourcelist.html", resources=resources, categories=categories)


@app.route("/save_plan", methods = ["GET", "POST"])
@login_required
def save_plan():

    """ establish db connection """
    conn = sqlite3.connect('turningpoints.db', timeout=10)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    """ establish entry_id and dates """
    entry_id = session["user_id"]
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    short_date = datetime.now().strftime("%Y-%m-%d")
    session["date"] = now

    if request.method == "POST":
        csis_number = session["csis_number"]
        client_id = session["client_id"]
        plan_id = session["plan_id"]
        firstname = session["firstname"]

        """ if existing plan, retrive plan notes, otherwise display error and return to create plan page """
        if plan_id:
            plan_notes = request.form.get("plan_notes")
            print(plan_notes)
        else:
            flash("plan error, contact administrator")
            navigation_clients = cursor.execute("""SELECT DISTINCT csis_number, firstname FROM log WHERE service_category_id = ? AND date(entry_date) = ?""",
                                            ("7", now,)).fetchall()
            conn.close()
            return render_template("plan.html, clients=navigation_clients, date=now")

        """ retrieve all services, cycle through one by one to see status within plan """
        services = cursor.execute("SELECT * FROM services ORDER BY id").fetchall()
        active = 1
        closed = 2
        complete = 5
        waiting = 4

        i = 0
        for i in range(len(services)):
            service_selection = services[i]["service_shortname"]
            service_id = services[i]["id"]
            service_category_id = services[i]["service_category_id"]

            """ retrieve service priority assignment """
            priority_variable = "priority_" + service_selection
            form_return = request.form.get(priority_variable)
            status_variable = "status_" + service_selection
            status_instruction = request.form.get(status_variable)

            if form_return:
                """ retrieve service note and checkbox """
                service_priority = int(form_return)
                note_check = "note_check_" + service_selection
                note_check_yes = request.form.get(note_check)
                service_note = "service_note_" + service_selection
                plan_service_note = request.form.get(service_note)
                priority = cursor.execute("""SELECT * FROM plan_priorities WHERE plan_id = ? AND service_id = ?""",
                            (plan_id, service_id,)).fetchone()

                """ update plan_priorities """
                if priority:
                    priority_id = priority["id"]
                    cursor.execute("""UPDATE plan_priorities SET service_note = ?, service_priority = ?, note_check = ?, plan_service_status = ?
                                WHERE id = ?""", (plan_service_note, service_priority, note_check_yes, status_instruction, priority_id))
                    conn.commit()
                else:
                    cursor.execute("""INSERT INTO plan_priorities (plan_id, service_id, service_note, service_priority, note_check, plan_service_status)
                                VALUES (?, ?, ?, ?, ?, ?)""", (plan_id, service_id, plan_service_note, service_priority, note_check_yes, active))
                    conn.commit()

                """ update resource list and checkboxes """
                j = 0
                resource_category_id = services[i]["resource_category_id"]
                resources = cursor.execute("SELECT resource_id FROM category_resource_link WHERE category_id = ?", (resource_category_id,)).fetchall()
                for j in range(len(resources)):
                    resource_selection = resources[j]["resource_id"]
                    resource_check = str(resource_selection) + "_" + str(service_id)
                    resource_check_yes = request.form.get(resource_check)

                    if resource_check_yes:
                        if resource_selection == int(resource_check_yes):
                            resource = cursor.execute("""SELECT * FROM plan_resources WHERE plan_id = ? AND service_id = ? AND resource_id = ?""",
                                (plan_id, service_id, resource_selection,)).fetchone()
                            if not resource:
                                cursor.execute("""INSERT INTO plan_resources (plan_id, service_id, resource_id, plan_resource_status)
                                            VALUES (?, ?, ?, ?)""", (plan_id, service_id, resource_selection, active))
                                conn.commit()
                            else:
                                cursor.execute("""UPDATE plan_resources SET plan_resource_status = ? WHERE plan_id = ? AND service_id = ? AND resource_id = ?""",
                                            (active, plan_id, service_id, resource_selection))
                                conn.commit()
                        else:
                            resource = cursor.execute("""SELECT * FROM plan_resources WHERE plan_id = ? AND service_id = ? AND resource_id = ?""",
                                (plan_id, service_id, resource_selection,)).fetchone()
                            if resource:
                                cursor.execute("""UPDATE plan_resources SET plan_resource_status = ? WHERE plan_id = ? AND service_id = ? AND resource_id = ?""",
                                            (closed, plan_id, service_id, resource_selection))
                                conn.commit()
            else:
                add_variable = "add_" + service_selection
                form_return_add = request.form.get(add_variable)
                if form_return_add:
                    cursor.execute("""INSERT INTO plan_priorities (plan_id, service_id, plan_service_status)
                                VALUES (?, ?, ?)""", (plan_id, service_id, active))
                    conn.commit()
                    cursor.execute("""INSERT INTO log (csis_number, firstname, service_category_id, service_id, status_id,
                        entry_id, last_update_date, last_update_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                        (csis_number, firstname, service_category_id, service_id, waiting, entry_id, now, entry_id))
                    conn.commit()



        """ Update Situations """

        situations = cursor.execute("SELECT sit.* FROM situations as sit").fetchall()

        i = 0
        for i in range(len(situations)):
            situation_selection = situations[i]["situation"]
            situation_id = situations[i]["id"]
            form_return = request.form.get(situation_selection)
            client_situation = cursor.execute("""SELECT * FROM client_situation
                                    WHERE client_situation_id = ? AND plan_id = ?""", (situation_id, plan_id,)).fetchone()
            if client_situation:
                cursor.execute("""UPDATE client_situation SET client_response = ? WHERE client_situation_id = ? AND plan_id = ?""",
                               (form_return, situation_id, plan_id))
                conn.commit()
            else:
                cursor.execute("""INSERT INTO client_situation (client_id, client_situation_id, client_response, csis_number, plan_id)
                       VALUES (?, ?, ?, ?, ?)""", (client_id, situation_id, form_return, csis_number, plan_id))
                conn.commit()


        cursor.execute("""UPDATE plans SET last_update = ?, last_update_user_id = ?, status = ?,
                       navigator_id = ?, notes = ? WHERE id = ?""", (now, entry_id,
                                                    "1", entry_id, plan_notes, plan_id))
        conn.commit()
        flash("client plan updated")

        navigation_clients = cursor.execute("""SELECT DISTINCT csis_number, firstname FROM log WHERE service_category_id = ? AND date(entry_date) = ?""",
                                            ("7", short_date,)).fetchall()
        conn.close()
        return render_template("plan.html", clients=navigation_clients, date=now)
    else:
        navigation_clients = cursor.execute("""SELECT DISTINCT csis_number, firstname FROM log WHERE service_category_id = ? AND date(entry_date) = ?""",
                                            ("7", short_date,)).fetchall()
        conn.close()
        return render_template("plan.html", clients=navigation_clients, date=now)


@app.route("/select_plan", methods = ["GET", "POST"])
@login_required
def select_plan():

    """ establish db connection """
    conn = sqlite3.connect('turningpoints.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    """ establish entry_id and date """
    entry_id = session["user_id"]
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    session["date"] = now
    today = datetime.today().strftime('%Y-%m-%d')

    """Plan Selection"""
    if request.method == "POST":
        """Retrieve plan number"""
        plan_id = request.form.get("display_plan")
        print(plan_id)
        session["plan_id"] = plan_id
        plan = cursor.execute("""SELECT p.*, c.circumstance FROM plans p
                              JOIN circumstances c ON p.plan_circumstance = c.id
                              WHERE p.id = ?""", (plan_id,)).fetchone()
        plan_notes = plan["notes"]

        """ Retrieve latest client record created today """

        csis_number = plan["csis_number"]
        session["csis_number"] = csis_number
        client_create_date = datetime.now().strftime('%Y-%m-%d')
        print(client_create_date, type(client_create_date))
        client = cursor.execute("""SELECT * FROM client WHERE csis_number = ? AND create_date = ? ORDER BY id DESC LIMIT 1""",
                                (csis_number, client_create_date,)).fetchone()

        if not client:
            conn.close()
            client = create_client_record(csis_number)

            conn = sqlite3.connect('turningpoints.db', timeout=10)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

        client_id = client["id"]
        print(client_id)
        session["client_id"] = client_id
        session["firstname"] = client["firstname"]
        dob_short = convert_to_displaydate(client["dob"])
        date = plan["data_date"]
        veteran = client["veteran"]
        client_circumstance = plan["circumstance"]
        print(client_circumstance)
        session["circumstance"] = client_circumstance
        client_plan_services = []
        client_plan_services = cursor.execute("""SELECT * FROM plan_priorities pp
                                    JOIN services s ON pp.service_id = s.id
                                    JOIN service_category sc ON s.service_category_id = sc.id
                                    JOIN status st ON pp.plan_service_status = st.id
                                    JOIN category c ON s.resource_category_id = c.id
                                    WHERE pp.plan_id = ?""", (plan_id,)).fetchall()

        services = cursor.execute("SELECT * FROM services ORDER BY id").fetchall()
        for row in client_plan_services:
            print(dict(row))


        seen_values = set()
        unique_services = []
        i = 0
        for service in client_plan_services:
            service_dict = dict(service)
            value = service_dict["service_id"]
            if value not in seen_values:
                seen_values.add(value)
        for service in services:
            service_dict = dict(service)
            value = service_dict["id"]
            if value not in seen_values:
                unique_services.append(service_dict)


        for i, service in enumerate(client_plan_services):
            service_dict = dict(service)
            category = service["resource_category_id"]
            resource_list = cursor.execute("""SELECT crl.resource_id, r.* FROM category_resource_link crl
                                JOIN resource r ON crl.resource_id = r.id
                                WHERE category_id =?""", (category,)).fetchall()
            service_dict["resources"] = [dict(resource) for resource in resource_list]
            client_plan_services[i] = service_dict
        print("csis:", csis_number, "now:", now)

        statuses = cursor.execute("SELECT * FROM status").fetchall()
        client_situations = cursor.execute("""SELECT cs.client_situation_id, cs.entry_date, s.situation, s.input_type_id, cs.client_response,
                                    s.situation_question, s.resource_category_id, s.associated_service_id FROM client_situation as cs
                                    JOIN situations as s ON cs.client_situation_id = s.id
                                    WHERE cs.plan_id = ?""", (plan_id,)).fetchall()

        conn.close()

        return render_template("plan2.html", plan_id=plan_id, plan_notes=plan_notes, client_plan_services=client_plan_services, client=client, date=date, dob=dob_short, veteran=veteran, \
                                client_circumstance=client_circumstance, situations=client_situations, services=unique_services, now=now, statuses=statuses)
    else:
        plans = cursor.execute("""SELECT p.id, p.csis_number, date(p.last_update) as shortlast_update, date(p.entry_date) as shortplan_date, p.status, s.status_name, cd.csis_firstname, cd.csis_lastname
                               FROM plans p
                               JOIN csis_download cd ON p.csis_number = cd.csis_number
                               JOIN status s ON p.status = s.id""").fetchall()
        conn.close()
        return render_template("clientplans.html", plans=plans)



@app.route("/situations", methods = ["GET"])
@login_required
def situations():

    """Plan Setup"""
    if request.method == "GET":
        return render_template("situations.html")


@app.route("/update", methods=["GET", "POST"])
@login_required
def update():
    """Password Update"""

    if request.method == "POST":
        # Ensure current password was submitted
        if not request.form.get("password"):
            return apology("must provide current password", 403)

        # Ensure new password was submitted
        elif not request.form.get("password_update"):
            return apology("must provide new password", 403)

        # Ensure new password was confirmed
        elif not request.form.get("confirm"):
            return apology("Must confirm new password", 403)

            """ establish db connection """
        conn = sqlite3.connect('turningpoints.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        user_profile = cursor.execute("SELECT * FROM users WHERE id = ?", (session["user_id"],)).fetchone()

        # Ensure current password is correct
        if not check_password_hash(user_profile["hash"], request.form.get("password")):
            conn.close()
            return apology("invalid password", 403)

        # Ensure password is entered and confirmed
        password_update = request.form.get("password_update")
        confirm = request.form.get("confirm")

        if password_update != confirm:
            conn.close()
            return apology("Passwords do not match")

        # add to user table

        hash = generate_password_hash(request.form.get("password_update"))
        cursor.execute("UPDATE users SET hash = ? WHERE id = ?", (hash, session["user_id"],))
        conn.commit()

        # Redirect user to home page
        conn.close()
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)

    else:
        return apology("invalid access", 403)


@app.route("/validate_registration", methods = ["POST"])
def validate_registration():

    if request.method == "POST":
        username = request.get_json() ['username']

        """ establish db connection """
        conn = sqlite3.connect('turningpoints.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        rows = cursor.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        conn.close()
        if rows:
            return jsonify({"user_exists": "true"})
        else:
            return jsonify({"user_exists": "false"})
    else:
        return render_template("register.html")


