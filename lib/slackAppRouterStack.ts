import { Duration, ScopedAws, Stack, StackProps } from "aws-cdk-lib";
import { Construct } from "constructs";
import {
  RestApi,
  LambdaIntegration,
  EndpointType,
} from "aws-cdk-lib/aws-apigateway";
import { StringParameter } from "aws-cdk-lib/aws-ssm";
import { AttributeType, BillingMode, Table } from "aws-cdk-lib/aws-dynamodb";
import {
  Code,
  Function,
  LayerVersion,
  Runtime,
  AssetCode,
} from "aws-cdk-lib/aws-lambda";
import {
  ManagedPolicy,
  PolicyStatement,
  Role,
  ServicePrincipal,
} from "aws-cdk-lib/aws-iam";
import { StateMachine } from "aws-cdk-lib/aws-stepfunctions";

// StackPropsを拡張する
export interface SlackAppRouterStackProps extends StackProps {
  envName: string;
  projectName: string;
  authorityManagementChannelId: string;
  managePhoneNumbersStateMachine: StateMachine;
}

export class SlackAppRouterStack extends Stack {
  constructor(scope: Construct, id: string, props: SlackAppRouterStackProps) {
    super(scope, id, props);

    const { accountId, region } = new ScopedAws(this);

    // SSMパラメータストアから値を取得する
    const SLACK_BOT_TOKEN = StringParameter.valueForStringParameter(
      this,
      `/${props.projectName}/${props.envName}/SLACK_BOT_TOKEN`
    );
    const SLACK_BOT_SIGNING_SECRET = StringParameter.valueForStringParameter(
      this,
      `/${props.projectName}/${props.envName}/SLACK_BOT_SIGNING_SECRET`
    );

    // 権限ユーザー管理テーブル
    const authorizationManagementUserTable = new Table(
      this,
      `${props.projectName}-${props.envName}-userTable`,
      {
        partitionKey: {
          name: "userId",
          type: AttributeType.STRING,
        },
        sortKey: {
          name: "appName",
          type: AttributeType.STRING,
        },
        billingMode: BillingMode.PAY_PER_REQUEST,
      }
    );

    // boltApp lambda用のロール
    const boltAppRole = new Role(this, `${props.envName}-boltAppRole`, {
      assumedBy: new ServicePrincipal("lambda.amazonaws.com"),
      managedPolicies: [
        ManagedPolicy.fromManagedPolicyArn(
          this,
          `${props.envName}-lambdaBasickExecution`,
          "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
        ),
      ],
    });

    // lambda
    const boltApp = new Function(this, `${props.envName}-boltApp`, {
      functionName: `${props.envName}-boltApp`,
      runtime: Runtime.PYTHON_3_9,
      code: Code.fromAsset("lambda/boltApp"),
      handler: "boltApp.handler",
      role: boltAppRole,
      timeout: Duration.seconds(30),
      layers: [
        new LayerVersion(this, `${props.envName}-boltAppLayer`, {
          code: AssetCode.fromAsset("layer/boltAppLayer/"),
        }),
      ],
      environment: {
        SLACK_BOT_TOKEN: SLACK_BOT_TOKEN,
        SLACK_BOT_SIGNING_SECRET: SLACK_BOT_SIGNING_SECRET,
        USER_TABLE_NAME: authorizationManagementUserTable.tableName,
        AUTHORITY_MANAGEMENT_CHANNEL_ID: props.authorityManagementChannelId,
        MANAGE_PHONE_NUMBERS_STATE_MACHINE_ARN:
          props.managePhoneNumbersStateMachine.stateMachineArn,
        TZ: "Asia/Tokyo",
      },
    });

    // boltAppRoleに権限を追加
    authorizationManagementUserTable.grantReadWriteData(boltApp);
    props.managePhoneNumbersStateMachine.grantStartExecution(boltAppRole);
    props.managePhoneNumbersStateMachine.grantStartSyncExecution(boltAppRole);
    boltAppRole.addToPolicy(
      new PolicyStatement({
        resources: [
          `arn:aws:lambda:${region}:${accountId}:function:${props.envName}-boltApp`,
        ],
        actions: ["lambda:GetFunction", "lambda:InvokeFunction"],
      })
    );

    // APIGW
    const api = new RestApi(this, `${props.envName}-boltApi`, {
      endpointConfiguration: {
        types: [EndpointType.REGIONAL],
      },
    });

    api.root.addMethod("POST", new LambdaIntegration(boltApp));
  }
}
