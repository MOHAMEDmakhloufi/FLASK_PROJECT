def get_data_from_db(site_name, mycursor):
    mycursor.execute(
        "SELECT `name`, `image_url`, `price`, `date`, `kilometrage`, `carburant`, `href`, `site_name`  FROM cars_info WHERE `site_name`=%s",
        (site_name,))
    return set(mycursor.fetchall())
def database_NOTin_datascraping(database, new_data):
    data_to_delete = database.difference(new_data)
    if len(data_to_delete) == 1:
        data_to_delete.add('-')
    id_data_to_delete = tuple(map(lambda x: x[6], data_to_delete))
    return str(id_data_to_delete) if len(id_data_to_delete) > 0 else "('-')"

def datascraping_NOTin_database(database, new_data):
    data_to_insert = new_data.difference(database)
    return list(data_to_insert)

def delete_old_data(mycursor, mydb, id_data_to_delete):
    sql = "DELETE FROM `cars_info` WHERE `href` IN " + id_data_to_delete

    mycursor.execute(sql)
    mydb.commit()
    print(mycursor.rowcount, "record(s) deleted")

def insert_new_data(mycursor, mydb, data_to_insert):
    sql = "INSERT INTO cars_info (name, image_url, price, date, kilometrage, carburant, href, site_name) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"

    mycursor.executemany(sql, data_to_insert)
    mydb.commit()
    print(mycursor.rowcount, "record inserted. : ")

def database_communication(data, site_name) :
    import mysql.connector
    #start create connection
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="scraping_cars"
    )
    mycursor = mydb.cursor()
    #end create connection

    #start transform data from dict to set
    values = set(map(lambda x: tuple(x.values()), data))
    #end transform data from dict to set

    #start get data from database
    myresult = get_data_from_db(site_name, mycursor)
    #end get data from database

    #start find elements not in my new values
    id_data_to_delete= database_NOTin_datascraping(myresult, values)

    #end find elements not in my new values

    #start find elements not in the resulta
    data_to_insert= datascraping_NOTin_database(myresult, values)
    #end find elements not in the resulta


    #start delete old items
    delete_old_data(mycursor, mydb, id_data_to_delete)
    #end delete old items

    #insert_new items
    insert_new_data(mycursor, mydb, data_to_insert)

