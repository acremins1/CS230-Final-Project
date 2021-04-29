"""
Name: Aidan Cremins
CS230: SN2
Data: National Parks in New York
"""

# Import the necessary libraries
import streamlit as st
import pandas as pd
import pydeck as pdk
import matplotlib.pyplot as plt
import urllib
from PIL import Image
import numpy as np

# Import the data from the .csv file into a data frame
df = pd.read_csv("National_Register_of_Historic_Places.csv")
# Remove duplicate values from this dataset. There seems to be some repeated locations which artificially inflates
# later statistics like number of locations per county.
df.drop_duplicates(subset=["Resource Name"],inplace=True)
# Display the page title
st.title("Analysis of New York Historical Sites")
# Get an image of the Statue of Liberty from the URL specified below. This is better than saving the image as a
#.jpeg and then opening with PIL since this program needs to be run on other computers. Information was found via:
# https://www.kite.com/python/answers/how-to-read-an-image-data-from-a-url-in-python
urllib.request.urlretrieve("https://api.time.com/wp-content/uploads/2015/06/150605-statue-of-liberty-10.jpg?\
quality=85&w=1024&h=512&crop=1","statueofliberty.png")
# Actually open the image and set its size
pic = Image.open("statueofliberty.png")
st.image(pic, width=600, height=500)
# Change the date column of the dateframe to be datetime objects to make graphing/analysis easier
df["National Register Date"] = pd.to_datetime(df["National Register Date"])
# Set up the radio button to allow users to make the initial decision if they have a specific register number
starter = st.radio("Do you have a National Register Number in mind? ", ("Yes", "No"))
# This function doesn't return anything but shows users the specific location of their register number

def display_specific_location():
    # Set up a text box for users to type their register number and then they hit the search button
    register_number = st.text_input("Enter the National Register Number: ")
    search_button = st.button("Search")
    if search_button == True:
        # As long as the register number is valid (in the dataframe), a new dataframe is created consisting of only
        # the row of the original dataframe where the register number matches
        if register_number in list(df["National Register Number"]):
            site_df = df[df["National Register Number"] == register_number]
        # Set up a map that shows only the location identified by the register number and zoomed in appropriately
            view_state_1loc = pdk.ViewState(
                            latitude=site_df["Latitude"].mean(),
                            longitude=site_df["Longitude"].mean(),
                            zoom = 9,
                            pitch = 0)
            layer_1loc = pdk.Layer('ScatterplotLayer',
                            data = site_df,
                            get_position = '[Longitude, Latitude]',
                            get_radius = 500,
            # The color of the point is set to red
                            get_color = [255,0,0], auto_highlight =True,
                            pickable = True)
            # Label the point on the map with the historic location's name and its register number
            tool_tip_1loc = {"html": "Historic Place Name:<br/> <b>{Resource Name}</b>\
                        <b> &nbsp Register Number:</b> {National Register Number}",
                        "style": { "backgroundColor": "green",
                                    "color": "white"}}
            map_1loc = pdk.Deck(
            # The map style is a topographical map which seems more appropriate when looking at historic sites,
            # many of which happen to be outdoors or near rivers, etc.
                map_style='mapbox://styles/mapbox/outdoors-v11',
                initial_view_state=view_state_1loc,
                layers=[layer_1loc],
                tooltip= tool_tip_1loc
            )
            # Actually create the chart and then display below the chart when the location was registered
            st.pydeck_chart(map_1loc)
            st.write(f"{site_df.iloc[0,0]} was registered in {site_df.iloc[0,2]}.")
        else:
            # If an incorrect register number is provided, display this error message
            st.write("Error. Not a valid National Register Number. Please try again.")

# This function also doesn't return anything, but shows a map where users can specify which category of sites they
# want to look at
def display_desired_location_type():
    # Make a subtitle for this section as we're focusing on general, statewide analysis
    st.markdown("## Statewide Analysis: ")
    # Create a nonexhaustive of possible site categories that users would be interested in focusing on
    site_categories = ["All", "Home", "Historic District", "Building", "Cemetery", "Bridge", \
                   "Religious Site", "Hotel/Inn", "Farm", "Park"]
    # Set up a radio button allowing users to pick between the categories
    site_type = st.radio("Select a historical site category: ", site_categories)
    # Establish an empty list to eventually store the names of locations within the desired category
    desired_names = []
    # Establish a series of non-exhaustive lists that contain keywords indicating membership of different categories
    home_keywords = ["cabin", "house", "residence", "cottage", "villa", "mansion", "estate", "homestead", "home",\
                     "manor"]
    historic_dist_keywords = ["historic district"]
    building_keywords = ["building", "hall", "courthouse", "armory", "library", "mill", "theater", "theatre", \
                         "center", "plant"]
    cemetery_keywords = ["cemetery"]
    bridge_keywords = ["bridge"]
    religious_sites_keywords = ["church", "chapel", "temple", "synagogue"]
    hotel_inn_keywords = ["hotel", "inn"]
    farm_keywords = ["farm", "barn", "farmhouse"]
    park_keywords = ["park"]
    # Create a function that requires a dataframe and list as inputs. It iterates through each row of the dataframe
    # and makes every word of the "Resource Name" column lowercase. If any of these words matches words in the
    # supplied list, then the entire value for "Resource Name" is appended to the desired_names() list. This
    # function then returns the desired_names list.
    def search_list(df, list):
        for index, row in df.iterrows():
            for i in range(len(list)):
                for word in row["Resource Name"].split(" "):
                    if word.lower() == list[i]:
                        desired_names.append(row["Resource Name"])
            else:
                pass
        return desired_names
    # Set up a blank dataframe called desired_df
    desired_df = pd.DataFrame()
    # Establish a series of if statements to subset the data by the specified user category. If no category is
    # specified (i.e. "All" is selected), then the desired_df is the same as df and all locations are shown.
    # If "Home" is selected, search_list() is run and searches through the dataframe and returns only names with
    # words in home_keywords.
    if site_type == "All":
        desired_df = df
    elif site_type == "Home":
        search_list(df, home_keywords)
    elif site_type == "Historic District":
        search_list(df, historic_dist_keywords)
    elif site_type == "Building":
        search_list(df, building_keywords)
    elif site_type == "Cemetery":
        search_list(df, cemetery_keywords)
    elif site_type == "Bridge":
        search_list(df, bridge_keywords)
    elif site_type == "Religious Site":
        search_list(df, religious_sites_keywords)
    elif site_type == "Hotel/Inn":
        search_list(df, hotel_inn_keywords)
    elif site_type == "Farm":
        search_list(df, farm_keywords)
    elif site_type == "Park":
        search_list(df, park_keywords)
# Add to the empty desired_df dataframe all rows from the main dataframe that contain a resource name in the
# list specified by the category radio button
    for i in range(len(desired_names)):
        desired_df = desired_df.append(df[df["Resource Name"] == desired_names[i]])
    # Set up a map that shows only the locations of the specified category
    view_state_category = pdk.ViewState(
        latitude=df["Latitude"].mean(),
        longitude=df["Longitude"].mean(),
        zoom = 6,
        pitch = 0)
    layer_category = pdk.Layer('ScatterplotLayer',
                    data = desired_df,
                    get_position = '[Longitude, Latitude]',
                    get_radius = 500,
                    # Again, the color of the point is set to red
                    get_color = [255,0,0], auto_highlight =True,
                    pickable = True)
    # Label the point on the map with the historic location's name and its register number
    tool_tip_category = {"html": "Historic Place Name:<br/> <b>{Resource Name}</b>\
                <b> &nbsp Register Number:</b> {National Register Number}",
                "style": { "backgroundColor": "green",
                            "color": "white"}}
    map_all = pdk.Deck(
        map_style='mapbox://styles/mapbox/outdoors-v11',
        initial_view_state=view_state_category,
        layers=[layer_category],
        tooltip= tool_tip_category
    )
    # Actually create the map chart
    st.pydeck_chart(map_all)

# This function sorts all of the values in the "County" column of the dataframe, orders them alphabetically, then
# only includes non-repeated ones to get an ordered list of county selections to be used in user interfaces
def find_unique_counties():
    df_alpha_county = df.sort_values(by=["County"])
    unique_counties = list(df_alpha_county["County"].drop_duplicates())
    return unique_counties

# This function creates a barchart that compares the number of historical sites in each county, ordered from most
# historical sites to the least. A slider is located above the barchart which controls how many of the top counties
# are included in the barchart.
def county_total_barchart():
    # Create the slider
    num_counties = len(find_unique_counties())
    num_counties = st.slider("", 1, num_counties, num_counties)
    # Create an empty dictionary and use it to store the number of historical sites per county
    county_count_dict ={}
    for index, row in df.iterrows():
        if row["County"] in county_count_dict.keys():
            county_count_dict[row["County"]] += 1
        else:
            county_count_dict[row["County"]] = 1
    # This function actually goes ahead and creates the barchart
    def create_county_total_barchart(dict, num):
        # Create an empty dictionary that gets filled according to how many values the user specifies via the
        # slider to show on the barchart
        dict_ordered = {}
        counter = 0
        for item in sorted(dict, key=dict.get, reverse=True):
            if counter < num:
                dict_ordered[item] = dict[item]
                counter += 1
        x = list(dict_ordered.keys())
        y = list(dict_ordered.values())
        # Outline the bars in navy blue for a better aesthetic look
        plt.bar(x, y, edgecolor="navy")
        plt.xlabel("County Name")
        # Set the x-axis labels to be vertical so that they all can fit. Also, automatically adjust the
        # fontsize so it gets bigger when there's fewer bars shown.
        plt.xticks(rotation=90, fontsize = min(310/num, 15))
        plt.ylabel("Number of Historical Sites")
        plt.title("Number of Historical Sites Per County")
        return plt
    # Write the number of counties included in the barchart above the chart to confirm the user's slider selection
    st.write(f"Include the top {num_counties} counties.")
    # Actually create the plot
    st.pyplot(create_county_total_barchart(county_count_dict, num_counties))

# This function doesn't return anything but shows a map of historical sites within the user's specified
# county. It then shows a barchart below the map that shows the number of historical sites registered per year
# for that county.
def display_desired_county(unique_counties):
    # Add a label to this section to signifiy that we're moving from overall statewide analysis to focusing on
    # a specific county
    st.markdown("## County Specific Analysis: ")
    # Set up a selection box where users can specify which county they want to look at
    county_selection = st.selectbox("Please select a county to view: ", unique_counties)
    # Establish a new dataframe that only includes data for the specified county
    county_df = df[df["County"] == county_selection]
    # Set up a map that shows only the locations of historical sites within the specified county
    view_state_county = pdk.ViewState(
        latitude=county_df["Latitude"].mean(),
        longitude=county_df["Longitude"].mean(),
        zoom = 8.5,
        pitch = 0)
    layer_county = pdk.Layer('ScatterplotLayer',
                    data = county_df,
                    get_position = '[Longitude, Latitude]',
                    get_radius = 200,
                    get_color = [255,0,0], auto_highlight =True,
                    pickable = True)
    tool_tip_county = {"html": "Historic Place Name:<br/> <b>{Resource Name}</b>\
                <b> &nbsp Register Number:</b> {National Register Number}",
                "style": { "backgroundColor": "green",
                            "color": "white"}}
    map_county = pdk.Deck(
        map_style='mapbox://styles/mapbox/outdoors-v11',
        initial_view_state=view_state_county,
        layers=[layer_county],
        tooltip= tool_tip_county    )
    # Actually display the map
    st.pydeck_chart(map_county)
    # Write below the chart how many historical sites the specified county has.
    st.write(f"{county_selection} County has {len(county_df)}\
    historical sites.")
    st.write(f"Check out some of the sites in {county_selection} County below!")
    output_df = county_df[["Resource Name","National Register Date"]]
    st.write(output_df.sort_values(by=["Resource Name"]))
    # This function actually creates the barchart
    def county_register_year_barplot(county_df, county_selection):
        # Create an empty dictionary and use it to determine how many sites were registered for each year
        # for the specified county.
        county_years = {}
        for index, row in county_df.iterrows():
            year = row["National Register Date"].year
            if year in county_years.keys():
                county_years[year] += 1
            else:
                county_years[year] = 1
        x = list(county_years.keys())
        y = list(county_years.values())
        # Again, outline the bars to have a better aesthetic look
        plt.bar(x, y, color = "cornflowerblue", edgecolor="navy")
        plt.xlabel("Year")
        # Again, adjust the x-axis labels so they're vertical and can all fit
        plt.xticks(rotation=90, fontsize = 6)
        plt.ylabel("Number of Historical Sites Registered")
        # Create a dynamic title that displays the selected county name
        plt.title(f"Number of Historical Sites Registered Per Year for {county_selection} County.")
        return plt
    # Actually show the chart
    plt.figure()
    st.pyplot(county_register_year_barplot(county_df, county_selection))

# The main function sets up the whole logical flow of this program.
def main():
    # If the user selects that yes, they do have a national register number in mind (the default), run the function
    # that accepts a register number input and displays that one point in a graph
    if starter == "Yes":
        display_specific_location()
    # If the user selects no and wants just general analysis, run the rest of the functions in the specified order
    # to let the user start with overall statewide analysis, and then move to county-specific analysis
    else:
        display_desired_location_type()
        find_unique_counties()
        county_total_barchart()
        display_desired_county(find_unique_counties())

# Call the main function to run the program
main()
