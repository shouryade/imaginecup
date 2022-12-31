docker build -t medidoor .
docker run -d --name medidoor-client -p 5390:5390 medidoor