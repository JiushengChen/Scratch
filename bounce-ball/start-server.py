from scratchclient import ScratchSession
from datetime import datetime
import os
import db
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(format="%(asctime)s | %(threadName)s | %(levelname)s | %(message)s", level=logging.INFO)
logging.basicConfig(format="%(asctime)s : %(levelname)s : %(message)s", level=logging.INFO)

dic = ["'", "<", ">", "?", "/", "`", " ", "=", "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z", "1", "2", "3", "4", "5", "6", "7", "8", "9", "0", ".", "-", "!", "@", "#", "$", "%", "^", "&", "*", "(", ")", "_", "+", "|", "\\", ":", ";"]

session = ScratchSession(os.environ["SCRATCH_USER_NAME"], os.environ["SCRATCH_CREDENTIAL"])
project = session.get_project(410226186)

## lots of other stuff
#print(session.get_project(450216269).get_comments()[0].content)
#print(session.get_studio(29251822).description)

connection = session.create_cloud_connection(410226186)

# e.g.,
# score=123, username=abc
# encodedTtl=3123091011 (position of a is 9, 1-based, and equal width digits)
def decode_(encodedTtl):
    n = int(encodedTtl[0])
    score = int(encodedTtl[1:1+n])
    encoded_username = encodedTtl[1+n:]
    username = decode_username_(encoded_username)
    return encoded_username, username, score

def decode_username_(encoded_username):
    decoded_username = [" "] * (len(encoded_username) // 2)
    for i in range(len(encoded_username) // 2):
        decoded_username[i] = dic[int("".join(encoded_username[2*i:2*i+2])) - 1] # 1-based to 0-based
    return "".join(decoded_username)

def encode_username_(username):
    username = username.lower()
    encoded_username = ["0"] * (len(username) * 2)
    for i in range(len(username)):
        n = dic.index(username[i]) + 1
        if n < 10:
            encoded_username[2*i+1] = str(n)
        else:
            t = str(n)
            encoded_username[2*i] = t[0]
            encoded_username[2*i+1] = t[1]
    return "".join(encoded_username)

username = "thi152s i1s a_te-st90@"
assert decode_username_(encode_username_(username)) == username

logger.info(f"Listening ...")
all_time_record_prev = 0
todays_record_prev = 0

@connection.on("set")
def on_set(variable):
    logger.info(f"Detected change: {variable.name}={variable.value}")
    if variable.name == "☁ tmp31415926a":
        # assume username is set and match the score, and decoded into int
        encoded_username, username, score = decode_(variable.value)
        logger.info(f"{encoded_username}, {username}, {score}")
        db_conn = db.create_connection()
        sql = f"SELECT highest_score FROM records WHERE username = '{username}'"
        ret = db.execute_read_query(db_conn, sql)
        utcnow = datetime.utcnow()
        update = False
        if ret:
            if score > ret[0][0]:
                sql = f"UPDATE records SET highest_score = ?, last_update_time_utc = ? WHERE username = ?"
                values = (score, utcnow, username)
                db.execute_query(db_conn, sql, values)
                update = True
        else:
            sql = f"INSERT INTO records (username, highest_score, last_update_time_utc) VALUES (?, ?, ?)"
            values = (username, score, utcnow)
            db.execute_query(db_conn, sql, values)
            update = True

        if update:
            sql = f"SELECT username, highest_score FROM records ORDER BY highest_score DESC LIMIT 1"
            ret = db.execute_read_query(db_conn, sql)
            all_time_record = ret[0][1]
            all_time_record_holder = ret[0][0]
            
            global all_time_record_prev
            global todays_record_prev
            if all_time_record > all_time_record_prev:
                logger.info(f"New all-time record! Champion is '{all_time_record_holder}' "
                            f"of score {all_time_record}")
                connection.set_cloud_variable("all-time champion encoded",
                        encode_username_(all_time_record_holder))
                connection.set_cloud_variable("all-time highest", str(all_time_record))
                all_time_record_prev = all_time_record

            sql = f"SELECT username, highest_score FROM records WHERE " + \
                  f"DATE(last_update_time_utc) = DATE('now') ORDER BY highest_score DESC LIMIT 1"
            ret = db.execute_read_query(db_conn, sql)
            if ret:
                todays_record = ret[0][1]
                todays_record_holder = ret[0][0]
                if todays_record > todays_record_prev:
                    logger.info(f"Today's new record! Champion is '{todays_record_holder}' "
                                f"of score {todays_record}")
                    connection.set_cloud_variable("today's champion encoded",
                            encode_username_(todays_record_holder))
                    connection.set_cloud_variable("today's highest", str(todays_record))
                    todays_record_prev = todays_record
            else:
                connection.set_cloud_variable("today's champion encoded", "")
                connection.set_cloud_variable("today's highest", "0")
        db_conn.close()
