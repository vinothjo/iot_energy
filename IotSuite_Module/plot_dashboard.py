import plotly.graph_objs as go
import json


class Plot_Dashboard():
    
    tesi_line = {
        type: 'line',
        'data': {
            'labels': ["January", "February", "March", "April", "May", "June", "July"],
            'datasets': [{
                'label': "My First dataset",
                'data': [2,4,6,2,1,5,9],

            }, {
                'label': "My Second dataset",
                'data': [8,9,3,2,1,5,1],
            }]
        },
        'options': {
            'responsive': 'true',
            'tooltips': {
                'mode': 'label'
            },
            'hover': {
                'mode': 'dataset'
            },
            'scales': {
                'xAxes': [{
                    'display': 'true',
                    'scaleLabel': {
                        'show': 'true',
                        'labelString': 'Month'
                    }
                }],
                'yAxes': [{
                    'display': 'true',
                    'scaleLabel': {
                        'show': 'true',
                        'labelString': 'Value'
                    },
                    'ticks': {
                        'suggestedMin': 0,
                        'suggestedMax': 100,
                    }
                }]
            }
        }
    }
    layout = go.Layout(
        #title='Energy Graph',
        xaxis=dict(
            title='',
            domain=[0.1, 0.9],
            side='bottom',
            position=-1,
            titlefont = dict(
                family='Courier New, monospace',
                size=18,
                color='#fc021b'
            )
        ),
        yaxis=dict(
            title='E Generation (kWh)',
            titlefont=dict(
                color='#1f77b4'
            ),
            tickfont=dict(
                color='#1f77b4'
            )
        ),
        yaxis2=dict(
            title='IRR (W/m2)',
            titlefont=dict(
                color='#be41f4'
            ),
            tickfont=dict(
                color='#be41f4'
            ),
            anchor='free',
            overlaying='y',
            side='left',
            position=0.03
        ),
        yaxis3=dict(
            title='Expected (kWh)',
            titlefont=dict(
                color='#41f449'
            ),
            tickfont=dict(
                color='#41f449'
            ),
            anchor='free',
            overlaying='y',
            side='right',
            position=0.97
        ),
        legend=dict(x=0, y=1.3)

    )

    def rander_graph(self,data):
        data = json.loads(data)
        y_axies = data['E_Generation']['Graphdata']['y']
        x_axies = data['E_Generation']['Graphdata']['x']

        irr_y_axies = data['Irr']['Graphdata']['y']
        irr_x_axies = data['Irr']['Graphdata']['x']

        exp_y_axies = data['Expected']['Graphdata']['y']
        exp_x_axies = data['Expected']['Graphdata']['x']


        egen = go.Bar(
            x= x_axies,
            y= y_axies,
            name='E_Generation data (kWh)',

        )
        irr = go.Scatter(
            x=irr_x_axies,
            y=irr_y_axies,
            name='IRR data (W/m2)',
            yaxis='y2',
            marker=dict(
                size=10,
                color='#be41f4',
                line=dict(
                    width=2,
                    color='green'
                )
            ),
        )
        exp = go.Scatter(
            x=exp_x_axies,
            y=exp_y_axies,
            name='Expected data (kWh)',
            yaxis='y3',
            mode='markers',
            marker=dict(
                size=10,
                color='#41f449',
                line=dict(
                    width=2,
                    color='green'
                )
            ),
        )

        return [egen,irr,exp], self.layout






    def rander_simplegraph(self, x_axies=[], y_axies_01=[], y_axies_02=[], x_lable="", y_label_01=None,y_label_02=None, title="",type_01="Bar",type_02="Bar"):
        layout = go.Layout(
            title=title,
            margin=go.Margin(
                l=1,
                r=1,
                b=100,
                t=100,
                pad=1
            ),
            xaxis=dict(
                title=x_lable,
                domain=[0.1, 0.9],
                side='bottom',
                position=-1,
                titlefont=dict(
                    family='Courier New, monospace',
                    size=18,
                    color='#fc021b'
                )
            ),
            yaxis=dict(
                title=y_label_01,
                titlefont=dict(
                    color='#1f77b4'
                ),
                tickfont=dict(
                    color='#1f77b4'
                )
            ),
            legend=dict(x=0, y=-0.7,orientation='h'),


        )
        if y_label_02:
            layout.__setitem__('yaxis2',dict(
                title=y_label_02,
                titlefont=dict(
                    color='#be41f4'
                ),
                tickfont=dict(
                    color='#be41f4'
                ),
                anchor='free',
                overlaying='y',
                side='left',
                position=0.03
            ))

        print('type_01',type_01)
        if type_01 == "Bar":
            y_01 = go.Bar(
                x= x_axies,
                y= y_axies_01,
                name=y_label_01,

            )
        else:
            y_01 = go.Scatter(
                x=x_axies,
                y=y_axies_01,
                name=y_label_01,
                line=dict(shape='spline',smoothing= 1.3)

            )
        if type_02 == "Bar":
            y_02 = go.Bar(
                yaxis='y2',
                x=x_axies,
                y=y_axies_02,
                name=y_label_02,

            )
        else:
            y_02 = go.Scatter(
                yaxis='y2',
                x=x_axies,
                y=y_axies_02,
                name=y_label_02,
                line=dict(shape='spline', smoothing=1.3)

            )

        if y_label_02:
            return [y_01,y_02], layout
        else:
            return [y_01], layout

        





