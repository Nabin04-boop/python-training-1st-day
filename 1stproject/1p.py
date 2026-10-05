def calculate_production_time(quantity, minutes_per_garment, workers, effieciency):
    total_work_mintues = quantity * minutes_per_garment
    theoritical_minutes = total_work_mintues / workers
    actual_minutes = theoritical_minutes / (effieciency/100)
    hours = actual_minutes / 60
    return hours

print("=== Garment Productoin  time Prdictor ===")
quantity = int(input("Quantity: "))
minutes = float(input("Munites per garment: "))
workers = int(input("workers:" ))
effieciency = float(input("Effieciency: "))

calculated_hurs = calculate_production_time(quantity, minutes, workers, effieciency)
print(f"\n Estimated Production Time: {calculated_hurs:.2f} hours" )
