#!/usr/bin/env python3

import requests
import json
import copy
import asyncio
import aiohttp

DEFAULT_FLAG = True

owner = "getify"
repo = "You-Dont-Know-JS"
branch = ''
sha = ''
repo_tree_json = ''
repo_tree = {}
folder_stack = []
image_extensions = ['.tif', '.tiff', '.bmp', '.jpg', 
                    '.jpeg', '.gif', '.png', '.eps', 
                    '.raw', '.cr2', '.nef', '.orf',
                    '.sr2', '.psd', '.xcf', '.ai',
                    '.cdr', '.apng', '.avif', '.jfif',
                    '.pjpeg', '.pjp', '.png', '.svg',
                    '.webp', '.ico', '.cur']

video_extensions = ['.webm', '.mkv', '.flv', '.vob',
                    '.ogv', '.ogg', '.drc', '.gifv',
                    '.mng', '.avi', '.mts', '.m2ts',
                    '.ts', '.mov', '.qt', '.wmv',
                    '.yuv', '.rm', '.rmvb', '.viv',
                    '.asf', '.amv', '.mp4', '.m4p',
                    '.m4v', '.mpg', '.mp2', '.mpeg',
                    '.mpe', '.mpv', '.m2v', '.svi',
                    '.3gp', '.3g2', '.mxf', '.roq',
                    '.nsv', '.f4v', '.f4p', '.f4a',
                    '.f4b']

audio_extensions = ['.aa', '.aac', '.aax', '.act',
                    '.aiff', '.alac', '.amr', '.ape',
                    '.au', '.awb', '.dss', '.dvf',
                    '.flac', '.gsm', '.iklax', '.ivs',
                    '.m4a', '.m4b', '.mmf', '.movpkg', 
                    '.mp3', '.mpc', '.msv', '.nmf',
                    '.ogg', '.oga', '.mogg', '.opus',
                    '.ra', '.rm', '.raw', '.rf64',
                    '.sln', '.tta', '.voc', '.vox',
                    '.wav', '.wma', '.wv', '.webm',
                    '.8svx', '.cda']

def is_image_audio_video(file_path_name):
    for i_ext in image_extensions:
        if file_path_name[0-len(i_ext):].lower() == i_ext:
            return True
    for v_ext in video_extensions:
        if file_path_name[0-len(v_ext):].lower() == v_ext:
            return True
    for a_ext in audio_extensions:
        if file_path_name[0-len(a_ext):].lower() == a_ext:
            return True
    return False

#async request and action
async def fetch_file(session, file_url):
    if is_image_audio_video(file_url):
        return "This is an Image/Audio/Video File\n\n\n"
    
    async with session.get(file_url) as response:
        if response.status == 200:
            return await(response.text()) + '\n\n\n'
        else:
            return "Unable to access File\n\n\n"

#create async http session and asynchronously get file contents
async def fetch_files(file_urls):
    async with aiohttp.ClientSession() as session:
        to_fetch = [fetch_file(session, file_url) for file_url in file_urls]
        return await asyncio.gather(*to_fetch)

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
    output_text += "File names: " + (", ".join(file_list) if file_list else "No Files Here")  + "\n"
    output_text += "Folder names: " + (", ".join(folder_list) if folder_list else "No Folders Here") + "\n\n"
    #Add File Contents
    file_path_list = []
    file_url_list = []
    for file in file_list:
        file_path = ref_tree[file]
        content_url = f"https://raw.githubusercontent.com/{owner}/{repo}/2nd-ed/{file_path}"
        # content_url = f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{file_path}"
        file_path_list.append(file_path + ":\n\n")
        file_url_list.append(content_url)
    #get file contents
    file_content_list = asyncio.run(fetch_files(file_url_list))
    for i in range(len(file_path_list)):
        output_text += file_path_list[i]
        output_text += file_content_list[i]
    #nodes to visit
    for i in reversed(folder_list):
        f_tree_copy = copy.deepcopy(f_tree)
        f_tree_copy.append(i)
        folder_stack_2.append(("/".join(f_tree_copy), f_tree_copy))

print(output_text)


#for private repos, use github API
#for public repos use raw github

#Next steps: #exception and error handling
#make it a CLI that can accept arguments etc.
#maybe ignore all video and image files for now
#then do the handlers for the markdown and ipynb file types
    #ipynb is essentially json
    #ipynb images are in png converted to base64 (need to convert back)
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

#exception handling, folder with no files

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



