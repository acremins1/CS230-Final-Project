"""
Name: Aidan Cremins
CS230: SN2
Data: National Parks in New York
URL: https://share.streamlit.io/acremins1/cs230-final-project/main/finalproject.py
Note: The Statue of Liberty photo is missing from my project posted online since it was causing an error.
Description: This program is designed to accommodate two main types of users with very different needs. For
experts who know the specific national register number of a historical site that they want to analyze, they can
enter the national register number right away and get the site location on a map as well as information below
the chart about when it was registered. For users who are less familiar and just want to explore the data, they
can first look through various categories of sites. Next, they can see a barchart that shows which counties have
the most historical sites and can filter how many top counties to include. After that, they can choose a specific
county in New York and only see the county's historical sites on a map and in tabular form. Lastly, they can look
at another barchart that shows the number of historical sites registered per year for that county.
"""

# Import the necessary libraries
import streamlit as st
import pandas as pd
import pydeck as pdk
import matplotlib.pyplot as plt
import urllib
from PIL import Image


# Import the data from the .csv file into a data frame
df = pd.read_csv("National_Register_of_Historic_Places.csv")
# Remove duplicate values from this dataset. There seems to be some repeated locations which artificially inflates
# later statistics like number of locations per county.
df.drop_duplicates(subset=["Resource Name"],inplace=True)
# Display the page title
st.title("Analysis of New York Historical Sites")
# Change the date column of the dateframe to be datetime objects to make graphing/analysis easier
df["National Register Date"] = pd.to_datetime(df["National Register Date"])
# Set up the radio button to allow users to make the initial decision if they have a specific register number
starter = st.sidebar.radio("Do you have a National Register Number in mind? (try 03NR05176)! If not, \
hit \"No\" to explore all of New York\'s historical sites!", ("Yes", "No"))

# This function doesn't return anything but shows users the specific location of their register number
def display_specific_location():
    # Set up a text box for users to type their register number and then they hit the search button
    register_number = st.sidebar.text_input("Enter the National Register Number: ")
    search_button = st.sidebar.button("Search")
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
    st.write("Please select a category of sites using the option buttons on the left.")
    # Create a nonexhaustive of possible site categories that users would be interested in focusing on
    site_categories = ["All", "Home", "Historic District", "Building", "Cemetery", "Bridge", \
                   "Religious Site", "Hotel/Inn", "Farm", "Park"]
    # Set up a radio button allowing users to pick between the categories
    site_type = st.sidebar.radio("Select a historical site category: ", site_categories)
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
                    get_radius = 700,
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
# This function creates a barchart using a dictionary for the x and y values. There are default color and
# edgecolor parameters (outlining the bars), but these can be changed if needed. There's also two optional
# parameters, num controls how many top values are included in the barchart for the later barchart showing the
# top counties in terms of most historic sites. County is an optional parameter that is used in the later
# barchart that shows the number of historical sites registered for each year for a specific county. Lastly,
# there's parameters to specify the x-axis, y-axis, and title labels.
def create_barchart(dict, titlelab, xlab, ylab, num="", county="", color="cornflowerblue",edgecolor="navy"):
        # Use the dictionary keys and values for the x and y values
        x = list(dict.keys())
        y = list(dict.values())
        # Specify the color and outline of the bars
        plt.bar(x, y, color=color, edgecolor=edgecolor)
        # Use the xlab argument to have the appropriate x-axis label
        plt.xlabel(xlab)
        # Set the x-axis labels to be vertical so that they all can fit. Also, automatically adjust the
        # fontsize so it gets bigger when there's fewer bars shown.
        plt.xticks(rotation=90, fontsize = min(310/len(dict.keys()), 15))
        # Use the ylab and titlelab arguments to have the appropriate y-axis and title labels
        plt.ylabel(ylab)
        plt.title(titlelab)
        return plt
# This function creates a barchart that compares the number of historical sites in each county, ordered from most
# historical sites to the least. A slider is located above the barchart which controls how many of the top counties
# are included in the barchart.
def county_total_barchart():
    st.write("Use the slider below to select how many of the top counties to include in the barchart.")
    # Create the slider for users to pick how many counties are included
    num_counties = len(find_unique_counties())
    num_counties = st.slider("", 1, num_counties, num_counties)
    # Create an empty dictionary and use it to store the number of historical sites per county
    county_count_dict ={}
    for index, row in df.iterrows():
        if row["County"] in county_count_dict.keys():
            county_count_dict[row["County"]] += 1
        else:
            county_count_dict[row["County"]] = 1
    # Set up a new empty dictionary that will be filled with key, value pairs from the dictionary above after
    # its ordered by value. Also, num_counties (selected by users) will determine how many key, value pairs
    # are added to this new dictionary.
    dict_counties_ordered = {}
    counter = 0
    for item in sorted(county_count_dict, key=county_count_dict.get, reverse=True):
        if counter < num_counties:
            dict_counties_ordered[item] = county_count_dict[item]
            counter += 1
    # Write the number of counties included in the barchart above the chart to confirm the user's slider selection
    st.write(f"Include the top {num_counties} counties.")
    # Establish the labels for the below barcharts' x-axis, y-axis and title
    county_total_title = "Number of Historical Sites Per County"
    county_total_xlab = "County Name"
    county_total_ylab = "Number of Historical Sites"
    # Actually create the plot using the above-created create_barchart() function. Use the ordered dictionary
    # and above created labels for the chart. Also use the optional num parameter.
    st.pyplot(create_barchart(dict=dict_counties_ordered, num=num_counties,titlelab=county_total_title, \
                              xlab=county_total_xlab, ylab=county_total_ylab))
    # Run this line so that the next barchart is created on the same axis as the one above
    plt.figure()

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
    # Create a dictionary that goes through the dataframe that contains only rows for the specified county
    # and stores how many historical sites were registered for each year
    county_years = {}
    for index, row in county_df.iterrows():
        year = row["National Register Date"].year
        if year in county_years.keys():
            county_years[year] += 1
        else:
            county_years[year] = 1
    # Establish the labels for the below barcharts' x-axis, y-axis and title
    county_years_title=f"Number of Historical Sites Registered Per Year for {county_selection} County."
    county_years_xlab="Year"
    county_years_ylab="Number of Historical Sites Registered"
    # Create the barchart using the generic create_barchart() function with county_years as the dictionary.
    # Also uses the optional county parameter and doesn't use the default color or edgecolor arguments.
    # Lastly, it uses the labels created above.
    st.pyplot(create_barchart(county_years, county=county_selection, color="red", edgecolor="maroon",
                              titlelab=county_years_title, xlab=county_years_xlab, ylab=county_years_ylab))

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
