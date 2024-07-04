
<div align="center">

# srepene Patcher
<img src="https://github.com/repinek/srepene_patcher/assets/137826826/b480e149-8bd5-40e2-a26f-313eb78b5191" width="600" height="360"/> <br>
### Change the text in Fall Guys easily
</div>

## Note
> [!WARNING]  
> 
> MediaTonic has never banned for changed text, but there's always a chance it could happen.
>
> Use at your own risk, I am not responsible for possible bans.

## Introduction
srepene Patcher is a program that allows you to modify any strings in the Fall Guys game, and then save them to a content_v2 or .ptch file, using a PyQT5 GUI. The content_v2 editing is used to change strings, and does not trigger EAC. 

.ptch files are used to save the changed strings, so that after updating content_v2 you don't have to do it all over again, just apply your .ptch file

The idea was completely taken from [Pancake Patcher](https://gamebanana.com/tools/7382), also patches from Pancake Patcher can be applied by srepene Patcher as well.

## Features 
- Decode v2 content and view strings directly from the GUI
- Search strings by id and text
- Modify string texts and save the changes to the encoded content v2 file
- Save changes to a .ptch file
- Apply changes from a .ptch file 

## To use:
1. Open the content_v2.gdata (It is located at the path C:\Users\YOURNAME\Appdata\LocalLow\Mediatonic\FallGuys_client\)
2. Edit strings
3. Click "Save patch" to create a file that you will be able to use to bring your edits back to the editor, in the event of a content update resetting everything.
4. If you want to add your additions to an existing patch, open the existing one in the Add to Patch button.
5. Press save, and overwrite content_v2.gdata. This will add all the changes currently in the GUI to the game.

## TODO:
- rewrite all legacy code, do full logging 
- add comments
- theme switcher (maybe)
