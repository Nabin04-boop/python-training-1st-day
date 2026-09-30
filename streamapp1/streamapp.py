import streamlit as st 
st.title("My First Streamlit App")
name = st.text_input("Enter name:")
if name: 
    st.write(f"Hello, {name}!")
    num = st.slider("Pick a number", 0, 100)
clicked = st.button("Calculate")
agree = st.checkbox("I agree to the terms")
fruit = st.selectbox("Favorate fruit", ["Apple", "Banana", "Mango"])
co11, co12 = st.columns(2)
with co11: 
    st.write("leftside")
with co12: 
    st.write("Rightside")