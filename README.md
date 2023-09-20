# SalesWizz - Streamlit LLM Hackathon App

[![Open App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://saleswizz.streamlit.app/)

This app is a basic implementation of a user-identity-aware chatbot. It is trained on internal sales data and follows the company's policy for handling IAM (Identity and Access Management).

The model is trained on the fictional sales data including region, quarter, quota, profit, commission and revenue.

The model is trained on the following policy:

The sales data can only be shared with Account Executives or Directors.
Account Executives can only be provided with data from their region. For example, an Account Executive from North America cannot get EMEA data and vice versa.
No data must be shared with contractors, regardless of the role and region.
The Directors can access data from all the regions (global).
The model is instructed about the current user's identity and decides whether to share the data or not based on the policy. As a nice bonus, the app displays the current user's photo from the employee table in the chat window.

High level architecture:
![Example Image 1](https://i.postimg.cc/T1wcpLD4/saleswizz-diagram.png)


The chatbot is following the logic below:
![Example Image 2](https://i.postimg.cc/K86N8M3h/model-logic.png)


Example conversations:
![Example Image 3](https://i.postimg.cc/DySHTh9g/saleswizz-sample.png)
