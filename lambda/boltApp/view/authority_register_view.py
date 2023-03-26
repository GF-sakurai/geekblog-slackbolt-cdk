authority_register_modal_view = {
	"type": "modal",
    "callback_id": "authority_register_submission_click",
	"title": {
		"type": "plain_text",
		"text": "権限管理アプリ",
		"emoji": True
	},
	"submit": {
		"type": "plain_text",
		"text": "Submit",
		"emoji": True
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
				"action_id": "authority_register_select-action",
				"initial_option": {
					"value": "registration",
					"text": {
						"type": "plain_text",
						"text": "権限の追加"
					}
				},
				"options": [
					{
						"value": "registration",
						"text": {
							"type": "plain_text",
							"text": "権限の追加"
						}
					},
					{
						"value": "delete",
						"text": {
							"type": "plain_text",
							"text": "権限の削除"
						}
					}
				]
			},
			"label": {
				"type": "plain_text",
				"text": "実行する処理"
			}
		},
		{
			"block_id": "select_user",
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": "*誰の権限を変更しますか？*"
			},
			"accessory": {
				"type": "users_select",
				"placeholder": {
					"type": "plain_text",
					"text": "選択する",
					"emoji": True
				},
				"action_id": "authority_register_select-action"
			}
		},
		{
			"block_id":"select_app",
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": "*権限を追加するアプリを選択してください*"
			},
			"accessory": {
				"type": "static_select",
				"placeholder": {
					"type": "plain_text",
					"text": "選択する",
					"emoji": True
				},
				"options": [
					{
						"text": {
							"type": "plain_text",
							"text": "電話番号登録",
							"emoji": True
						},
						"value": "manage_phone_numbers"
					},
					{
						"text": {
							"type": "plain_text",
							"text": "アプリ権限管理",
							"emoji": True
						},
						"value": "authority_register"
					},
				],
				"action_id": "authority_register_select-action"
			}
		}
	]
}