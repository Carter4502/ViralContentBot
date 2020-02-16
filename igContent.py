"""
A tool to find posts for instagram pages, input however many IG pages and what time to search in and this tool
will find the posts with the most potential to go viral for you to repost on your
page.

Attributes: PostID, Likes, Average Likes (of last 12 of users posts)

Viral Condition: Likes > (Average Likes * 0.6) + Average Likes
Viral Score: 1 - (Average Likes / Likes) [Higher viral score = higher chance to go viral]

ex. Avg Likes = 120 likes
	New Post = 300 likes
	Viral because 300 > 150
	Viral Score = 1 - (120 / 300) =  66.66 %

- Posts can be found from their post id with www.instagram.com/p/[POST ID]
- Test accounts to make sure its working properly, copy and paste (without quotes):
 "433 espn nba nfl bleacherreport houseofhighlights lakers celtics"

"""

import requests, json, sys
import urllib.request
import time
from bs4 import BeautifulSoup

def getboth(posts_info, likesOnPosts, idsOnPosts, time_imported): # return videos and images
	averageLikes = []
	for x in range(12):
		averageLikes.append(posts_info["ProfilePage"][0]["graphql"]["user"]["edge_owner_to_timeline_media"]["edges"][x]["node"]["edge_liked_by"]["count"])
		if ((int(time.time()) - int(posts_info["ProfilePage"][0]["graphql"]["user"]["edge_owner_to_timeline_media"]["edges"][x]["node"]["taken_at_timestamp"])) / (60*60*24)) < int(time_imported):
			likesOnPosts.append(posts_info["ProfilePage"][0]["graphql"]["user"]["edge_owner_to_timeline_media"]["edges"][x]["node"]["edge_liked_by"]["count"])
			idsOnPosts.append(posts_info["ProfilePage"][0]["graphql"]["user"]["edge_owner_to_timeline_media"]["edges"][x]["node"]["shortcode"])
	avgLikes = sum(averageLikes) / len(averageLikes)
	return likesOnPosts, idsOnPosts, avgLikes
def getphotos(posts_info, likesOnPosts, idsOnPosts, time_imported): # return only photos
	averageLikes = []
	for x in range(12):
		if posts_info["ProfilePage"][0]["graphql"]["user"]["edge_owner_to_timeline_media"]["edges"][x]["node"]["is_video"] == False:
			averageLikes.append(posts_info["ProfilePage"][0]["graphql"]["user"]["edge_owner_to_timeline_media"]["edges"][x]["node"]["edge_liked_by"]["count"])
			if ((int(time.time()) - int(posts_info["ProfilePage"][0]["graphql"]["user"]["edge_owner_to_timeline_media"]["edges"][x]["node"]["taken_at_timestamp"])) / (60*60*24)) < int(time_imported):
				likesOnPosts.append(posts_info["ProfilePage"][0]["graphql"]["user"]["edge_owner_to_timeline_media"]["edges"][x]["node"]["edge_liked_by"]["count"])
				idsOnPosts.append(posts_info["ProfilePage"][0]["graphql"]["user"]["edge_owner_to_timeline_media"]["edges"][x]["node"]["shortcode"])
	avgLikes = sum(averageLikes) / len(averageLikes)
	return likesOnPosts, idsOnPosts, avgLikes
def getvideos(posts_info, likesOnPosts, idsOnPosts, time_imported): # return only videos
	averageLikes = []
	for x in range(12):
		if posts_info["ProfilePage"][0]["graphql"]["user"]["edge_owner_to_timeline_media"]["edges"][x]["node"]["is_video"] == True:
			averageLikes.append(posts_info["ProfilePage"][0]["graphql"]["user"]["edge_owner_to_timeline_media"]["edges"][x]["node"]["edge_liked_by"]["count"])
			if ((int(time.time()) - int(posts_info["ProfilePage"][0]["graphql"]["user"]["edge_owner_to_timeline_media"]["edges"][x]["node"]["taken_at_timestamp"])) / (60*60*24)) < int(time_imported):
				likesOnPosts.append(posts_info["ProfilePage"][0]["graphql"]["user"]["edge_owner_to_timeline_media"]["edges"][x]["node"]["edge_liked_by"]["count"])
				idsOnPosts.append(posts_info["ProfilePage"][0]["graphql"]["user"]["edge_owner_to_timeline_media"]["edges"][x]["node"]["shortcode"])
	avgLikes = sum(averageLikes) / len(averageLikes)
	return likesOnPosts, idsOnPosts, avgLikes
def find_posts(username, bestposts, time_imported):
	page = "https://www.instagram.com/" + username
	response = requests.get(page)
	soup = BeautifulSoup(response.text, 'html.parser')
	texthtml = soup.get_text()
	indexs = texthtml.find("window._sharedData") + 21
	indexe = texthtml.find("null}]}") + 7
	user_information = texthtml[indexs:indexe] + "}"
	json_data = json.loads(user_information)
	posts_info = json_data["entry_data"]
	likesOnPosts = []
	averageLikes = []
	idsOnPosts = []
	if mediaType == "b": # if chose both
		likesOnPosts, idsOnPosts, averageLikes = getboth(posts_info, likesOnPosts, idsOnPosts, time_imported)
	elif mediaType == "p": # only photos
		likesOnPosts, idsOnPosts, averageLikes = getphotos(posts_info, likesOnPosts, idsOnPosts, time_imported)
	else: # only videos
		likesOnPosts, idsOnPosts, averageLikes = getvideos(posts_info, likesOnPosts, idsOnPosts, time_imported)
	for post in range(len(likesOnPosts)):
		if likesOnPosts[post] > averageLikes + (0.4 * averageLikes): # if it's considered a viral post
			viral_score = 1 - (averageLikes / likesOnPosts[post]) # viral score
			if viral_score > bestposts[0][1]: # if score higher than on current list exchange it
				bestposts.pop(0)
				bestposts.append([idsOnPosts[post], viral_score])
				bestposts.sort(key = lambda x: x[1])
	return bestposts
mediaType = ""
time_imported = ""
def run_intro():
	mediaType = input("Do you want just videos (v) just photos (p) or both (b)? ")
	time_imported = input("Within how many days should the post be? ")
	if mediaType not in ["v", "b", "p"]:
		print("error, only type v, b, or p")
	if not time_imported.isdigit():
		print("error, use only positive numbers for the days.")
	return time_imported, mediaType

while mediaType not in ["v", "b", "p"] or not time_imported.isdigit():
	time_imported, mediaType = run_intro()

pages_to_analyze = input("Type usernames separated by a space to analyze for viral content: ")
pageslist = pages_to_analyze.split(" ")
viralPostData = [["a", 0], ["b", 0], ["c", 0], ["d", 0], ["e", 0], ["f", 0], ["g", 0], ["h", 0], ["i", 0]] # empty list to start with
for user in pageslist:
	print(user)
	viralPostData = find_posts(user, viralPostData, time_imported)
for item in viralPostData:
	if item[1] != 0:
		print("Post: www.instagram.com/p/" + item[0] + " Score: " + str(item[1] * 100) + "\n")



