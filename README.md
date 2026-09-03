# WOTD Bot

This is the code I used to create my Word Of the day bot. The bot tweets a word once a day with the help of GitHub actions and Google drive

## Dependencies

To get this project up and running, you'll need to install the following Python packages:

```sh
pip install -r requirements.txt
```

## Configuration

Credentials are read from environment variables. In GitHub Actions, create repository secrets with these names and map them to the job environment:

```text
WORD_API_KEY
TWITTER_API_KEY
TWITTER_API_SECRET
TWITTER_BEARER_TOKEN
TWITTER_ACCESS_TOKEN
TWITTER_ACCESS_TOKEN_SECRET
IMAGE_FILE_ID_NEW_YEARS_DAY
IMAGE_FILE_ID_VALENTINES_DAY
IMAGE_FILE_ID_EASTER
IMAGE_FILE_ID_HALLOWEEN
IMAGE_FILE_ID_CHRISTMAS
IMAGE_FILE_ID_INDEPENDENCE_DAY
IMAGE_FILE_ID_THANKSGIVING
IMAGE_FILE_ID_LABOR_DAY
IMAGE_FILE_ID_BASE
WORD_LIST
```
