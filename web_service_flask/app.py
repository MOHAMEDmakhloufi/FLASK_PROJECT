from flask import Flask, render_template, request

import time
app = Flask(__name__)


@app.route('/')
def base():
    return render_template('base.html')

def validation(request):
    price1= float(request.form['prices'])
    price2 = float(request.form['prices2'])
    return price1 > price2

def get_item_from_db(request):
    import mysql.connector
    # start create connection
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="scraping_cars"
    )
    mycursor = mydb.cursor()
    # end create connection
    price1 = float(request.form['prices'])
    price2 = float(request.form['prices2'])
    if request.form['modele'] :
        mycursor.execute(
        "SELECT *  FROM cars_info WHERE name like %s and price BETWEEN %s and %s",
        ('%'+request.form['modele']+'%', price1, price2))
    else :
        mycursor.execute(
            "SELECT *  FROM cars_info WHERE  price BETWEEN %s and %s",
            (price1, price2))
    l= list(mycursor.fetchall())

    return list(map(lambda car: list(car), l))


def sort_cars(list_cars):
    print(list_cars)
    normalization = lambda old, min, max: float((float(old) - min) / (max - min) if (max - min) != 0 else 1)
    un_normalization = lambda new, min, max: int(new*(max - min) + min)
    list_prices= list(map(lambda car : car[3], list_cars))
    min_prices, max_prices= min(list_prices), max(list_prices)
    list_date = list(map(lambda car: int(car[4]), list_cars))
    min_date, max_date = min(list_date), max(list_date)
    list_kilo = list(map(lambda car: car[5], list_cars))
    min_kilo, max_kilo = min(list_kilo), max(list_kilo)

    def tarnsform(item):
        item[3]= normalization(item[3], min_prices, max_prices)
        item[4] = normalization(item[4], min_date, max_date)
        item[5] = normalization(item[5], min_kilo, max_kilo)
        return item
    def un_tarnsform(item):
        item[3]= un_normalization(item[3], min_prices, max_prices)
        item[4] = un_normalization(item[4], min_date, max_date)
        item[5] = un_normalization(item[5], min_kilo, max_kilo)
        return item
    list_cars = list(map(tarnsform, list_cars))
    list_cars.sort(key=lambda item: item[3]- item[4]+item[5])
    list_cars = list(map(un_tarnsform, list_cars))
    return list_cars
@app.route('/', methods=['POST'])
def cars():
    #start validation
    if validation(request) :
        return base()
    #end validation

    #start get cars from db
    list_cars= get_item_from_db(request)
    #end get cars from db
    best_1, best_2, best_3=[], [], []
    if len(list_cars) > 0 :
        #start sort cars
        list_cars= sort_cars(list_cars)
        #end sort cars
        print(list_cars)
        best_1= list_cars.pop(0)
        if len(list_cars) >0 :
            best_2= list_cars.pop(0)
            if len(list_cars) > 0 :
                best_3 = list_cars.pop(0)
    return render_template('cars.html', list_cars= list_cars, best_1=best_1, best_2= best_2, best_3=best_3)

if __name__ == '__main__':
    app.run()
