import re
import pandas as pd

def preprocess(data):
    pattern = r'\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}\s?(?:AM|PM)\s-\s'

    dates = re.findall(pattern, data)        # full datetime strings
    messages = re.split(pattern, data)[1:]   # messages after each datetime

    # sanity check
    if len(dates) != len(messages):
        raise ValueError(f"Dates ({len(dates)}) and Messages ({len(messages)}) count mismatch")

    df = pd.DataFrame({'user_message': messages, 'message_date': dates})

    # clean and convert dates
    df['message_date'] = df['message_date'].str.replace('\u202f', ' ', regex=True)
    df['message_date'] = pd.to_datetime(df['message_date'], format='%m/%d/%y, %I:%M %p - ')
    df.rename(columns={'message_date': 'date'}, inplace=True)

    # split user and message
    users, msgs = [], []
    for msg in df['user_message']:
        entry = re.split(r'([\w\W]+?):\s', msg, maxsplit=1)
        if len(entry) > 2:
            users.append(entry[1])
            msgs.append(entry[2])
        else:
            users.append('group_notification')
            msgs.append(entry[0])

    df['user'] = users
    df['message'] = msgs
    df.drop(columns=['user_message'], inplace=True)

    # extract datetime features
    df["year"] = df["date"].dt.year
    df["month"] = df["date"].dt.month_name()
    df["day"] = df["date"].dt.day
    df["hour"] = df["date"].dt.hour
    df["minute"] = df["date"].dt.minute

    return df