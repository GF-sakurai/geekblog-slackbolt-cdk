import { aws_logs, Stack, StackProps } from "aws-cdk-lib";
import { Construct } from "constructs";
import { AttributeType, BillingMode, Table } from "aws-cdk-lib/aws-dynamodb";
import {
  Chain,
  Choice,
  Condition,
  Fail,
  JsonPath,
  LogLevel,
  StateMachine,
  StateMachineType,
} from "aws-cdk-lib/aws-stepfunctions";
import {
  CallAwsService,
  DynamoAttributeValue,
  DynamoDeleteItem,
  DynamoPutItem,
} from "aws-cdk-lib/aws-stepfunctions-tasks";

// StackPropsを拡張する
export interface ManagePhoneNumbersStackProps extends StackProps {
  envName: string;
  projectName: string;
  authorityManagementChannelId: string;
}

export class ManagePhoneNumbersStack extends Stack {
  public readonly managePhoneNumbersStateMachine: StateMachine;
  constructor(
    scope: Construct,
    id: string,
    props: ManagePhoneNumbersStackProps
  ) {
    super(scope, id, props);

    // 電話番号管理テーブル
    const managePhoneNumbersTbl = new Table(
      this,
      `${props.projectName}-${props.envName}-managePhoneNumbersTable`,
      {
        partitionKey: {
          name: "phoneNumber",
          type: AttributeType.STRING,
        },
        billingMode: BillingMode.PAY_PER_REQUEST,
      }
    );

    const deleteTask = new DynamoDeleteItem(this, "deleteRecord", {
      table: managePhoneNumbersTbl,
      key: {
        phoneNumber: DynamoAttributeValue.fromString(
          JsonPath.stringAt("$.phone_number")
        ),
      },
    });

    const putItemTask = new DynamoPutItem(this, "putItem", {
      table: managePhoneNumbersTbl,
      item: {
        phoneNumber: DynamoAttributeValue.fromString(
          JsonPath.stringAt("$.phone_number")
        ),
        companyName: DynamoAttributeValue.fromString(
          JsonPath.stringAt("$.company_name")
        ),
        memo: DynamoAttributeValue.fromString(JsonPath.stringAt("$.memo")),
        createdAt: DynamoAttributeValue.fromString(
          JsonPath.stringAt("$.created_at")
        ),
        registrant: DynamoAttributeValue.fromString(
          JsonPath.stringAt("$.registrant")
        ),
      },
    });

    const summaryTask = new CallAwsService(this, "scanRecord", {
      service: "dynamodb",
      action: "scan",
      parameters: {
        TableName: managePhoneNumbersTbl.tableName,
      },
      iamResources: [managePhoneNumbersTbl.tableArn],
      iamAction: "dynamodb:Scan",
    });

    const choiceTask = new Choice(this, "choiceSelectType")
      .when(Condition.stringEquals("$.selected_type", "delete"), deleteTask)
      .when(
        Condition.stringEquals("$.selected_type", "registration"),
        putItemTask
      )
      .when(Condition.stringEquals("$.selected_type", "summary"), summaryTask)
      .otherwise(new Fail(this, "fail"));

    const definition = Chain.start(choiceTask);

    const managePhoneNumbersStateMachine = new StateMachine(
      this,
      `${props.projectName}-${props.envName}-managePhoneNumbers`,
      {
        definition: definition,
        stateMachineType: StateMachineType.EXPRESS,
        logs: {
          destination: new aws_logs.LogGroup(
            this,
            `${props.projectName}-${props.envName}-managePhoneNumbersLogGroup`
          ),
          level: LogLevel.ALL,
        },
      }
    );
    this.managePhoneNumbersStateMachine = managePhoneNumbersStateMachine;
  }
}
