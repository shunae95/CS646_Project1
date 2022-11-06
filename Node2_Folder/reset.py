import os
# print(os.listdir(f"{os.path.dirname(__file__)}/Node1_Folder/processed"),end= "\n\n\n")

node1Folder = os.listdir(f"{os.path.dirname(__file__)}/Node1_Folder/processed")
for file in node1Folder:
    if file.endswith(".json") and file != "f91a588226a79b5d40f3bb0012bf2b51b10fa3b3ebb82346d3f070191d983ae8.json":
        os.remove(f"{os.path.dirname(__file__)}/Node1_Folder/processed/{file}")
    elif file == "f91a588226a79b5d40f3bb0012bf2b51b10fa3b3ebb82346d3f070191d983ae8.json":
        os.rename(f"{os.path.dirname(__file__)}/Node1_Folder/processed/{file}",f"{os.path.dirname(__file__)}/Node1_Folder/pending/{file}")

node1Blocks = os.listdir(f"{os.path.dirname(__file__)}/Node1_Folder/")
for file in node1Blocks:
    if file.endswith(".json") and (file.startswith("B_") or file.startswith("signatures")):
        os.remove(f"{os.path.dirname(__file__)}/Node1_Folder/{file}")

node2Folder = os.listdir(f"{os.path.dirname(__file__)}/Node2_Folder/processed")
for file in node2Folder:
    if file.endswith(".json") and file != "f91a588226a79b5d40f3bb0012bf2b51b10fa3b3ebb82346d3f070191d983ae8.json":
        os.remove(f"{os.path.dirname(__file__)}/Node2_Folder/processed/{file}")
    elif file == "f91a588226a79b5d40f3bb0012bf2b51b10fa3b3ebb82346d3f070191d983ae8.json":
        os.rename(f"{os.path.dirname(__file__)}/Node2_Folder/processed/{file}",f"{os.path.dirname(__file__)}/Node2_Folder/pending/{file}")

node2Blocks = os.listdir(f"{os.path.dirname(__file__)}/Node2_Folder/")
for file in node2Blocks:
    if file.endswith(".json") and (file.startswith("B_") or file.startswith("signatures")):
        os.remove(f"{os.path.dirname(__file__)}/Node2_Folder/{file}")
# print(os.listdir(f"{os.path.dirname(__file__)}/Node2_Folder/processed"),end= "\n\n\n")
