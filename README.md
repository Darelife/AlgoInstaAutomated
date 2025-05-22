# AlgoInstaAutomated

Run [`main.py`](./main.py), and fill in the prompts

Run it using `python3 main.py`

### Docker
To save it as a docker image (couldn't upload it as it's too large for github), do `docker build -t algoinsta:latest .`, then to load the docker image, use `docker load -i algoinsta.tar`, and to run it do `docker run -it -v "$PWD/output:/app/output" algoinsta`

![ReadMeImage](ReadMeImage.png)
