#!/bin/sh

# $1 is the database name: LunchTime, SocialMenu
psql -f common/setup/facebook_email.pgsql $1 otnpostgres
