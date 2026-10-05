import streamlit as st_lit
def calculate_production_time(quantity, minutes_per_garment, workers, effieciency):
    total_work_mintues = quantity * minutes_per_garment
    theoritical_minutes = total_work_mintues / workers
    actual_minutes = theoritical_minutes / (effieciency/100)
    hours = actual_minutes / 60
    return hours

st_lit.title("Garment Productoin time Prdictor")
quantity = st_lit.number_input("Quantity:", min_value = 0)
minutes = st_lit.number_input("Minutes per garment:", min_value = 0.1)
workers = st_lit.number_input("Workers:", min_value = 1)
efficiency = st_lit.number_input("Efficiency:", min_value = 0.1)

if st_lit.button("Calculate Production"):
    calculate_hours=calculate_production_time(quantity, minutes, workers, efficiency)
    st_lit.write("Estimated production time:", round(calculate_hours,2 )) 