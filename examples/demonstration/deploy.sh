#!/bin/bash
cd ~/fastapi-oauth2/
git restore .
git pull

cd ~/fastapi-oauth2/examples/demonstration
echo "import main; from fastapi import FastAPI; app = FastAPI(); app.mount('/fastapi-oauth2', main.app)" > playground.py

sudo rm -r /var/www/playground/fastapi-oauth2/
sudo cp -r ~/fastapi-oauth2/examples/demonstration /var/www/playground/fastapi-oauth2/
sudo python3 -m pip install -r /var/www/playground/fastapi-oauth2/requirements.txt

# Update environment variables for production
ENV_FILE=/var/www/playground/fastapi-oauth2/.env
for ENV_KEY in OAUTH2_GITHUB_CLIENT_ID OAUTH2_GITHUB_CLIENT_SECRET OAUTH2_GOOGLE_CLIENT_ID OAUTH2_GOOGLE_CLIENT_SECRET;
do
  sudo python3 -c "from dotenv import set_key; set_key('${ENV_FILE}', '${ENV_KEY}', '${!ENV_KEY}')";
done

sudo service playground.fastapi-oauth2 restart
