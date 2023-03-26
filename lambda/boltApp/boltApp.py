
import logging
import os
import boto3
from pprint import pformat
from typing import Dict

from slack_bolt import Ack, App
from slack_bolt.adapter.aws_lambda import SlackRequestHandler
from slack_sdk import WebClient
from view.common_view import *
from manage_phone_numbers import *
from authority_register import *
logger = logging.getLogger()
logger.setLevel(logging.INFO)
dynamodb = boto3.client('dynamodb')

app = App(
    process_before_response=True,
    token=os.environ["SLACK_BOT_TOKEN"],
    signing_secret=os.environ["SLACK_BOT_SIGNING_SECRET"],
)


"""
Lazy listeners機能の使用時に、3秒以内にレスポンスを返す処理
"""
def respond_to_slack_within_3_seconds(ack):

    ack()


home_tab_view_blocks_dict = {
    "manage_phone_numbers": manage_phone_numbers_block,
    "authority_register": authority_register_block,
}


"""
ホームタブのviewを表示
"""
@app.event("app_home_opened")
def update_home_tab(client: WebClient, event: Dict):
    user_id = event["user"]
    allowed_apps = get_allowed_apps(user_id)
    home_tab_view_blocks = []

    for allowed_app in allowed_apps:
        home_tab_view_blocks.append(home_tab_view_blocks_dict[allowed_app])
    
    home_tab_view = {
        "type": "home",
        "blocks": home_tab_view_blocks
    }
    
    try:
        client.views_publish(user_id=user_id, view=home_tab_view)
    except Exception as e:
        logger.error(f"Error publishing home tab:\n {e}")


"""
アプリのホームで電話番号管理ボタンを押したときの処理
"""
app.action("request_manage_phone_numbers_button_click")(
    ack=respond_to_slack_within_3_seconds,
    lazy=[handle_open_manage_phone_numbers_modal_button_clicks]
)

"""
電話番号管理でいずれかのラジオボタンを選択してNextをクリックしたときの処理
"""
@app.view("request_manage_phone_numbers_type_select_modal")
def call_handle_request_manage_phone_numbers_modal_view_events(ack: Ack, view: Dict):
    handle_request_manage_phone_numbers_type_select_modal_view_events(ack, view)


"""
ラジオボタンで「登録」を選択して、電話番号等各種情報を入力してSubmitをクリックしたときの処理
"""
@app.view("manage_phone_numbers_registration")
def call_handle_request_manage_phone_numbers_registration(ack: Ack, body: Dict):
    handle_request_manage_phone_numbers_registration(ack, body)


"""
ラジオボタンで「削除」を選択して、電話番号を入力してSubmitをクリックしたときの処理
"""
@app.view("manage_phone_numbers_delete")
def call_handle_request_manage_phone_numbers_delete(ack: Ack, body: Dict):
    handle_request_manage_phone_numbers_delete(ack, body)


"""
アプリのホームでアプリ権限管理ボタンをクリックしたときの処理
"""
app.action("authority_register_button_click")(
    ack=respond_to_slack_within_3_seconds,
    lazy=[handle_open_authority_register_button_clicks]
)

"""
アプリ権限管理のモーダルでユーザー選択及びアプリ選択をしたときの処理
"""
@app.action("authority_register_select-action")
def authority_register_select_action(ack: Ack):
    ack()


"""
アプリ権限管理のモーダルでSubmitをクリックしたときの処理
"""
@app.view("authority_register_submission_click")
def call_handle_request_authority_register_modal_view_events(ack: Ack, body: Dict, client: WebClient):
    handle_request_authority_register_modal_view_events(ack, body, client)


"""
ユーザがどのアプリの権限を持っているか確認する関数
"""
def get_allowed_apps(user_id):
    table_name = os.environ["USER_TABLE_NAME"]

    key_condition_expression = "userId = :pk"
    expression_attribute_values ={
        ":pk": {"S":user_id}
    }
    
    response = dynamodb.query(
        TableName=table_name,
        KeyConditionExpression=key_condition_expression,
        ExpressionAttributeValues=expression_attribute_values
    )
    apps = []
    items = response["Items"]
    for item in items:
        apps.append(item["appName"]["S"])
    
    return apps


"""
Slack Appのエントリポイント
"""
def handler(event, context):
    logger.info(f"event:\n{pformat(event)}")
    slack_handler = SlackRequestHandler(app=app)
    return slack_handler.handle(event, context)
