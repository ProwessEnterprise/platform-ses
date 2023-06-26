import pymysql.cursors
from dotenv import load_dotenv
import os

class EmailDatabase1:
    def __init__(self, host, user, password, database):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None
        self.cursor = None

    def connect(self):
        self.connection = pymysql.connect(host=self.host,
                                          user=self.user,
                                          password=self.password,
                                          database=self.database,
                                          cursorclass=pymysql.cursors.DictCursor)
        self.cursor = self.connection.cursor()
    
    def create_table(self):
        query = """CREATE TABLE IF NOT EXISTS emailinfo(
                   id BIGINT AUTO_INCREMENT PRIMARY KEY,
                   subject VARCHAR(255),
                   body text)"""
        self.cursor.execute(query)
        self.connection.commit()
   
    def insert_emailinfo(self, subject, body):
        query = """INSERT INTO emailinfo(subject, body)
                VALUES(%s,%s)"""
        self.cursor.execute(query,(subject, body))
        self.connection.commit()
    
    def get_all_emailinfo(self):
        query = "SELECT * FROM emailinfo ORDER BY id DESC LIMIT 1"
        self.cursor.execute(query)
        result = self.cursor.fetchall()
        emails = []
        for row in result:
            email = {
            "id": row['id'],
            "subject": row['subject'],
            "body": row['body']
            }
            emails.append(email)
        return emails
    
    def disconnect(self):
        if self.connection and self.cursor:
            self.cursor.close()
            self.connection.close()
            self.cursor = None
            self.connection = None
def main():
    load_dotenv()
    host_name = os.environ['host_name']
    user_name = os.environ['user_name']
    database_password = os.environ['database_password']
    database_name1 = os.environ['database_name1']

    db = EmailDatabase1(host_name, user_name, database_password, database_name1)
    db.connect()
    db.create_table()

    emails_query = "SELECT recipientname,employeeid FROM emails"
    db.cursor.execute(emails_query)
    emails_result = db.cursor.fetchall()
    for row in emails_result:
        recipientname = row['recipientname']
        employeeid = row['employeeid']
    
    assets_query = "SELECT assetid, assettype, assetmodel, dispatchdate FROM assets"
    db.cursor.execute(assets_query)
    assets_result = db.cursor.fetchall()
    for row in assets_result:
        assetid = row['assetid']
        assettype = row['assettype']
        assetmodel = row['assetmodel']
        dispatchdate = row['dispatchdate']

    
    recipient_name = recipientname
    employee_id = employeeid
    asset_id =assetid
    asset_type = assettype
    asset_model = assetmodel
    dispatch_date = dispatchdate
    
    subject = "Asset Tracking | {} | {} | Employee id: {}".format(asset_type, recipient_name, employee_id)
   
    if asset_type.lower() == "laptop":
        body_file_name = "laptopbody.html"
    elif asset_type.lower() == "printer":
        body_file_name = "printerbody.html"
    else:
        body_file_name = "modembody.html" 
    
    with open(body_file_name, "r") as body_file:
       body = body_file.read().format(recipient_name,asset_id, asset_type,asset_model, asset_id, dispatch_date)
    
   
    db.insert_emailinfo(subject,body)
    
    emails = db.get_all_emailinfo()
    print("ALL EMAILS:")
    print(emails)

    db.disconnect()

if __name__ == '__main__':
    main()
    
    

