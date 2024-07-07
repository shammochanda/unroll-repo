#!/usr/bin/env python3

import requests
import json
import copy

DEFAULT_FLAG = True

owner = "getify"
repo = "You-Dont-Know-JS"
branch = ''
sha = ''
repo_tree_json = ''
repo_tree = {}
folder_stack = []

#Getting Branch Name
if DEFAULT_FLAG:
    url = f"https://api.github.com/repos/{owner}/{repo}"
    response = requests.get(url)
    if response.status_code == 200:
        branch = response.json()['default_branch']
    else:
        print('Error')

#Getting SHA for the branch of this repo
url = f"https://api.github.com/repos/{owner}/{repo}/branches/{branch}"
response = requests.get(url)
if response.status_code == 200:
    sha = response.json()["commit"]["sha"]
else:
    print("Error")

#Getting the git tree for the branch of this repo
url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/{sha}?recursive=1"
response = requests.get(url)
if response.status_code == 200:
    repo_tree_json = response.json()['tree']
else:
    print("Error")


#Making Repo Tree
for item in repo_tree_json:
    while len(folder_stack) != 0:
        #match folder strings until match is found or no match
        folder_match_string = "/".join(folder_stack) + "/"
        folder_match_string_len = len(folder_match_string)
        #to ensure no indexing errors
        if folder_match_string_len > len(item['path']):
            folder_stack.pop()
            continue
        else:
            #match found, append accordingly
            if folder_match_string == item['path'][:folder_match_string_len]:
                ref_dict = repo_tree
                for folder in folder_stack:
                    ref_dict = ref_dict[folder]
                if item["type"] == 'tree':
                    ref_dict[item['path'][folder_match_string_len:]] = {}
                    folder_stack.append(item['path'][folder_match_string_len:])
                elif item["type"] == "blob":
                    ref_dict[item['path'][folder_match_string_len:]] = item['path']
                break
            #no match, try one level up
            else:
                folder_stack.pop()
                continue
    #this is not a nested file/folder, append to main list
    if len(folder_stack) == 0:
        if item["type"] == 'tree':
            repo_tree[item['path']] = {}
            folder_stack.append(item['path'])
        elif item["type"] == "blob":
            repo_tree[item['path']] = item['path']

output_text = ""
folder_stack_2 = [('Repo', [])]

#Parse Tree to Output Text
#DFS using Stack
while folder_stack_2:
    f, f_tree = folder_stack_2.pop()
    ref_tree = repo_tree
    file_list = []
    folder_list = []
    output_text += f"{f} files and folders:\n\n"
    #go in to subtree
    for i in f_tree:
        ref_tree = ref_tree[i]
    #iterate through subtree
    for k, v in ref_tree.items():
        if isinstance(v, dict):
            folder_list.append(k)
        else:
            file_list.append(k)
    output_text += "File names: " + ", ".join(file_list) + "\n"
    output_text += "Folder names: " + ", ".join(folder_list) + "\n\n"
    #nodes to visit
    for i in reversed(folder_list):
        if f_tree:
            f_tree_copy = copy.deepcopy(f_tree)
            f_tree_copy.append(i)
            folder_stack_2.append((i, f_tree_copy))
        else:
            folder_stack_2.append((i, [i]))

print(output_text)


#what to do if file list is empty
#what to do if folder list is empty

#iterate through them separately (parallelized gets for the files)

#Next steps: Organize in files then folders, attach the api request link
#exception and error handling
#make it a CLI that can accept arguments etc.
#then do the GETs, and parallelize them
#then do the handlers for the markdown and ipynb file types
#handle private repos
#testing


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

#tree parsing:
#if tree add it as a list with one item, also add tree name to a stack
#if blob encountered:
    #if tree stack empty, append to list
    #if tree stack not empty, check prefix of blob
        #check prefix iteratively
            #check all items in the stack first, then less than less
            #keep the stuff that match, pop the rest
                #after popping, maybe rearrange such that blobs come before trees?
            #index deep enough into the list (e.g. match 3 means index 3 deep)
            #add to that list
#append to list as tuples (blob_name, "blob"), ("tree_name", "tree")

#exception handling, folder with no files

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



