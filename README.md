# R3Think - Visualize the Connections Between Ideas

## Running Locally
### Note: To use offline database, you must build a complete copy of the Wikipedia database using [vulcan](https://github.com/DayOfThePenguin/vulcan)
1. Create & activate new virtualenv
```shell
virtualenv env
source activate-env
```
2. Install the required packages
```shell
python -m pip install -r requirements.txt
```
3. Start the PostgreSQL database (or start from vulcan if installed)
```shell
docker-compose up
```
4. Run the gunicorn server
```shell
uvicorn main:app --reload
```
