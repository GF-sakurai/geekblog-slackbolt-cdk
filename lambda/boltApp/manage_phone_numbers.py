from typing import Dict
from slack_sdk import WebClient
from slack_bolt import Ack
import os
import logging
import json
import re
import datetime
import boto3

from view.manage_phone_numbers_view import *
from view.common_view import *

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
step_functions = boto3.client('stepfunctions')


def handle_open_manage_phone_numbers_modal_button_clicks(body: Dict, client: WebClient,):
    client.views_open(
        trigger_id=body["trigger_id"],
        view=request_manage_phone_numbers_modal_view,
    )


def handle_request_manage_phone_numbers_type_select_modal_view_events(ack: Ack, view: Dict):
    inputs = view["state"]["values"]
    selected_type = inputs["request-type-block"]["manage_phone_numbers-input-element"]["selected_option"]["value"]

    if selected_type == "registration":
        ack(
            response_action="update",
            view=manage_phone_numbers_registration_view
        )
        return
    elif selected_type == "delete":
        ack(
            response_action="update",
            view=manage_phone_numbers_delete_view
        )
        return
    elif selected_type == "summary":
        print("summary")
        input_data = {"selected_type": selected_type}
        response = step_functions.start_sync_execution(
            stateMachineArn=os.environ["MANAGE_PHONE_NUMBERS_STATE_MACHINE_ARN"],
            input=json.dumps(input_data)
        )
        ack(
            response_action="update",
            view=manage_phone_numbers_summary_result_view(response)
        )


def handle_request_manage_phone_numbers_registration(ack: Ack, body: Dict):
    now = datetime.datetime.now().strftime(('%Y-%m-%d %H:%M:%S'))
    phone_number = body['view']['state']['values']['phone_number_block']['manage_phone_numbers_input_element']['value']
    phone_number = re.sub(r'\D', '', phone_number)
    click_user_name = body['user']['username']
    company_name = body['view']['state']['values']['company_name_block']['manage_phone_numbers_input_element']['value']
    memo = body['view']['state']['values']['memo_block']['manage_phone_numbers_input_element']['value']
    if memo is None:
        memo = "備考なし"
    if is_valid_phone_number(phone_number) == False:
        ack(
            response_action="errors",
            errors={
                "phone_number_block": "正しい電話番号を入力してください",
            },
        )
        return
    
    input_data = {
        "selected_type": "registration",
        "phone_number": phone_number,
        "created_at": now,
        "company_name": company_name,
        "memo": memo,
        "registrant": click_user_name
    }
    
    response = step_functions.start_sync_execution(
        stateMachineArn=os.environ["MANAGE_PHONE_NUMBERS_STATE_MACHINE_ARN"],
        input=json.dumps(input_data)
    )
    print(type(response))
    if response["status"] == "SUCCEEDED":
        text = f"{phone_number}の登録が完了しました"
    else:
        text = f"{phone_number}の登録に失敗しました"
    ack(
        response_action="update",
        view=manage_phone_numbers_registration_or_delete_result_view(text)
    )


def handle_request_manage_phone_numbers_delete(ack: Ack, body: Dict):
    phone_number = body['view']['state']['values']['phone_number_block']['manage_phone_numbers_input_element']['value']
    phone_number = re.sub(r'\D', '', phone_number)
    if is_valid_phone_number(phone_number) == False:
        ack(
            response_action="errors",
            errors={
                "phone_number_block": "正しい電話番号を入力してください",
            },
        )
        return
    
    input_data = {
        "selected_type": "delete",
        "phone_number": phone_number,
    }
    
    response = step_functions.start_sync_execution(
        stateMachineArn=os.environ["MANAGE_PHONE_NUMBERS_STATE_MACHINE_ARN"],
        input=json.dumps(input_data)
    )
    if response["status"] == "SUCCEEDED":
        text = f"{phone_number}の削除が完了しました"
    else:
        text = f"{phone_number}の削除に失敗しました"
    ack(
        response_action="update",
        view=manage_phone_numbers_registration_or_delete_result_view(text)
    )


"""
入力された番号が、日本の固定電話もしくは日本の携帯電話番号と一致するかを判定する
"""
def is_valid_phone_number(phone_number):

    # 電話番号の形式に合致する正規表現パターン
    fixed_phone_pattern = r'^0\d{9}$'
    mobile_phone_pattern = r'^0[5789]0\d{8}$'

    if re.match(mobile_phone_pattern, phone_number):
        return True
    elif re.match(fixed_phone_pattern, phone_number) and phone_number[:3] not in ["090", "080", "070", "050"]:
        return True
    else:
        return False

