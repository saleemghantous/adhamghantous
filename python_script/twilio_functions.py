from twilio.twiml.voice_response import Gather, Say, VoiceResponse
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
from .ReportObj import *
from .UserObj import *
from . import *
from .authentication import *
from mongoengine import *
from datetime import datetime
from .config import config, alert_type_legend, alert_target_legend
import json
from flask import Flask, request, jsonify
import pytz
import os

account_sid = os.getenv('ACCOUNT_SID')
auth_token = os.getenv('AUTH_TOKEN')
from_number = "+97233821154"
client = Client(account_sid, auth_token)
action = os.getenv('POST_URL')

mp3_dict = {
    "limited_real": 'https://sapphire-wolf-8672.twil.io/assets/staff_real.mp3',
    "limited_real_res_1": "https://sapphire-wolf-8672.twil.io/assets/staff_real_res_1.mp3",
    "limited_real_res_2": "https://sapphire-wolf-8672.twil.io/assets/staff_real_res_2.mp3",
    "limited_real_res_3": "https://sapphire-wolf-8672.twil.io/assets/staff_real_res_3.mp3",
    "limited_exercise": 'https://sapphire-wolf-8672.twil.io/assets/staff_exercise.mp3',
    "limited_exercise_res_1": "https://sapphire-wolf-8672.twil.io/assets/staff_exercise_res_1.mp3",
    "limited_exercise_res_2": "https://sapphire-wolf-8672.twil.io/assets/staff_exercise_res_2.mp3",
    "limited_exercise_res_3": "https://sapphire-wolf-8672.twil.io/assets/staff_exercise_res_3.mp3",
    "extended_real": 'https://sapphire-wolf-8672.twil.io/assets/staff_real.mp3',
    "extended_real_res_1": "https://sapphire-wolf-8672.twil.io/assets/staff_real_res_1.mp3",
    "extended_real_res_2": "https://sapphire-wolf-8672.twil.io/assets/staff_real_res_2.mp3",
    "extended_real_res_3": "https://sapphire-wolf-8672.twil.io/assets/staff_real_res_3.mp3",
    "extended_exercise": 'https://sapphire-wolf-8672.twil.io/assets/staff_exercise.mp3',
    "extendedexercise_res_1": "https://sapphire-wolf-8672.twil.io/assets/staff_exercise_res_1.mp3",
    "extended_exercise_res_2": "https://sapphire-wolf-8672.twil.io/assets/staff_exercise_res_2.mp3",
    "extended_exercise_res_3": "https://sapphire-wolf-8672.twil.io/assets/staff_exercise_res_3.mp3",
}


report_dict = {
    "invited_list": [],
    "coming_list": [],
    "working_list": [],
    "declined_list": [],
    "no_answer_list": [],
}


def get_current_time_in_israel():
    # Define the Israel timezone
    israel_tz = pytz.timezone('Asia/Jerusalem')
    # Get the current time in the Israel timezone
    now_israel = datetime.now(israel_tz)
    # Format the time in the desired format
    formatted_time = now_israel.strftime('%H:%M:%S %d/%m/%Y')
    return formatted_time


def open_new_alet_report(data):
    newReport = Report(
        alert_name=data["alertName"],
        alert_type=alert_type_legend[data["alertType"]],
        alert_target=alert_target_legend[data["alertTarget"]],
        alert_date=get_current_time_in_israel(),
        call_id=[],
        attempts=1,
        data={})
    newReport.save()
    return newReport.id


def fill_report_initial_data(report_id, data):
    report_dict = {
        "invited_list": [],
        "coming_list": [],
        "working_list": [],
        "declined_list": [],
        "no_answer_list": [],
    }

    if (data["alertTarget"] == "limited"):
        users = User.objects(first_phase="כן")
        for user in users:
            user_data = user.to_json()
            user_data["attempts"] = 0
            report_dict["invited_list"].append(user_data)
    else:
        users = User.objects(second_phase="כן")
        for user in users:
            user_data = user.to_json()
            user_data["attempts"] = 0
            report_dict["invited_list"].append(user_data)
    report = Report.objects(id=report_id).first()
    report.update(data=report_dict)


def call_again():
    reports = Report.objects(attempts=1)
    for report in reports:
        report_json = report.to_json()
        if (is_difference_greater_than_10_minutes(get_current_time_in_israel(), report_json["alert_date"])):
            print("call")
            report_json["date"] = get_current_time_in_israel()
            for user in report_json["data"]["no_answer_list"]:
                user["attempts"] = 2
                user["date"] = get_current_time_in_israel()
                call_sid = send_to_staff(user["phone"], alert_target=alert_target_legend[report_json["alert_target"]], alert_type=alert_type_legend[report_json["alert_type"]])
                report.update(push__call_id=call_sid,data=report_json["data"])
            report.update(attempts=2)

def send_alert(data):
    report_id = open_new_alet_report(data)
    fill_report_initial_data(report_id, data)
    report = Report.objects(id=report_id).first()
    if (data["alertTarget"] == "limited"):
        users = User.objects(first_phase="כן")
    else:
        users = User.objects(second_phase="כן")
    for user in users:
        report_dict = report.to_json()["data"]
        user_data = user.to_json()
        user_data["date"] = get_current_time_in_israel()
        user_data["attempts"] = 1
        report_dict["no_answer_list"].append(user_data)
        call_sid = send_to_staff(user.to_json()[
            "phone"], alert_target=data["alertTarget"], alert_type=data["alertType"])
        report.update(push__call_id=call_sid, data=report_dict)
    return {"result": "success"}


def send_to_staff(to, alert_target, alert_type):
    # Replace with your own Twilio phone numbers
    to_number = '+972'+str(to)[1:]
    # Create a TwiML response
    twiml_response = VoiceResponse()

    # Use Gather to collect user input
    gather = Gather(numDigits=1, action=action, method='POST', timeout=15)

    gather.play(mp3_dict[f"{alert_target}_{alert_type}"])
    twiml_response.append(gather)

    # Use the generated TwiML in the call
    call = client.calls.create(
        twiml=str(twiml_response),  # Convert TwiML to string
        to=to_number,
        from_=from_number,
    )
    return str(call.sid)


def get_alert_info(data):
    report = Report.objects(call_id=data["CallSid"]).first()
    report_json = report.to_json()
    return report_json["alert_id"], alert_target_legend[report_json["alert_target"]], alert_type_legend[report_json["alert_type"]]


def handle_key(data):
    data["Called"] = "0" + data["Called"][4:]
    alert_id, alert_target, alert_type = get_alert_info(data)
    digit_pressed = data.get('Digits')
    twiml_response = VoiceResponse()
    report = Report.objects(id=alert_id).first()
    report_json_data = report.to_json()["data"]
    if digit_pressed == '1':
        twiml_response.play(mp3_dict[f"{alert_target}_{alert_type}_res_1"])
        user_data = [item for item in report_json_data["no_answer_list"]
                     if item["phone"] == data["Called"]]
        user_data[0]["date"] = get_current_time_in_israel()
        report_json_data["no_answer_list"] = [
            item for item in report_json_data["no_answer_list"] if item["phone"] != data["Called"]]
        report_json_data["coming_list"].append(user_data[0])
    elif digit_pressed == '2':
        twiml_response.play(mp3_dict[f"{alert_target}_{alert_type}_res_2"])
        user_data = [item for item in report_json_data["no_answer_list"]
                     if item["phone"] == data["Called"]]
        user_data[0]["date"] = get_current_time_in_israel()
        report_json_data["no_answer_list"] = [
            item for item in report_json_data["no_answer_list"]if item["phone"] != data["Called"]]
        report_json_data["declined_list"].append(user_data[0])
    elif digit_pressed == '3':
        twiml_response.play(mp3_dict[f"{alert_target}_{alert_type}_res_3"])
        user_data[0] = [item for item in report_json_data["no_answer_list"]
                     if item["phone"] == data["Called"]]
        user_data["date"] = get_current_time_in_israel()
        report_json_data["no_answer_list"] = [
            item for item in report_json_data["no_answer_list"]if item["phone"] != data["Called"]]
        report_json_data["working_list"].append(user_data[0])
    else:
        gather = Gather(numDigits=1, action=action,
                        method='POST', timeout=15)
        gather.play(mp3_dict[f"{alert_target}_{alert_type}"])
        twiml_response.append(gather)
        return str(twiml_response)
    report.update(data=report_json_data)
    return str(twiml_response)


def get_balance(data):
    balance = client.api.v2010.account.balance.fetch()
    return {"balance": balance.balance, "currency": balance.currency}


def is_difference_greater_than_10_minutes(datetime_str1, datetime_str2,mins=5):
    # Define the datetime format
    datetime_format = "%H:%M:%S %d/%m/%Y"

    # Convert the string dates to datetime objects
    datetime1 = datetime.strptime(datetime_str1, datetime_format)
    datetime2 = datetime.strptime(datetime_str2, datetime_format)

    # Calculate the difference between the two datetime objects
    difference = abs(datetime1 - datetime2)
    # Check if the difference is greater than 10 minutes (600 seconds)
    return difference.total_seconds() > mins*60
