# Hello Camera

A sample add-on for Vigiora Server. It shows that community add-ons install and run on your server, and it is the smallest working example for people who want to write their own.

## What it does

For every camera you assign to it, Hello Camera adds one result with the label `hello` every 30 seconds. It does nothing else. It does not read video or sound.

## What it needs

- Vigiora Server with Docker on the machine that runs the add-on.
- Almost no resources: it runs on a Raspberry Pi 4.

## Permissions

- **See your cameras**: to know which cameras you assigned to it.
- **Add events and results**: to post its `hello` results.

## For developers

The source is about 80 lines in `src/hello_camera/__main__.py`. It was made with `vigiora-addon new` from the [Vigiora Add-on Kit](https://github.com/data-tamer/vigiora-addon-kit). To start your own add-on, use the [add-on template](https://github.com/data-tamer/vigiora-addon-template).

Run the tests with `pytest`, and check the repository with `vigiora-addon validate .` before you submit it.

## Licence

Apache-2.0.
