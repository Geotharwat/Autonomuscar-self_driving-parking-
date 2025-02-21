docker compose up -d 
until $(curl --output /dev/null --silent --head --fail http://127.0.0.1); do
    printf '.'
    sleep 1
done
cd control
python3 main.py