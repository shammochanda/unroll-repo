#!/usr/bin/env python3

import requests
import json

DEFAULT_FLAG = True

owner = "getify"
repo = "You-Dont-Know-JS"
branch = ''
sha = ''

#Getting Branch Name
if DEFAULT_FLAG:
    url = f"https://api.github.com/repos/{owner}/{repo}"
    response = requests.get(url)
    if response.status_code == 200:
        branch = response.json()['default_branch']
    else:
        print('Error')

url = f"https://api.github.com/repos/{owner}/{repo}/branches/{branch}"
response = requests.get(url)
if response.status_code == 200:
    sha = response.json()["commit"]["sha"]
else:
    print("Error")

url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/{sha}?recursive=1"
response = requests.get(url)
if response.status_code == 200:
    data = response.json()

    with open("output.json", "w") as file:
        json.dump(data, file, indent=3)
else:
    print("Error")

#TO IMPLEMENT

#specify which branch
#if branch not specified use default branch:
#https://api.github.com/repos/{owner}/{repo} and then navigate to "default_branch"
#of returned JSON

#how to get tree_sha for tree: 
#https://api.github.com/repos/{owner}/{repo}/branches/{branch_name}


#things to implement first:
#obtain filelist - git tree with github api: https://docs.github.com/en/rest/git/trees?apiVersion=2022-11-28
#https://api.github.com/repos/{owner}/{repo}/git/trees/{sha}?recursive=1
#use a BFS tree for file/folder list
#use DFS tree for going through the files and folders
#sort such that the files come first and the folders later

#obtain file contents with title - just use raw.github (need to handle notebooks though)

#parallelized GETS instead of sequential

#notebook handler (as well as notebook images)
    #notebook images are pngs (need to decode)
    #notebook is essentially like JSON, need to parse
#markdown handler (as well as markdown images) (README in particular)
    #markdown images are linked to assets

#include error handling


#BEHAVIOUR

#callable program with arguments
#e.g. unroll_repo -git link, unroll_repo -git -n(for names) owner repo_name
#e.g. unroll_repo directory_name (local)

#recursively breakdown files and folders in this format:
#Repo files and folders: folder1, folder2, file1, file2
#file1: gap and then file1 contents
#file2: gap and then file2 contents
#folder1 files and folders: etc. etc.
#folder1/file1: gap and then folder1/file1 contents
#exhaustively go through folder1
#folder2 files and folders: etc. etc.
#folder2/file1: gap and then folder2/file1 contents 



#FEATURES

#unroll from github
#unroll from other sites e.g. bitbucket
#unroll from just a folder list

#option to include images (pngs from notebooks and markdown as well)

#option for accessing private repo

#option for repo and owner or just using a link

#filetypes to ignore (e.g. .lock, .json)
#file titles to ignore (e.g. license, credits etc)

#option to initialize with your own github key (for private repo maybe?)



#hoppscotch



