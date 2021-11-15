Steps:
1. Start your mysql database server.
2. Start your apache server.
3. Go to your browser and type "127.0.0.1" in the address bar and click on phyMyAdmin.
4. Create a new database named 'blog'
5. Download flask_for_class.zip file from NYU Brightspace and unzip it.
6. Import simple.sql file in blog database. It will create two tables named 'user' and
'blog_post'.
7. Install flask and pymysql modules in python if required.
8. Run init1.py file using "python init1.py" command from the terminal.
  If you used a root password for your mysql database, edit the init1.py file to
  write that password in conn = pymysql.connect(host='localhost',
		                   port = 8889,
                       user='root',
                       password='root',
                       db='blog',
                       charset='utf8mb4',
                       cursorclass=pymysql.cursors.DictCursor) line.


9. Now create another tab in your browser, type "127.0.0.1:5000" in the address bar.
You should be able to see a web page with login and register links.
10. Now play with it. Look changes in the database tables.
