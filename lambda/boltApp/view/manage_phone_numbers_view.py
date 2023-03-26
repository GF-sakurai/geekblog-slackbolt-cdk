import json

request_manage_phone_numbers_modal_view = {
	"type": "modal",
	"callback_id": "request_manage_phone_numbers_type_select_modal",
	"title": {
		"type": "plain_text",
		"text": "電話番号編集",
		"emoji": True
	},
	"submit": {
		"type": "plain_text",
		"text": "Next",
		"emoji": True,
	},
	"close": {
		"type": "plain_text",
		"text": "Cancel",
		"emoji": True
	},
	"blocks": [
		{
			"type": "input",
			"block_id": "request-type-block",
			"element": {
				"type": "radio_buttons",
				"action_id": "manage_phone_numbers-input-element",
				"options": [
					{
						"value": "registration",
						"text": {
							"type": "plain_text",
							"text": "電話番号の登録"
						}
					},
					{
						"value": "delete",
						"text": {
							"type": "plain_text",
							"text": "電話番号の削除"
						}
					},
					{
						"value": "summary",
						"text": {
							"type": "plain_text",
							"text": "電話番号一覧の取得"
						}
					}
				]
			},
			"label": {
				"type": "plain_text",
				"text": "実行する処理"
			}
		},
	]
}


manage_phone_numbers_registration_view = {
	"type": "modal",
	"callback_id": "manage_phone_numbers_registration",
	"title": {
		"type": "plain_text",
		"text": "電話番号登録",
		"emoji": True
	},
	"submit": {
		"type": "plain_text",
		"text": "Submit",
		"emoji": True,
	},
	"close": {
		"type": "plain_text",
		"text": "Cancel",
		"emoji": True
	},
	"blocks": [
		{
			"type": "input",
			"block_id": "phone_number_block",
			"element": {
				"type": "plain_text_input",
				"action_id": "manage_phone_numbers_input_element",
			},
			"label": {
				"type": "plain_text",
				"text": "電話番号"
			},
		},
        {
			"type": "input",
			"block_id": "company_name_block",
			"element": {
				"type": "plain_text_input",
				"action_id": "manage_phone_numbers_input_element",
			},
			"label": {
				"type": "plain_text",
				"text": "会社名"
			},
		},
        {
			"type": "input",
			"block_id": "memo_block",
			"element": {
				"type": "plain_text_input",
                "multiline": True,
				"action_id": "manage_phone_numbers_input_element",
			},
			"label": {
				"type": "plain_text",
				"text": "メモ"
			},
			"optional": True
		}
	]
}


manage_phone_numbers_delete_view = {
	"type": "modal",
	"callback_id": "manage_phone_numbers_delete",
	"title": {
		"type": "plain_text",
		"text": "電話番号削除",
		"emoji": True
	},
	"submit": {
		"type": "plain_text",
		"text": "Submit",
		"emoji": True,
	},
	"close": {
		"type": "plain_text",
		"text": "Cancel",
		"emoji": True
	},
	"blocks": [
		{
			"type": "input",
			"block_id": "phone_number_block",
			"element": {
				"type": "plain_text_input",
				"action_id": "manage_phone_numbers_input_element",
			},
			"label": {
				"type": "plain_text",
				"text": "電話番号"
			},
		},
	]
}


def manage_phone_numbers_registration_or_delete_result_view(text):
	result_block = {
		"type": "context",
		"elements": [
			{
				"type": "plain_text",
				"text": text,
				"emoji": True
			}
		]
	}

	view = {
		"type": "modal",
		"callback_id":"manage_phone_numbers_summary",
		"title": {
			"type": "plain_text",
			"text": "電話番号登録結果",
			"emoji": True
		},
		"close": {
			"type": "plain_text",
			"text": "Close",
			"emoji": True
		},
		"blocks": [result_block]
	}	
	return view


def manage_phone_numbers_summary_result_view(summary_results):
	text = ""

	print(summary_results)
	output = json.loads(summary_results["output"])
	result_count = str(output["Count"])

	print(json.dumps(output))


	print(f"合計数 {result_count}")
	items = output["Items"]
	text += "登録件数：" + str(result_count) + "件" + "\n" + \
			"――――――――――――――――――――――――――――――――――――――――――――\n"
	for item in items:
		phone_number = item["phoneNumber"]["S"]
		company_name = item["companyName"]["S"]
		memo = item["memo"]["S"]
		created_at = item["createdAt"]["S"]
		registrant = item["registrant"]["S"]
		text += "電話番号：" + phone_number + "\n" + \
				"会社名：" + company_name + "\n" + \
				"メモ：" + memo + "\n" + \
				"登録日時：" + created_at + "\n" + \
				"登録者：" + registrant + "\n" + \
				"――――――――――――――――――――――――――――――――――――――――――――\n"

	result_block = {
		"type": "context",
		"elements": [
			{
				"type": "plain_text",
				"text": text,
				"emoji": True
			}
		]
	}

	view = {
		"type": "modal",
		"callback_id":"manage_phone_numbers_summary",
		"title": {
			"type": "plain_text",
			"text": "電話番号一覧",
			"emoji": True
		},
		"close": {
			"type": "plain_text",
			"text": "Cancel",
			"emoji": True
		},
		"blocks": [result_block]
	}	
	return view
