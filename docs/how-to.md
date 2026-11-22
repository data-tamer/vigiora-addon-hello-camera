# Hello Camera: how to set it up and use it

This guide is shown to the people who install your add-on. Write it for them.

## What it does

Hello Camera posts a result with the label `hello` for every camera you assign to it, every 30 seconds. It does nothing else. It is meant to show that an add-on is installed and working.

## Set it up

1. Install the add-on from the Add-ons page of your Vigiora server.
2. Open the HAL page of the server and find `hello-camera`. It appears there once it has enrolled.
3. Assign the cameras you want it to greet.

![Placeholder screenshot of the add-on's page](../images/screenshot-1.png)

## Settings

| Setting | Where | Meaning |
|---|---|---|
| `GREETING` | Service-wide setting of `hello-camera` | The word in each result. Default `hello`. |
| `greeting` | A camera's own setting for this add-on | Overrides `GREETING` for that camera. |
| `HELLO_INTERVAL_SEC` | Environment of the container | Seconds between results. Default 30. |

A change to the assigned cameras or to `GREETING` is picked up within one polling interval (30 seconds by default).

## Stop it

Use Stop on the add-on's HAL page. It stays enrolled and keeps checking in, but posts nothing until you press Start.

## Permissions

It asks for `cameras:read` (to know which cameras are assigned) and `events:write` (to post its results). It does not read video.

## Troubleshooting

- **It does not appear on the HAL page.** Check the container's logs. "cannot enrol yet" means it cannot reach the server; "enrolment refused" means the key is wrong.
- **It appears but posts nothing.** No cameras are assigned to it, or it is stopped.
