# BRAINSTORM

# DONE

* using same method for documenting classes and functions as used in my recent to this project workout web application
* got it downloading... uhoh
* Version 1.0.2 --- working on getting thing to download files correctly

* Version 1.1.0 --- (IN PROGRESS) Should be able to auto scan and also scan emails in gmail. The Scan itself should be able to give you a general statement on how likely it is phishing or not and from what exactly it drew that conclusion.

# TO-DO

* Also it seems the way we are fixing the header and taking out key phrases is not good enough to make it unique so sometimes it thinks we already downloaded it...

# NOTES ABOUT SCAN

so problem with just using virus total is have to hardcode api key inside so would need to remember to take out everytime I use and stuff like that. Maybe add a way for the user to add their own virus total api key? (actually kind of cool idea) otherwise uses other types of scans anyway.
So far it looks like we are going to end up using machine learning or the like to make some heuristics checks on the extracted email data.