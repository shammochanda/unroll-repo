#!/usr/bin/env python3

import requests
import json
import copy
import asyncio
import aiohttp
import argparse
import sys

DEFAULT_BRANCH_FLAG = True

owner = ""
repo = ""
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

parser = argparse.ArgumentParser()

parser.add_argument("owner", nargs=1, help="Owner of Repo to Unroll")
parser.add_argument("name", nargs=1, help="Name of Repo to Unroll")
parser.add_argument("-b", "--branch", nargs=1, help="Name of Specific Branch")

args = parser.parse_args()

owner = args.owner[0]
repo = args.name[0]

if args.branch:
    branch = args.branch[0]
    DEFAULT_BRANCH_FLAG = False

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

#parse python notebooks
def handle_ipynb(file_json):
    output_text = ""
    file_contents = file_json["cells"]
    for cell in file_contents:
        cell_type = cell["cell_type"].title()
        output_text += f"Cell Type: {cell_type}\n\n"
        output_text += "Cell Source:\n\n" + "".join(cell["source"]) + "\n\n"
        #parse cell outputs
        if cell_type == "Code":
            output_text += "Cell Output:\n\n"
            if cell["outputs"]:
                for output in cell["outputs"]:
                    output_type = output["output_type"]
                    if output_type == "stream":
                        output_text += "".join(output["text"]) + "\n"
                    elif output_type == "execute_result":
                        output_text += "".join(output["data"]["text/plain"]) + "\n\n"
                    elif output_type == "display_data":
                        output_text += "Image Outputted\n\n" + "".join(output["data"]["text/plain"]) + "\n\n"
            else:
                "No Cell Output\n\n"
    return output_text


#async request and action
async def fetch_file(session, file_url):
    if is_image_audio_video(file_url):
        return "This is an Image/Audio/Video File\n\n\n"
    
    async with session.get(file_url) as response:
        if response.status == 200:
            #check ipynb here
            if file_url[-6:] == ".ipynb":
                file_json = await(response.json(content_type=None))
                file_contents = handle_ipynb(file_json)
                return file_contents + "\n\n\n"
            else:
                return await(response.text()) + '\n\n'
        else:
            return "Unable to access File\n\n\n"

#create async http session and asynchronously get file contents
async def fetch_files(file_urls):
    async with aiohttp.ClientSession() as session:
        to_fetch = [fetch_file(session, file_url) for file_url in file_urls]
        return await asyncio.gather(*to_fetch)

#Getting Branch Name
if DEFAULT_BRANCH_FLAG:
    url = f"https://api.github.com/repos/{owner}/{repo}"
    response = requests.get(url)
    if response.status_code == 200:
        branch = response.json()['default_branch']
    else:
        sys.exit("Invalid Repo Name or Owner")

#Getting SHA for the branch of this repo
url = f"https://api.github.com/repos/{owner}/{repo}/branches/{branch}"
response = requests.get(url)
if response.status_code == 200:
    sha = response.json()["commit"]["sha"]
else:
    sys.exit("Invalid Repo Name, Owner or Branch")

#Getting the git tree for the branch of this repo
url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/{sha}?recursive=1"
response = requests.get(url)
if response.status_code == 200:
    repo_tree_json = response.json()['tree']
else:
    sys.exit("Unable to Obtain Git Tree")


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
        content_url = f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{file_path}"
        file_path_list.append(file_path + " Contents:\n\n")
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