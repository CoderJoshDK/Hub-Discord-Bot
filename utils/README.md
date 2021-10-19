# Purpose

## util.py

discord.py helper functions. 
 - GetMessage : This function sends an embed containing the params and then waits for a message to return
 - sendLog : send a message to the guild's log room
 - sendAdmin : send a message to the guild's admin room
 - getChannels : Get a list of channels from the data base and look at the searches
 - sendToImportantChannel : Try to send a message to the first availabe channel in a given list
 - dm_user : dm a user


## mongo.py

A helper file for using mongo db.
Class document aims to make using mongo calls easy, saves
needing to know the syntax for it. Just pass in the db instance
on init and the document to create an instance on
