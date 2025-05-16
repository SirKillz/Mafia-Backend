# Use the official MYSQL Image
FROM mysql:8.0

# Copy the init script over
# We are placing this inside of a specific known directory to initialize the database
COPY init.sql /docker-entrypoint-initdb.d/

#Expose the default port 3306
EXPOSE 3306

# Set the mysql_data volume:
VOLUME ["var/lib/mysql"]