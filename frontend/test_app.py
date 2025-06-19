import streamlit as st

st.title("🏥 MediConnect AI - Test")
st.write("Hello! This is a test to see if Streamlit is working.")

if st.button("Test Button"):
    st.success("✅ Streamlit is working correctly!")
    
st.sidebar.write("Sidebar test")
st.write("If you can see this, the basic app is loading.")