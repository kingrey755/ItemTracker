import streamlit as st
from minio import Minio
from minio.error import S3Error
import json
import uuid
import io

minio_client = Minio(
    "play.min.io",
    access_key="Q3AM3UQ867SPQQA43P2F",
    secret_key="zuf+tfteSlswRu7BJ86wekitnifILbZam1KYY3TG",
    secure=True
)

if "bucketName" not in st.session_state:
    st.session_state.bucketName = "sapra7751622"

if "currentScreen" not in st.session_state:
    st.session_state.currentScreen = "home"

try:
    if not minio_client.bucket_exists(st.session_state.bucketName):
        minio_client.make_bucket(st.session_state.bucketName)
except S3Error as e:
    print("Error occurred:", e)

st.set_page_config(page_title="Item Tracker", page_icon="logo.png")



def sidebar():
    st.sidebar.title("Navigation")
    screen = st.sidebar.pills("Go to", ["Home", "Add Item", "Update Item", "Delete Item"]) 

    if screen is None:
        return   
    st.session_state.currentScreen = screen.lower().replace(" ", "_")

    print("Current Screen:", st.session_state.currentScreen)

sidebar()

def homeScreen():
    st.title("Rama & Besties Item Tracker - Home")
    st.header("Items:")

    objects = minio_client.list_objects(
        st.session_state.bucketName,
        prefix="items/",
        recursive=True
    )

    cols = st.columns(3)
    idx = 0

    for obj in objects:
        response = minio_client.get_object(st.session_state.bucketName, obj.object_name)
        item = json.loads(response.read())

        with cols[idx]:
            with st.container(border=True):
                st.subheader(item["name"])
                st.caption(f"{item['location']}")

        idx = (idx + 1) % 3


def addItemScreen():
    st.title("Rama & Besties Item Tracker - Add Item")
    item = st.text_input("Item: ")
    location = st.text_input("Location: ")

    item_data = {
        "id": str(uuid.uuid4()),
        "name": item,
        "location": location
    }

    json_bytes = json.dumps(item_data).encode("utf-8")

    object_name = f"items/{item_data['id']}.json"

    if st.button("Add Item"):
        minio_client.put_object(
            "sapra7751622",
            object_name,
            data=io.BytesIO(json_bytes),
            length=len(json_bytes),
            content_type="application/json"
        )

        st.success("Uploaded Successfully!")
        st.balloons()

def updateItemScreen():
    st.title("Rama & Besties Item Tracker - Update Item")

    allItems = minio_client.list_objects(
        st.session_state.bucketName,
        prefix="items/",
        recursive=True
    )

    itemFilesNames = []
    items = []

    for obj in allItems:
        if not obj.object_name.endswith(".json"):
            continue 

        data = minio_client.get_object(st.session_state.bucketName, obj.object_name).read()

        if not data.strip():
            continue

        item = json.loads(data)
        items.append(item)
        itemFilesNames.append(obj.object_name)

    if not items:
        st.warning("No Items To Update")
        return

    itemNames = [item["name"] for item in items]
    selectedName = st.selectbox("Select an item to update", itemNames)

    index = itemNames.index(selectedName)
    selectedItem = items[index]
    selectedFile = itemFilesNames[index]

    newName = st.text_input("Name", value=selectedItem["name"])
    newLocation = st.text_input("Location", value=selectedItem["location"])

    if st.button("Save Changes"):
        updated = selectedItem
        updated["name"] = newName
        updated["location"] = newLocation

        encoded = json.dumps(updated).encode("utf-8")

        minio_client.put_object(
            st.session_state.bucketName,
            selectedFile,
            data=io.BytesIO(encoded),
            length=len(encoded),
            content_type="application/json"
        )

        st.success("Updated Successfully!")
        st.balloons()


        




def deleteItemScreen():
    st.title("Rama & Besties Item Tracker - Delete Item")

    allItems = minio_client.list_objects(
        st.session_state.bucketName,
        prefix="items/",
        recursive=True
    )

    itemFilesNames = []
    items = []

    for obj in allItems:
        if not obj.object_name.endswith(".json"):
            continue 

        data = minio_client.get_object(st.session_state.bucketName, obj.object_name).read()

        if not data.strip():
            continue

        item = json.loads(data)
        items.append(item)
        itemFilesNames.append(obj.object_name)

    if not items:
        st.warning("No Items To Delete")
        return

    itemNames = [item["name"] for item in items]
    selectedName = st.selectbox("Select an item to delete", itemNames)

    index = itemNames.index(selectedName)
    selectedItem = items[index]
    selectedFile = itemFilesNames[index]

    with st.popover("DELETE ITEM"):
        if st.button("Delete"):
            
            minio_client.remove_object(st.session_state.bucketName, selectedFile)

            st.success("Deleted Successfully!")
            st.balloons()

if st.session_state.currentScreen == "home":
    homeScreen()

elif st.session_state.currentScreen == "add_item":
    addItemScreen()


elif st.session_state.currentScreen == "update_item":
    updateItemScreen()

elif st.session_state.currentScreen == "delete_item":
    deleteItemScreen()


