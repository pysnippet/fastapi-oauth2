#!/bin/bash
cd ~/fastapi-oauth2/
git restore .
git pull
sudo rm -r /var/www/docs/fastapi-oauth2/
cd ~/fastapi-oauth2/docs/ && npm install && npm run build
sudo cp -r ~/fastapi-oauth2/docs/.vitepress/dist/ /var/www/docs/fastapi-oauth2/
