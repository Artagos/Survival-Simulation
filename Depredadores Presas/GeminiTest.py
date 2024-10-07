import google.generativeai as genai
import os

genai.configure(api_key="AIzaSyBnk707kh7HMBeg8eGNwzbYHWxVBHkwYx0"   )

model = genai.GenerativeModel('gemini-1.5-flash')
response = model.generate_content("write a message to my friend giving some wise advice")
print(response)
print(response.text)