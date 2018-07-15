import plotly.graph_objs as go
import json

class Plot_Inv():


    def rander_Bar_graph(self,data,title="",y_name="",x_name="",color='#1f77b4'):
        layout = go.Layout(
            title=title,
            xaxis=dict(
                domain=[0.1, 0.9],
                title=x_name
            ),
            yaxis=dict(
                title= y_name,
                titlefont=dict(
                    color=color
                ),
                tickfont=dict(
                    color=color
                )
            ),
            margin=dict(
                l=70,
                r=70,
                b=150,
                t=70,
                pad=4
            )


        )
        y_axies = data['y']
        x_axies = data['x']

        plot_date = go.Bar(
            x= x_axies,
            y= y_axies,
            name=y_name

        )

        return [plot_date], layout

    def rander_Bar_graph_multiY(self,data = {},title="",x_name="",color='#1f77b4'):
        layout = go.Layout(
            title=title,
            xaxis=dict(
                domain=[0.1, 0.9],
                title=x_name
            )
        )

        plot_date = []
        for sen_id in data.keys():
            inv = data[sen_id]
            x = []
            y = []
            for k in inv:
                x.append(k['x'])
                y.append(k['y'])

            p_date = go.Bar(
                    x= x,
                    y= y,
                    name=sen_id)
            plot_date.append(p_date)

        return plot_date, layout


    def rander_Scatter_graph(self,data,title="",y_name="",x_name="",color='#1f77b4'):
        layout = go.Layout(
            title=title,
            xaxis=dict(
                domain=[0.1, 0.9],
                title=x_name
            ),
            yaxis=dict(
                title= y_name,
                titlefont=dict(
                    color=color
                ),
                tickfont=dict(
                    color=color
                ),
                rangemode="nonnegative",
                margin=dict(
                    l=70,
                    r=70,
                    b=150,
                    t=70,
                    pad=4
                )
            )
        )
        y_axies = data['y']
        x_axies = data['x']

        plot_date = go.Bar(
            x= x_axies,
            y= y_axies,
            name=y_name

        )

        return [plot_date], layout


    def rander_pie_graph(self,data,lables):
        plot_date = go.Pie(labels=lables, values=data)
        return plot_date


