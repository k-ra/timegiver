Timegiver Design Document
Kyra Mo and Carina Peng

To ensure effective communication and distinct operations between organizations and volunteers, we created two separate paths for registration and log-in. A distinct portal allows volunteers to register for activities without having to input information more than once, and gives organizations access to a function that posts volunteer openings and checks previously posted events and responses. 

Hence, the log-in information is stored on two different SQL tables, “orgs” and “users”. An additional “orginfo” table and form is presented on registration so organizations can detail a description, location, and mode of operation (online or in-person). 

When an organization is logged in, they can do three things: they can add new volunteer opportunities to the “openings’ table, view all previously added openings, and receive responses from user sign-ups. 

When an organization posts an opening, we allow for a mechanism to filter via the duration, date, type of activity, and description parameters. The “openings” tables houses these attributes for each posted event. Furthermore, the dropdown of activities such as “Education” and “Environment” allows for an effective filtering. We attempted to filter through the description via a keyword function that we coded in helpers.py. This function essentially uses the TF-IDF in Natural Language Processing (Term Frequency – Inverse document frequency) to find the most relevant words in a string of words. We were able to implement the function, but decided not to include it on the website due to the inevitable limits of term-frequency when the description is short. 

​To check for user responses, we iterate through the organization’s each posting and check for entries on the “signup” table, then insert them into a dictionary to be fed to the HTML. The organization will be able to access the user’s name and form of contact (email).

When a volunteer is logged in, they enter their time availability and preferences for the activities. We access the openings table and filter through activities that match these parameters, and display them dynamically on a table. 

Then, to register for an event, the user clicks the corresponding sign-up button, which stores the user_id and opening_id in the table “signup”. This is how the user and organization is connected. The user is then redirected to a page with all their registered upcoming events.

This is a general overview of the design behind each page or function currently in Timegiver!