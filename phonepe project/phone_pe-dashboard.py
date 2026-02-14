import sys
import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine
import requests
import json
import os

# ---------------------- Database connection ---------------------- #
engine = create_engine( "postgresql://dhivya10_user:Slgr1aoQEm59696HAu2lit0L5oNiDLTY@dpg-d5vgght6ubrc73cfnv5g-a.singapore-postgres.render.com/phonepe_db3" )



# ---------------------- Page Config ---------------------- #
st.set_page_config(layout='wide')
st.title("PHONEPE DATA VISUALIZATION & ANALYSIS")

# ---------------------- Sidebar ---------------------- #
with st.sidebar:
    select = st.selectbox("Main Menu", ["Home", "Data Exploration", "India Map visualization"])

# ---------------------- Home ---------------------- #
if select == "Home":
        st.title("📱 PhonePe Data Analysis Dashboard")

        st.markdown("---")

        st.subheader("About PhonePe")

        st.markdown("""
        PhonePe is one of India’s leading digital financial services platforms, enabling secure UPI-based transactions, 
        bill payments, merchant payments, insurance, and investment services. 

        With a strong nationwide presence, PhonePe has significantly accelerated digital payment adoption 
        and financial inclusion across India.
        """)

        st.markdown("---")

        st.subheader("About This Dashboard")

        st.markdown("""
        This dashboard analyzes PhonePe’s transaction, insurance, and user data to uncover meaningful insights, 
        trends, and state-wise performance patterns across India.  

        Through interactive visualizations and data exploration, it highlights regional transaction behavior, 
        insurance penetration, and user growth dynamics.
        """)


# ---------------------- Data Exploration ---------------------- #
elif select == "Data Exploration":

    tab1, tab2, tab3 = st.tabs(["Aggregated Data", "Map Data", "Top Data"])

    # ---------------------- Tab 1: Aggregated Data ---------------------- #
    with tab1:
        method = st.radio("Select the Data", ["Insurance", "Transaction", "User"])
        if method == "Insurance":
            st.header("Insurance Penetration and Growth Potential Analysis")
        # ---------------------- Insurance ---------------------- #
            def get_aggregated_insurance(engine):
                query = """
                    SELECT
                        "State",
                        SUM("Transaction_count") AS "Transaction_count",
                        SUM("Transaction_amount") AS "Transaction_amount"
                    FROM "agg_insurance"
                    GROUP BY "State";
                """
                df = pd.read_sql(query, engine)
                df = df.sort_values("Transaction_amount", ascending=False)
                return df

            
            df_all = get_aggregated_insurance(engine)
            if df_all.empty:
                    st.warning("No insurance transaction data available.")
            else:
             top_n = st.slider("Select Top/Bottom N State", 5, 20, 10)

            df_top = df_all.head(top_n)
            df_bottom = df_all.tail(top_n).sort_values("Transaction_amount", ascending=True)


            col1, col2 = st.columns(2)

                # Transaction Amount
            with col1:
                fig_top_amount = px.bar(
                df_top,
                x="State",
                y="Transaction_amount",
                color="Transaction_amount",
                title=f"Top {top_n} State - Insurance Amount"
            )
            st.plotly_chart(fig_top_amount, use_container_width=True,key="top_amount")

                # Transaction Count
            with col2:
                fig_top_count = px.line(
                df_top,
                x="State",
                y="Transaction_count",
                markers=True,
                title=f"Top {top_n} State - Insurance Count"
                )
                st.plotly_chart(fig_top_count, use_container_width=True,key="top_count")
            
            col3, col4 = st.columns(2)
            with col3:
                    fig_bottom_amount = px.bar(
                df_bottom,
                x="State",
                y="Transaction_amount",
                color="Transaction_amount",
                title=f"Bottom {top_n} State - Insurance Amount"
                )
                    st.plotly_chart(fig_bottom_amount, use_container_width=True)
            
            with col4:
                fig_bottom_count = px.line(
                df_bottom,
                x="State",
                y="Transaction_count",
                markers=True,
                title=f"Bottom {top_n} State - Insurance Count"
                )
                st.plotly_chart(fig_bottom_count, use_container_width=True)

            st.divider()
            st.subheader("State-wise Insurance Trend Over Year")
            State_df = pd.read_sql('SELECT DISTINCT "State" FROM "agg_insurance" ORDER BY "State";', engine)
            State = State_df["State"].tolist()

            selected_state = st.selectbox(
            "Select State for Trend Analysis",
            options=[""] + State,
            index=0
            )

            if selected_state:
                def get_state_year_trend(engine, state):
                    query = """
                    SELECT
                        "Year",
                        SUM("Transaction_count") AS transaction_count,
                        SUM("Transaction_amount") AS transaction_amount
                    FROM "agg_insurance"
                    WHERE "State" = %(state)s
                    GROUP BY "Year"
                    ORDER BY "Year";
                    """
                    return pd.read_sql(query, engine, params={"state": state})

                df_trend = get_state_year_trend(engine, selected_state)

                if df_trend.empty:
                    st.warning("No data available for this state.")
                else:
                    col5, col6 = st.columns(2)
                    with col5:
                        fig_trend_count = px.line(
                        df_trend,
                        x="Year",
                        y="transaction_count",
                        markers=True,
                        title=f"Insurance Count Trend in {selected_state}"
                     )
                        st.plotly_chart(fig_trend_count, use_container_width=True)

                    with col6:
                        fig_trend_amount = px.line(
                        df_trend,
                        x="Year",
                        y="transaction_amount",
                        markers=True,
                        title=f"Insurance Amount Trend in {selected_state}"
                        )
                        st.plotly_chart(fig_trend_amount, use_container_width=True)

         # ---------------------- Transaction ---------------------- 
        # 
        if method == "Transaction":

            st.header("Decoding Transaction Dynamics on PhonePe")

            # ----------------- Fetch Data Function ----------------- #
            def get_aggregated_transactions(engine):
                query = """
                SELECT
                "Year",
                "Quarter",
                "State",
                "Transaction_type",
                SUM("Transaction_count") AS "Transaction_count",
                SUM("Transaction_amount") AS "Transaction_amount"
                FROM "agg_transactions"
                GROUP BY "Year", "Quarter", "State", "Transaction_type"
                ORDER BY "Year", "Quarter";
                """
                df = pd.read_sql(query, engine)
                return df


            df = get_aggregated_transactions(engine)

            if df.empty:
                st.warning("No transaction data available.")
            else:
                all_State = sorted(df["State"].unique().tolist())
                selected_state = st.selectbox(
                    "Select State",
                options=all_State,
                index=0,
                help="Select a state to visualize its transactions over all Year"
                )

                if selected_state:
                    df_state = df[df["State"] == selected_state]

        # ----------------- Aggregate over time ----------------- #
                    df_time_amount = df_state.groupby(["Year", "Quarter"], as_index=False).agg({"Transaction_amount": "sum"})
                    df_time_count = df_state.groupby(["Year", "Quarter"], as_index=False).agg({"Transaction_count": "sum"})

                    col1, col2 = st.columns(2)

        # Transaction Amount over Year
                    with col1:
                        fig_amount_time = px.line(
                        df_time_amount,
                        x=df_time_amount.apply(lambda x: f"{x['Year']}-Q{x['Quarter']}", axis=1),
                        y="Transaction_amount",
                        markers=True,
                        title=f"{selected_state}: Transaction Amount Over Year",
                            labels={"y": "Transaction Amount", "x": "Year-Quarter"}
                            )
                        st.plotly_chart(fig_amount_time, use_container_width=True)

        # Transaction Count over Year
                    with col2:
                        fig_count_time = px.line(
                        df_time_count,
                        x=df_time_count.apply(lambda x: f"{x['Year']}-Q{x['Quarter']}", axis=1),
                        y="Transaction_count",
                        markers=True,
                        title=f"{selected_state}: Transaction Count Over Year",
                        labels={"y": "Transaction Count", "x": "Year-Quarter"}
                        )
                        st.plotly_chart(fig_count_time, use_container_width=True)

        # ----------------- Charts by Transaction Type ----------------- #
                    df_type_amount = df_state.groupby("Transaction_type", as_index=False).agg({"Transaction_amount": "sum"})
                    df_type_count = df_state.groupby("Transaction_type", as_index=False).agg({"Transaction_count": "sum"})

                    col3, col4 = st.columns(2)

                    with col3:
                        fig_amount_pie = px.pie(
                        df_type_amount,
                        names="Transaction_type",
                        values="Transaction_amount",
                        title=f"{selected_state}: Transaction Amount Distribution by Payment",
                        hole=0.3  # optional for donut style
                        )
                        st.plotly_chart(fig_amount_pie, use_container_width=True)

                    # Pie chart for Transaction Count
                    with col4:
                        fig_count_pie = px.pie(
                        df_type_count,
                        names="Transaction_type",
                        values="Transaction_count",
                        title=f"{selected_state}: Transaction Count Distribution by Payment",
                        hole=0.3  # optional for donut style
                            )
                        st.plotly_chart(fig_count_pie, use_container_width=True)


        # ----------------- Top Performing Transaction Type ----------------- #
                # ----------------- Top 5 & Bottom 5 State ----------------- #
                    st.subheader(f"Top Performing Payment Type in {selected_state}")

                    df_top_type = df_type_amount.sort_values(
                    "Transaction_amount", ascending=False
                    ).head(1)

                    fig_top_type = px.bar(
                     df_top_type,
                    x="Transaction_type",
                     y="Transaction_amount",
                    title=f"Top Payment Type by Amount in {selected_state}",
                    color="Transaction_type"
                        )

                    st.plotly_chart(fig_top_type, use_container_width=True)

                else:
                    st.info("Please select a state to display charts.")



        
        # ---------------------- User ---------------------- #
        if method == "User":
            st.header("Device Dominance and User Engagement Analysis")

    
    # Fetch all State for the selectbox
            all_State_df = pd.read_sql('SELECT DISTINCT "State" FROM agg_users ORDER BY "State";', engine)
            all_State = all_State_df["State"].tolist()

            selected_state = st.selectbox(
            "Select State",
                options=[""] + all_State,
                index=0,
                help="Select a state to visualize its users over all Year"
            )

            if selected_state:

        # ----------------- Function to fetch user data ----------------- #
                def get_users(engine, state):
                    query = """
                    SELECT
                    "Year",
                    "Brands",
                    AVG("Percentage") AS avg_percentage,
                    SUM("user_count") AS total_users
                            FROM agg_users
                    WHERE "State" = %(state)s
                    GROUP BY "Year", "Brands"
                    ORDER BY "Year", total_users DESC;
                    """
                    df = pd.read_sql(query, engine, params={"state": state})
                    return df

                df_state = get_users(engine, selected_state)

                    
                if df_state.empty:
                    st.warning("please select data for analysis")
                else:
                    st.dataframe(df_state, use_container_width=True)
                    
            
            
                    fig = px.bar(
                    df_state,
                    x="Year",
                    y="total_users",
                    color="Brands",
                    title=f"User Count by Brand over Year in {selected_state}"
                    )
                    st.plotly_chart(fig, use_container_width=True)


                    st.subheader(f"Top Brand by User Count in {selected_state}")
                # ----------------- Top Brand by Users ----------------- #
                    df_top_brand = df_state.groupby("Brands", as_index=False).agg({"total_users": "sum"})
                    df_top_brand = df_top_brand.sort_values("total_users", ascending=False).head(3)

                    fig_top_brand = px.bar(
                    df_top_brand,
                    x="Brands",
                    y="total_users",
                    title=f"Top 3 Brands by User Count in {selected_state}",
                    color="Brands"
                    )
                    st.plotly_chart(fig_top_brand, use_container_width=True)

                # ----------------- Underutilized Devices ----------------- #
                    df_underutilized = df_state.groupby("Brands", as_index=False)["avg_percentage"].mean().nsmallest(5, "avg_percentage")
                    st.subheader("Top 5 Underutilized Devices")
                    fig_underutilized = px.bar(
                    df_underutilized,
                    x="Brands",
                    y="avg_percentage",
                    color="Brands",
                    title="Underutilized Devices (Avg Share)"
                    )
                    st.plotly_chart(fig_underutilized, use_container_width=True)
                st.subheader("Top 5 States by Total Registered Users")
                df_top_states = pd.read_sql("""
                        SELECT
                        "State" as state,
                        SUM("user_count") AS total_users
                        FROM agg_users
                        GROUP BY "State"
                        ORDER BY total_users DESC
                        LIMIT 5;
                        """, engine)

                if not df_top_states.empty:
                        fig_top_states = px.line(
                        df_top_states,
                        x="state",
                        y="total_users",
                        markers=True,
                        title="Top 5 States by Registered Users",
                        )
                        st.plotly_chart(fig_top_states, use_container_width=True)
                else:
                        st.warning("No user data available for top states.")


    with tab2:
        map_method = st.radio(
        "Select the Data",
        ["Map Insurance", "Map Transaction", "Map User"]
        )
        #-----------Map user-------------
        if map_method == "Map User":

            st.header("User Engagement and Growth Strategy")
        # State Dropdown
        # -----------------------------
            all_State_df = pd.read_sql(
            'SELECT DISTINCT "State" FROM map_user ORDER BY "State";',
            engine
             )
            all_State = sorted(all_State_df["State"].tolist())

            selected_state = st.selectbox(
            "Select State",
            options=[""] + all_State,
            index=0,
            help="Select a state to visualize its users over all Year"
            )

        # -----------------------------
        # Selected State Year-Wise Data
        # -----------------------------
            if selected_state:
                def get_map_user(engine, state):

                    query="""
                        SELECT
                        "State",
                        "Districts",
                            "Year",
                        SUM("RegisteredUser") AS total_registered_users,
                        SUM("AppOpens") AS total_appopens
                            FROM map_user
                            WHERE "State" = %(state)s
                        GROUP BY "State","Districts","Year"
                        ORDER BY "Year";
                        """
             
                    df= pd.read_sql(query, engine, params={"state": state})
                    return df
                
                df_state= get_map_user(engine, selected_state)

                if not df_state.empty:
                    col1, _ = st.columns(2)
                    with col1:
                        fig_state = px.bar(
                        df_state,
                        x="Year",
                        y="total_registered_users",
                        color="total_appopens",
                        title=f"User App Open Count over Year in {selected_state}"
                    )
                    fig_state.update_yaxes(autorange=True)
                    st.plotly_chart(fig_state, use_container_width=True)

            # -----------------------------
            # District-Level Top 5 / Bottom 5
            # -----------------------------
            df_district = pd.read_sql(
                """
                SELECT
                    "Districts",
                    SUM("AppOpens") AS total_appopens,
                    SUM("RegisteredUser") AS total_registered_users
                FROM map_user
                WHERE "State" = %(state)s
                GROUP BY "Districts"
                ORDER BY total_appopens DESC;
                """,
                engine,
                params={"state": selected_state}
            )

            if not df_district.empty:
                df_district = df_district.sort_values(by="total_appopens", ascending=False)
                top5_districts = df_district.head(5)
                bottom5_districts = df_district.tail(5).sort_values(by="total_appopens", ascending=True)

                st.subheader(f"District-wise App Opens & Registered Users in {selected_state}")
                col2, col3 = st.columns(2)

                with col2:
                    fig_top_d = px.bar(
                        top5_districts,
                        x="Districts",
                        y=["total_appopens", "total_registered_users"],
                        barmode="group",
                        title="Top 5 Districts",
                        color_discrete_map={
                            "total_appopens": "grey",
                            "total_registered_users": "pink"
                        }
                    )
                    fig_top_d.update_yaxes(autorange=True)
                    st.plotly_chart(fig_top_d, use_container_width=True, key="top5_district")

                with col3:
                    fig_bottom_d = px.bar(
                        bottom5_districts,
                        x="Districts",
                        y=["total_appopens", "total_registered_users"],
                        barmode="group",
                        title="Bottom 5 Districts",
                        color_discrete_map={
                            "total_appopens": "blue",
                            "total_registered_users": "orange"
                        }
                    )
                    fig_bottom_d.update_yaxes(autorange=True)
                    st.plotly_chart(fig_bottom_d, use_container_width=True, key="bottom5_district")

        # -----------------------------
        # State-Level Top 5 / Bottom 5
        # -----------------------------
                df_state_summary = pd.read_sql(
                """
                SELECT
                "State",
                SUM("AppOpens") AS total_appopens,
                SUM("RegisteredUser") AS total_registered_users
                FROM map_user
                GROUP BY "State"
                    ORDER BY total_appopens DESC;
                """,
                engine
                    )

                if not df_state_summary.empty:
                    df_state_summary = df_state_summary.sort_values(by="total_appopens", ascending=False)
                    top5_State = df_state_summary.head(5)
                    bottom5_State = df_state_summary.tail(5).sort_values(by="total_appopens", ascending=True)

                    st.subheader("State-wise App Opens & Registered Users")
                    col4, col5 = st.columns(2)

                    with col4:
                        fig_top_s = px.bar(
                        top5_State,
                        x="State",
                        y=["total_appopens", "total_registered_users"],
                        barmode="group",
                        title="Top 5 State",
                        color_discrete_map={
                        "total_appopens": "green",
                        "total_registered_users": "blue"
                        }
                        )
                    fig_top_s.update_yaxes(autorange=True)
                    st.plotly_chart(fig_top_s, use_container_width=True, key="top5_state")

                    with col5:
                        fig_bottom_s = px.bar(
                        bottom5_State,
                        x="State",
                        y=["total_appopens", "total_registered_users"],
                        barmode="group",
                        title="Bottom 5 State",
                        color_discrete_map={
                        "total_appopens": "red",
                        "total_registered_users": "orange"
                        }
                        )
                        fig_bottom_s.update_yaxes(autorange=True)
                        st.plotly_chart(fig_bottom_s, use_container_width=True, key="bottom5_state")
            #-----------Map Transaction-------------
        if map_method == "Map Transaction":
            st.header(" Transaction Engagement & Market Expansion Strategy")

    # -----------------------------
    # State Dropdown
    # -----------------------------
            map_State_df = pd.read_sql(
            'SELECT DISTINCT "State" FROM map_transaction ORDER BY "State";',
            engine
            )
            map_State = sorted(map_State_df["State"].tolist())

            map_selected_state = st.selectbox(
            "Select State",
            options=[""] + map_State,
                index=0,
            help="Select a state to visualize transaction data"
            )

    # -----------------------------
    # Year Filter
    # -----------------------------
            map_Year_df = pd.read_sql(
                'SELECT DISTINCT "Year" FROM map_transaction ORDER BY "Year";',
            engine
            )
            map_Year = sorted(map_Year_df["Year"].tolist())

            map_selected_Year = st.selectbox(
            "Select Year(s)",
            options=[""] + map_Year,
            index=0
            )
           

    # -----------------------------
    # Selected State Data
    # -----------------------------
            if map_selected_state and map_selected_Year:
                map_state_transaction_df = pd.read_sql(
                """
                SELECT
                "State",
                "Districts",
                "Year",
                "Quarter",
                SUM("Transaction_count") AS total_transactions,
                SUM("Transaction_amount") AS total_amount
                FROM map_transaction
                WHERE "State" = %(state)s
              AND "Year" = (%(Year)s)
                GROUP BY "State","Districts","Year","Quarter"
                ORDER BY "Year","Quarter";
                """,engine,
                params={"state": map_selected_state, "Year": map_selected_Year}
                )

                if not map_state_transaction_df.empty:

            # -----------------------------
            # Quarterly Trend
            # -----------------------------
                    map_quarterly_trend = (
                    map_state_transaction_df
                    .groupby(["Year", "Quarter"])
                    .agg({"total_amount": "sum"})
                    .reset_index()
                    )

                    map_quarterly_trend["Year-Quarter"] = (
                    map_quarterly_trend["Year"].astype(str) + " Q" +
                        map_quarterly_trend["Quarter"].astype(str)
                    )

                    fig_map_trend = px.line(
                        map_quarterly_trend,
                    x="Year-Quarter",
                    y="total_amount",
                    markers=True,
                    title=f"Quarterly Transaction Trend - {map_selected_state}"
                     )
                    st.plotly_chart(fig_map_trend, use_container_width=True)

            # -----------------------------
                # District-Level Summary
            # -----------------------------
                    map_district_df = (
                        map_state_transaction_df
                     .groupby("Districts")
                    .agg({
                    "total_transactions": "sum",
                    "total_amount": "sum"
                    })
                    .reset_index()
                    )

                    map_district_df["avg_value"] = (
                    map_district_df["total_amount"] / map_district_df["total_transactions"]
                    )

                    map_district_df = map_district_df.sort_values(
                        by="total_amount",
                    ascending=False
                    )

                    map_top5_districts = map_district_df.head(5)
                    map_bottom5_districts = map_district_df.tail(5).sort_values(
                    by="total_amount",
                    ascending=True
                    )

                    st.subheader(f"District-wise Transactions in {map_selected_state}")
                    col1, col2 = st.columns(2)

            # Top 5 Districts
                    with col1:
                        fig_map_top_districts = px.bar(
                    map_top5_districts,
                    x="Districts",
                    y=["total_amount", "total_transactions"],
                    barmode="group",
                    title="Top 5 Districts by Revenue"
                    )
                    st.plotly_chart(fig_map_top_districts, use_container_width=True)

            # Bottom 5 Districts
                    with col2:
                        fig_map_bottom_districts = px.bar(
                        map_bottom5_districts,
                    x="Districts",
                    y=["total_amount", "total_transactions"],
                    barmode="group",
                    title="Bottom 5 Districts by Revenue"
                    )
                        st.plotly_chart(fig_map_bottom_districts, use_container_width=True)

    # -----------------------------
    # State-Level Top & Bottom 5
    # -----------------------------
            map_state_summary = pd.read_sql(
            """
            SELECT
            "State",
            SUM("Transaction_count") AS total_transactions,
            SUM("Transaction_amount") AS total_amount
            FROM map_transaction
            GROUP BY "State"
            ORDER BY total_amount DESC;
            """,
            engine
            )

            if not map_state_summary.empty:
                map_state_summary = map_state_summary.sort_values(
            by="total_amount",
            ascending=False
            )

            map_top5_State = map_state_summary.head(5)
            map_bottom5_State = map_state_summary.tail(5).sort_values(
            by="total_amount",
            ascending=True
            )

            st.subheader("State-wise Transaction Summary")
            col3, col4 = st.columns(2)

            with col3:
                fig_map_top_State = px.bar(
                    map_top5_State,
                x="State",
                y=["total_amount", "total_transactions"],
                barmode="group",
                title="Top 5 State"
                    )
                st.plotly_chart(fig_map_top_State, use_container_width=True)

            with col4:
                fig_map_bottom_State = px.bar(
                    map_bottom5_State,
                x="State",
                y=["total_amount", "total_transactions"],
                barmode="group",
                title="Bottom 5 State"
                )   
                st.plotly_chart(fig_map_bottom_State, use_container_width=True)


        
    # ---------------------- Tab 3: Top Data ---------------------- #
    with tab3:
        top_method = st.radio(
            "Select the Data",
            ["Top Insurance", "Top Transaction", "Top User"]
        )
        st.info(f"{top_method} functionality will go here.")
        




elif select == "India Map visualization":
     
    import json
    import requests
     
                            # ---------------------- Tab 4: India Choropleth ---------------------- #
    st.header("India State-wise Analysis")

    # Metric selection
    metric_options = [
        "Transaction Amount", 
        "Transaction Count", 
        "Insurance Amount", 
        "Insurance Count", 
        "App User Count"
    ]
    selected_metric = st.selectbox("Select Metric for Choropleth", metric_options)

    # Load India GeoJSON
    geojson_path = r"C:\Users\haris\phonepe project\phone_pe files\india_states.geojson.txt"

    with open(geojson_path, "r", encoding="utf-8") as f:
        geojson = json.load(f)   
 
    # Aggregate data based on selected metric
    if selected_metric in ["Transaction Amount", "Transaction Count"]:
        df_choro = pd.read_sql("""
            SELECT
                "State" as state,
                SUM("Transaction_amount") AS transaction_amount,
                SUM("Transaction_count") AS transaction_count
            FROM agg_transactions
            GROUP BY "State";
        """, engine)
        df_choro['value'] = df_choro['transaction_amount'] if selected_metric=="Transaction Amount" else df_choro['transaction_count']

    elif selected_metric in ["Insurance Amount", "Insurance Count"]:
        df_choro = pd.read_sql("""
            SELECT
                "State" as state,
                SUM("Transaction_amount") AS insurance_amount,
                SUM("Transaction_count") AS insurance_count
            FROM agg_insurance
            GROUP BY "State";
        """, engine)
        df_choro['value'] = df_choro['insurance_amount'] if selected_metric=="Insurance Amount" else df_choro['insurance_count']

    elif selected_metric == "App User Count":
        df_choro = pd.read_sql("""
            SELECT
                "State" as state,
                SUM("user_count") AS user_count
            FROM agg_users
            GROUP BY "State";
        """, engine)
        df_choro['value'] = df_choro['user_count']

    # Check if data exists
    if df_choro.empty:
        st.warning("No data available for the selected metric.")
    else:
        df_choro['state'] = df_choro['state'].str.strip().str.title()
        # Plot choropleth
        fig_choro = px.choropleth(
                df_choro,
            geojson=geojson,
            featureidkey='properties.ST_NM',
            locations='state',
            color='value',
            color_continuous_scale="blues",
            title=f"India Choropleth Map - {selected_metric}",
            hover_data={'state': True, 'value': True}
                )
        fig_choro.update_geos(fitbounds="locations", visible=False)
        st.plotly_chart(fig_choro, use_container_width=True)
