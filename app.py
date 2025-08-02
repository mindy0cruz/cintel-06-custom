from shiny import App, reactive, render, ui
from shinywidgets import render_plotly
import pandas as pd
import plotly.express as px
from faicons import icon_svg

# Load data
df = pd.read_csv("tips.csv")
bill_rng = (min(df["total_bill"]), max(df["total_bill"]))

# Icons
ICONS = {
    "users": icon_svg("users", "solid"),
    "pen": icon_svg("pen", "solid"),
    "receipt": icon_svg("receipt", "solid"),
}

# UI
app_ui = ui.page_fluid(
    ui.page_opts(title="Mindy's Tips Dashboard", fillable=True),
    ui.sidebar(
        ui.input_slider(
            "total_bill",
            "Bill Total:",
            min=bill_rng[0],
            max=bill_rng[1],
            value=bill_rng,
            pre="$",
        ),
        ui.input_checkbox_group(
            "gender",
            "Server Gender:",
            choices={
                "Male": ui.span("Male", style="color:blue;"),
                "Female": ui.span("Female", style="color:pink;"),
            },
            selected=["Male", "Female"],
        ),
        ui.input_checkbox_group(
            "selected_time",
            "Service Time:",
            choices=["Lunch", "Dinner"],
            selected=["Lunch", "Dinner"],
            inline=True,
        ),
    ),
    ui.layout_columns(
        ui.value_box(
            title="Guests",
            value=ui.output_text("guests_count"),
            showcase=ICONS["users"],
            theme="bg-gradient-blue-yellow",
        ),
        ui.value_box(
            title="Average Tip",
            value=ui.output_text("avg_tip_pct"),
            showcase=ICONS["pen"],
            theme="bg-gradient-blue-yellow",
        ),
        ui.value_box(
            title="Average Bill",
            value=ui.output_text("avg_bill"),
            showcase=ICONS["receipt"],
            theme="bg-gradient-blue-yellow",
        ),
    ),
    ui.layout_columns(
        ui.card(
            ui.card_header("Tips by Table"),
            ui.output_data_frame("show_data"),
            full_screen=True,
        ),
        ui.card(
            ui.card_header("Tips by Gender"),
            ui.output_plot("plot_tips_by_gender"),
            full_screen=True,
        ),
        ui.card(
            ui.card_header("Tips by Day"),
            ui.output_plot("day_plot"),
            full_screen=True,
        ),
    ),
)

# Server logic
def server(input, output, session):
    @reactive.calc
    def filtered_data():
        bill = input.total_bill()
        gender = input.gender()
        times = input.selected_time()

        tips = df[
            df["total_bill"].between(bill[0], bill[1])
            & df["sex"].isin(gender)
            & df["time"].isin(times)
        ].copy()
        tips["tip_pct"] = tips["tip"] / tips["total_bill"]
        return tips

    @output
    @render.text
    def guests_count():
        return str(filtered_data().shape[0])

    @output
    @render.text
    def avg_tip_pct():
        data = filtered_data()
        return "N/A" if data.empty else f"{(data['tip_pct'].mean() * 100):.1f}%"

    @output
    @render.text
    def avg_bill():
        data = filtered_data()
        return "N/A" if data.empty else f"${data['total_bill'].mean():.2f}"

    @output
    @render.data_frame
    def show_data():
        return render.DataGrid(filtered_data())

    @output
    @render_plotly
    def plot_tips_by_gender():
        df = filtered_data()
        if df.empty:
            return px.bar(title="No Data")
        summary = df.groupby("sex")["tip"].mean().reset_index()
        return px.bar(summary, x="sex", y="tip", color="sex", title="Tips by Gender")

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


app = App(app_ui, server)

