#!/usr/bin/env node
import "source-map-support/register";
import * as cdk from "aws-cdk-lib";
import { SlackAppRouterStack } from "../lib/slackAppRouterStack";
import { ManagePhoneNumbersStack } from "../lib/ManagePhoneNumbersStack";

const app = new cdk.App();
const projectName = app.node.tryGetContext("projectName");
const envKey = app.node.tryGetContext("environment");
const envValues = app.node.tryGetContext(envKey);

const managePhoneNumbersStack = new ManagePhoneNumbersStack(
  app,
  `${envValues.env}-${projectName}-managePhoneNumbersStack`,
  {
    envName: envValues.env,
    projectName: projectName,
    authorityManagementChannelId: envValues.authorityManagementChannelId,
  }
);

const slackAppRouterStack = new SlackAppRouterStack(
  app,
  `${envValues.env}-${projectName}-SlackAppRouterStack`,
  {
    envName: envValues.env,
    projectName: projectName,
    authorityManagementChannelId: envValues.authorityManagementChannelId,
    managePhoneNumbersStateMachine:
      managePhoneNumbersStack.managePhoneNumbersStateMachine,
  }
);
