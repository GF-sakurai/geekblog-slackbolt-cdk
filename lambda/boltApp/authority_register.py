from typing import Dict
from slack_sdk import WebClient
from view.authority_register_view import authority_register_modal_view
from slack_bolt import Ack, App
import boto3
import os
dynamodb = boto3.client("dynamodb")
def handle_open_authority_register_button_clicks(body: Dict,client: WebClient):
    client.views_open(
        trigger_id=body["trigger_id"],
        view=authority_register_modal_view,
    )


def handle_request_authority_register_modal_view_events(ack: Ack, body: Dict, client: WebClient):
    app = App(token=os.environ["SLACK_BOT_TOKEN"])
    input_value = body["view"]["state"]["values"]
    request_type = input_value["request-type-block"]["authority_register_select-action"]["selected_option"]["value"]
    select_user_id = input_value["select_user"]["authority_register_select-action"]["selected_user"]
    select_app = input_value["select_app"]["authority_register_select-action"]["selected_option"]["value"]
    user_name = app.client.users_info(user=select_user_id)["user"]["real_name"]
    click_user_id = body["user"]["id"]

    if request_type == "registration":
        put_user_data(select_user_id, select_app, user_name)
        message = f"<@{click_user_id}>さんが<@{select_user_id}>さんに{select_app}の権限を追加しました"
    elif request_type == "delete":
        delete_user_data(select_user_id, select_app)
        message = f"<@{click_user_id}>さんが<@{select_user_id}>さんの{select_app}の権限を削除しました"

    client.chat_postMessage(channel=os.environ["AUTHORITY_MANAGEMENT_CHANNEL_ID"], text=message)

    ack()


def put_user_data(user_id,app_name,user_name):
    item = {
        "userId": {"S": user_id},
        "appName":{"S": app_name},
        "userName":{"S":user_name}
    }

    response = dynamodb.put_item(
        TableName=os.environ["USER_TABLE_NAME"],
        Item=item
    )


def delete_user_data(user_id, app_name):
    response = dynamodb.delete_item(
        TableName=os.environ["USER_TABLE_NAME"],
        Key={
            "userId": {"S": user_id},
            "appName": {"S": app_name}
        }
    )


