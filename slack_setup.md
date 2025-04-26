# Slack Integration Setup Guide

This guide will help you set up the Slack integration for your Iris AI Team Interactor.

## 1. Create a Slack App

1. Go to [Slack API Apps page](https://api.slack.com/apps)
2. Click "Create New App"
3. Choose "From scratch"
4. Enter a name for your app (e.g., "Iris") and select your workspace
5. Click "Create App"

## 2. Configure Basic Information

1. In the "Basic Information" section, note your App ID, Client ID, and Client Secret
2. Under "App Credentials" you'll find your Signing Secret

## 3. Set Up OAuth & Permissions

1. Navigate to "OAuth & Permissions" in the sidebar
2. Under "Bot Token Scopes", add the following scopes:
   - `chat:write` - Send messages from your app
   - `users:read` - View users in the workspace
   - `users:read.email` - Look up users by email
   - `channels:read` - View channels in the workspace
   - `groups:read` - View private channels
   - `im:read` - View direct messages
   - `mpim:read` - View group direct messages
   - `app_mentions:read` - View when your app is mentioned
   
3. Click "Install to Workspace" to authorize the app
4. After installation, note your Bot User OAuth Token (starts with `xoxb-`)

## 4. Enable Socket Mode

1. Go to "Socket Mode" in the sidebar
2. Toggle "Enable Socket Mode" to on
3. Give your app token a name (e.g., "Iris Socket")
4. Click "Generate" and note your App-Level Token (starts with `xapp-`)

## 5. Configure Event Subscriptions

1. Go to "Event Subscriptions" in the sidebar
2. Toggle "Enable Events" to on
3. Under "Subscribe to bot events" add the following events:
   - `message.channels` - Get notified when a message is posted to a channel
   - `message.groups` - Get notified when a message is posted to a private channel
   - `message.im` - Get notified when a direct message is posted
   - `app_mention` - Get notified when your app is mentioned

4. Click "Save Changes"

## 6. Add App to Channels

1. Open your Slack workspace
2. Navigate to the channels where you want to use Iris
3. Type `/invite @Iris` to add the bot to each channel

## 7. Configure Environment Variables

1. Add the following to your `.env` file:

```
SLACK_BOT_TOKEN=xoxb-your-bot-token
SLACK_APP_TOKEN=xapp-your-app-token
```

2. Make sure not to share these tokens publicly

## 8. Test the Integration

Run the test script to verify your setup:

```
python test_slack.py
```

## Common Issues

- **Authentication errors**: Double-check your tokens in the `.env` file
- **Permission errors**: Make sure you've added all required OAuth scopes
- **Socket Mode issues**: Verify Socket Mode is enabled and your SLACK_APP_TOKEN starts with `xapp-`
- **Event subscription errors**: Make sure the bot is subscribed to the necessary events

## Using the Integration

1. Start the Slack listener:
```
python slack_listener.py
```

2. Send messages to your bot in any channel it's been invited to
3. Try phrases like "create a task for reviewing the documentation" or "schedule a meeting with the team tomorrow" 