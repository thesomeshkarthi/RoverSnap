# RoverSnap

Video Demo: https://youtu.be/uyfwfN7zf3A


Description:
RoverSnap is a flask-based web application that allows users to sign up and browse through the NASA Mars Rover API for Mars Rover captures. Users can search for images that they find interesting by selecting a date and a rover to look at. These images can then be saved to the user's scrapbook, which is a public profile that can then be found by other users, (similar to a blog or social media page). When saving Mars rover pictures to their scrapbook, users have the option to add a caption and title similar to a traditional post on other social media platforms. These images and captions can then be reposted/resaved by other users.

application.py is the controller of the website and it is where all of the flask routes are handled. This includes generating the dynamic search pages and login screens. It is also where the API is called when searching for Mars rover pictures by date and rover name. I used Python because it is a language I am familiar with. Most of the work found in this file involves rearranging variables and passing different variables that needs to get displayed through the "return render template" code.

helpers.py is an extension of application.py and it has useful functions that are called in the latter. This includes calling the API and retrieving information such as image URLs and SOL information.

about.html is the HTML page that displays the credits for this project. It is not dynamic, but it does use Bootstrap to display the different cards.

apology.html is the generic cs50 error page that helped me create the project and troubleshoot potential errors.

index.html is the main page where users can fill out the form with the action "/". It takes in user info such as the date and name of the rover, which is then passed into application.py and returned via a Jinja loop that displays all the API results.

layout.html is the standard header that is displayed on all pages via a Jinja extension. It features the different links and pages of the website.

login.html is the login page for the website, which uses a form to retrieve user info and check the login validity through application.py. If an error is found, an alert is passed back to the page and displayed at the top via the flashed messages. The category of the message determines if it is either successful, (a new account is created shows the green alert), or if is a failure, (an incorrect username or password is inputted).

register.html is very similar in nature to the login page. It also uses a form which is then passed through application.py with the "/register" POST route.

scrapbook.html is where users can view their own scrapbook or other scrapbooks. Depending on what information is passed through the template depending on the flask route, this page will either output the user's own scrapbook or another's scrapbook. In addition, it could also output the user's scrapbook in a gallery view or the classic view. There are Jinja loops to handle all of the different possibilities mentioned.

Overall, I am happy with how the design of the web app turned out. I felt that it was very intuitive and self explanatory. I also enjoyed how minimal and modern it looks. It was interesting to manipulate various SQL tables in a way that was best to present information through the Flask templates. I had to make a table based on the username as well as separate user tables so search queries wouldn't overlap with one another if multiple people were using the app at once. As of right now, none of the tables are too long and it seems like this program can definitely fit over 100 users.

I am currently working on a way to publicly host this program via PostgreSQL and Heroku. Wish me luck! A huge thank you to the cs50 team and @SamimOnline at BootSnipp for the login design template.
