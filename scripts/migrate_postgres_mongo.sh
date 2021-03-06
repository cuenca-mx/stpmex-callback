#!/bin/bash

# Define basic functions
function print_info {
        echo -n -e '\e[1;36m'
        echo -n $1
        echo -e '\e[0m'
}

function print_warn {
        echo -n -e '\e[1;33m'
        echo -n $1
        echo -e '\e[0m'
}

print_info "Read parameters"

# Read parameters
while getopts u:h:p:P: option
do
case "${option}"
in
u) USER=${OPTARG};;
h) HOST=${OPTARG};;
P) PASS=${OPTARG};;
p) PORT=${OPTARG};;
esac
done

print_info "Will conect to: $USER:$PASS@$HOST:$PORT"

# Install postgres

print_info "Install postgres"

echo "deb http://apt.postgresql.org/pub/repos/apt/ stretch-pgdg main" > /etc/apt/sources.list.d/pgdg.list
wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add -
apt-get update
DEBIAN_FRONTEND=noninteractive apt-get -q -y install postgresql postgresql-contrib

# Install pandas

print_info "Install DEV"

make install-dev

# Read data from postgres and put it into a csv file
print_info "Connect to postgres and extract transactions"
psql "dbname=db host=${HOST} user=${USER} password=${PASS} port=${PORT} sslmode=require" -c "\copy (SELECT * FROM public.transactions) to 'transactions.csv' with csv header"

print_info "Connect to postgres and extract requests"
psql "dbname=db host=${HOST} user=${USER} password=${PASS} port=${PORT} sslmode=require" -c "\copy (SELECT * FROM public.requests) to 'requests.csv' with csv header"

print_info "Connect to postgres and extract events"
psql "dbname=db host=${HOST} user=${USER} password=${PASS} port=${PORT} sslmode=require" -c "\copy (SELECT * FROM public.events) to 'events.csv' with csv header"


# Load data into mongodb
print_info "Connect to mongodb and send info"

flask speid migrate-from-csv --transactions transactions.csv --events events.csv --requests requests.csv

# Wipe data
print_info "Delete temp files"
rm -f transactions.csv events.csv requests.csv
