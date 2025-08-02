import pandas as pd
import plotly.express as px
import faicons as fa

from shiny import reactive, render
from shiny.express import ui, input, output
from shinywidgets import render_plotly
from faicons import icon_svg

# ---------------------------
# Data
# ---------------------------
tips = pd.read_csv(
    "https://raw.githubusercontent.com/mindy0cruz/cintel-06-custom/main/tips.csv"
)
bill_rng = (min(tips["total_bill"]), max(tips["total_bill"]))

# ---------------------------
# Reactive Filter
# ---------------------------
@reactive.calc
def filtered_data():
    bill = input.total_bill()
    gender = input.gender()
    times = input.selected_time()

    df = tips[
        (tips["total_bill"].between(bill[0], bill[1]))
        & (tips["sex"].isin(gender))
        & (tips["time"].isin(times))
    ].copy()
    df["tip_pct"] = df["tip"] / df["total_bill"]
    return df

# ---------------------------
# Icons
# ---------------------------
ICONS = {
    "users": fa.icon_svg("users", "solid"),
    "pen": fa.icon_svg("pen", "solid"),
    "receipt": fa.icon_svg("receipt", "solid"),
}

# ---------------------------
# UI
# ---------------------------
ui.page_opts(title="Mindy's Tip Dashboard", fillable=True)

with ui.sidebar():
    ui.input_slider(
        "total_bill",
        "Bill Total:",
        min=bill_rng[0],
        max=bill_rng[1],
        value=bill_rng,
        pre="$",
    )

    ui.input_checkbox_group(
        "gender",
        "Gender:",
        choices={
            "Male": ui.span("Male", style="color:red;"),
            "Female": ui.span("Female", style="color:blue;"),
        },
        selected=["Male", "Female"],
    )

    ui.input_checkbox_group(
        "selected_time",
        "Meal Time:",
        choices=["Lunch", "Dinner"],
        selected=["Lunch", "Dinner"],
        inline=True,
    )

# ---------------------------
# Value Boxes
# ---------------------------
with ui.layout_columns():
    @output
    @render.text
    def guests_count():
        return str(filtered_data().shape[0])

    ui.value_box(
        title="Guests",
        value=guests_count,
        showcase=ICONS["users"],
        theme="bg-gradient-green-orange",
    )

    @output
    @render.text
    def avg_tip_pct():
        df = filtered_data()
        return "N/A" if df.empty else f"{(df['tip_pct'].mean() * 100):.1f}%"

    ui.value_box(
        title="Average Tip",
        value=avg_tip_pct,
        showcase=ICONS["pen"],
        theme="bg-gradient-blue-yellow",
    )

    @output
    @render.text
    def avg_bill():
        df = filtered_data()
        return "N/A" if df.empty else f"${df['total_bill'].mean():.2f}"

    ui.value_box(
        title="Average Bill",
        value=avg_bill,
        showcase=ICONS["receipt"],
        theme="bg-gradient-purple-pink",
    )

# ---------------------------
# Charts & Table
# ---------------------------
with ui.layout_columns():
    with ui.card(full_screen=True):
        ui.card_header("Tips by Table")

        @output
        @render.data_frame
        def show_data():
            return filtered_data()

with ui.card(full_screen=True):
    ui.card_header("Tip by Gender")

    @output
    @render_plotly
    def plot_tips_by_gender():
        df = filtered_data()
        if df.empty:
            return px.pie(title="No Data")
        summary = df.groupby("sex")["tip"].mean().reset_index()
        return px.pie(
            summary,
            values="tip",
            names="sex",
            color="sex",
            title="Tip by Gender"
        )

with ui.card(full_screen=True):
    ui.card_header("Tips by Day")

    @output
    @render_plotly
    def day_plot():
        df = filtered_data()
        if df.empty:
            return px.bar(title="No data")
        summary = df.groupby("day")["tip"].sum().reset_index()
        return px.bar(
            summary,
            x="day",
            y="tip",
            color="day",
            title="Tips by Day",
            labels={"tip": "Total Tips ($)", "day": "Day"},
            category_orders={"day": ["Thur", "Fri", "Sat", "Sun"]},
        )
