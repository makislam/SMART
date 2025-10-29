"""
Interactive Robot Arm Control with Joint Angle Sliders
Uses Plotly Dash for real-time control of all 6 joint angles
"""

import numpy as np
from dash import Dash, dcc, html, Input, Output, State
import plotly.graph_objects as go
from visualization import PlotlyURDFVisualizer

# Initialize the visualizer
visualizer = PlotlyURDFVisualizer('URDF/mycobotpro320.urdf', show_inertia=False)

# Create Dash app
app = Dash(__name__)

# Color scheme
COLORS = {
    'primary': '#2C3E50',      # Dark blue-gray
    'secondary': '#3498DB',    # Bright blue
    'accent': '#E74C3C',       # Red
    'success': '#2ECC71',      # Green
    'background': '#ECF0F1',   # Light gray
    'card': '#FFFFFF',         # White
    'text': '#2C3E50',         # Dark text
    'text_light': '#7F8C8D',   # Light gray text
    'border': '#BDC3C7',       # Border gray
}

# Get joint limits for sliders
joint_limits = []
for joint in visualizer.joints:
    joint_limits.append({
        'min': joint['limits']['lower'],
        'max': joint['limits']['upper'],
        'name': joint['name']
    })

# Preset configurations
presets = {
    'Home': [0, 0, 0, 0, 0, 0],
    'Config 1': [0, -np.pi/2, -np.pi/3, -np.pi/4, -np.pi/2, 0],
    'Vertical': [0, -np.pi/2, 0, 0, 0, 0],
    'Reach Forward': [0, -np.pi/4, -np.pi/4, -np.pi/4, 0, 0],
}

# Slider styling
slider_style = {
    'marginBottom': '25px',
    'padding': '15px 20px',
    'backgroundColor': COLORS['card'],
    'borderRadius': '12px',
    'boxShadow': '0 2px 8px rgba(0,0,0,0.08)',
    'border': f'1px solid {COLORS["border"]}',
    'transition': 'all 0.3s ease'
}

button_base_style = {
    'margin': '6px',
    'padding': '12px 24px',
    'fontSize': '14px',
    'fontWeight': '600',
    'border': 'none',
    'borderRadius': '8px',
    'cursor': 'pointer',
    'transition': 'all 0.3s ease',
    'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
    'fontFamily': "'Segoe UI', 'Roboto', sans-serif"
}

preset_button_style = {
    **button_base_style,
    'backgroundColor': COLORS['secondary'],
    'color': 'white',
}

reset_button_style = {
    **button_base_style,
    'width': '100%',
    'padding': '14px',
    'fontSize': '16px',
    'backgroundColor': COLORS['accent'],
    'color': 'white',
    'marginTop': '20px'
}

# Create layout
app.layout = html.Div([
    # Header
    html.Div([
        html.H1("🤖 myCobot 320 Pi", 
                style={
                    'textAlign': 'center',
                    'color': COLORS['primary'],
                    'marginBottom': '5px',
                    'fontSize': '36px',
                    'fontWeight': '700',
                    'fontFamily': "'Segoe UI', 'Roboto', sans-serif"
                }),
        html.P("Interactive 6-Axis Robotic Arm Control", 
               style={
                   'textAlign': 'center',
                   'color': COLORS['text_light'],
                   'fontSize': '16px',
                   'marginBottom': '25px',
                   'fontFamily': "'Segoe UI', 'Roboto', sans-serif"
               })
    ], style={
        'backgroundColor': COLORS['card'],
        'padding': '25px',
        'boxShadow': '0 2px 10px rgba(0,0,0,0.1)',
        'marginBottom': '20px'
    }),
    
    html.Div([
        # Left panel - Controls
        html.Div([
            html.Div([
                html.H3("⚙️ Joint Control", 
                       style={
                           'marginBottom': '20px',
                           'color': COLORS['primary'],
                           'fontSize': '24px',
                           'fontWeight': '600',
                           'fontFamily': "'Segoe UI', 'Roboto', sans-serif"
                       }),
                
                # Preset buttons section
                html.Div([
                    html.H4("📋 Preset Configurations", 
                           style={
                               'marginBottom': '12px',
                               'color': COLORS['text'],
                               'fontSize': '16px',
                               'fontWeight': '600',
                               'fontFamily': "'Segoe UI', 'Roboto', sans-serif"
                           }),
                    html.Div([
                        html.Button(name, id=f'preset-{name}', style=preset_button_style)
                        for name in presets.keys()
                    ], style={'marginBottom': '25px', 'display': 'flex', 'flexWrap': 'wrap'}),
                ], style={
                    'padding': '20px',
                    'backgroundColor': COLORS['card'],
                    'borderRadius': '12px',
                    'marginBottom': '20px',
                    'boxShadow': '0 2px 8px rgba(0,0,0,0.08)',
                    'border': f'1px solid {COLORS["border"]}'
                }),
                
                # Individual joint sliders
                html.Div([
                    html.Div([
                        html.Div([
                            html.Label([
                                html.Span(f'C{i+1}', style={
                                    'backgroundColor': COLORS['secondary'],
                                    'color': 'white',
                                    'padding': '4px 10px',
                                    'borderRadius': '6px',
                                    'fontSize': '14px',
                                    'fontWeight': '700',
                                    'marginRight': '10px',
                                    'fontFamily': "'Segoe UI', 'Roboto', monospace"
                                }),
                                html.Span(f'{joint_limits[i]["name"]}', style={
                                    'color': COLORS['text'],
                                    'fontSize': '15px',
                                    'fontWeight': '500',
                                    'fontFamily': "'Segoe UI', 'Roboto', sans-serif"
                                })
                            ], style={'display': 'flex', 'alignItems': 'center', 'marginBottom': '10px'}),
                            dcc.Slider(
                                id=f'slider-{i}',
                                min=joint_limits[i]['min'],
                                max=joint_limits[i]['max'],
                                value=0,
                                marks={
                                    joint_limits[i]['min']: {
                                        'label': f'{np.degrees(joint_limits[i]["min"]):.0f}°',
                                        'style': {'color': COLORS['text_light'], 'fontSize': '11px', 'fontFamily': "'Segoe UI', 'Roboto', sans-serif"}
                                    },
                                    0: {
                                        'label': '0°',
                                        'style': {'color': COLORS['success'], 'fontSize': '12px', 'fontWeight': '600', 'fontFamily': "'Segoe UI', 'Roboto', sans-serif"}
                                    },
                                    joint_limits[i]['max']: {
                                        'label': f'{np.degrees(joint_limits[i]["max"]):.0f}°',
                                        'style': {'color': COLORS['text_light'], 'fontSize': '11px', 'fontFamily': "'Segoe UI', 'Roboto', sans-serif"}
                                    }
                                },
                                tooltip={"placement": "bottom", "always_visible": True},
                                updatemode='drag',
                                className='custom-slider'
                            ),
                            html.Div(id=f'output-{i}', 
                                   style={
                                       'marginTop': '8px',
                                       'fontSize': '13px',
                                       'color': COLORS['text_light'],
                                       'textAlign': 'center',
                                       'fontFamily': "'Segoe UI', 'Roboto', monospace"
                                   }),
                        ]),
                    ], style=slider_style)
                    for i in range(6)
                ]),
                
                # Reset button
                html.Button('🔄 Reset to Home', id='reset-btn', style=reset_button_style),
                
                # Current angles display
                html.Div([
                    html.H4("📊 Current Configuration", 
                           style={
                               'marginTop': '25px',
                               'marginBottom': '12px',
                               'color': COLORS['text'],
                               'fontSize': '16px',
                               'fontWeight': '600',
                               'fontFamily': "'Segoe UI', 'Roboto', sans-serif"
                           }),
                    html.Pre(id='angles-display', 
                            style={
                                'backgroundColor': COLORS['primary'],
                                'color': '#ECF0F1',
                                'padding': '15px',
                                'borderRadius': '8px',
                                'fontSize': '12px',
                                'fontFamily': "'Consolas', 'Monaco', 'Courier New', monospace",
                                'lineHeight': '1.6',
                                'overflowX': 'auto',
                                'boxShadow': '0 2px 8px rgba(0,0,0,0.15)'
                            })
                ], style={
                    'padding': '20px',
                    'backgroundColor': COLORS['card'],
                    'borderRadius': '12px',
                    'boxShadow': '0 2px 8px rgba(0,0,0,0.08)',
                    'border': f'1px solid {COLORS["border"]}'
                })
                
            ], style={'padding': '25px'})
            
        ], style={
            'width': '35%',
            'display': 'inline-block',
            'verticalAlign': 'top',
            'boxSizing': 'border-box',
            'backgroundColor': COLORS['background'],
            'height': '100vh',
            'overflowY': 'auto'
        }),
        
        # Right panel - 3D Visualization
        html.Div([
            dcc.Graph(
                id='robot-graph',
                style={'height': '100vh'},
                config={
                    'displayModeBar': True,
                    'displaylogo': False,
                    'modeBarButtonsToRemove': ['select2d', 'lasso2d']
                }
            )
        ], style={
            'width': '65%',
            'display': 'inline-block',
            'verticalAlign': 'top',
            'backgroundColor': COLORS['card']
        }),
        
    ], style={'display': 'flex'}),
    
], style={
    'fontFamily': "'Segoe UI', 'Roboto', 'Helvetica Neue', Arial, sans-serif",
    'margin': '0',
    'padding': '0',
    'backgroundColor': COLORS['background']
})

# Add custom CSS via external stylesheet
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>myCobot 320 Pi Control</title>
        {%favicon%}
        {%css%}
        <style>
            .custom-slider .rc-slider-track {
                background-color: ''' + COLORS['secondary'] + ''' !important;
                height: 6px !important;
            }
            .custom-slider .rc-slider-rail {
                height: 6px !important;
                background-color: ''' + COLORS['border'] + ''' !important;
            }
            .custom-slider .rc-slider-handle {
                width: 20px !important;
                height: 20px !important;
                margin-top: -7px !important;
                border: 3px solid ''' + COLORS['secondary'] + ''' !important;
                background-color: white !important;
                box-shadow: 0 2px 8px rgba(0,0,0,0.15) !important;
            }
            .custom-slider .rc-slider-handle:hover {
                border-color: ''' + COLORS['accent'] + ''' !important;
            }
            .custom-slider .rc-slider-handle:active {
                box-shadow: 0 0 8px ''' + COLORS['secondary'] + ''' !important;
            }
            button:hover {
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(0,0,0,0.15) !important;
            }
            button:active {
                transform: translateY(0px);
            }
            *::-webkit-scrollbar {
                width: 10px;
            }
            *::-webkit-scrollbar-track {
                background: ''' + COLORS['background'] + ''';
            }
            *::-webkit-scrollbar-thumb {
                background: ''' + COLORS['border'] + ''';
                border-radius: 5px;
            }
            *::-webkit-scrollbar-thumb:hover {
                background: ''' + COLORS['text_light'] + ''';
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# Callback to update visualization
@app.callback(
    [Output('robot-graph', 'figure')] + 
    [Output(f'slider-{i}', 'value') for i in range(6)] +
    [Output(f'output-{i}', 'children') for i in range(6)] +
    [Output('angles-display', 'children')],
    [Input(f'slider-{i}', 'value') for i in range(6)] +
    [Input('reset-btn', 'n_clicks')] +
    [Input(f'preset-{name}', 'n_clicks') for name in presets.keys()],
    prevent_initial_call=False
)
def update_robot(*args):
    # Extract current slider values (first 6 arguments)
    current_angles = list(args[:6])
    
    # Check which button was clicked
    from dash import callback_context
    if callback_context.triggered:
        button_id = callback_context.triggered[0]['prop_id'].split('.')[0]
        
        if button_id == 'reset-btn':
            current_angles = [0, 0, 0, 0, 0, 0]
        elif button_id.startswith('preset-'):
            preset_name = button_id.replace('preset-', '')
            if preset_name in presets:
                current_angles = presets[preset_name]
    
    # Create the robot traces
    traces = visualizer.create_robot_traces(current_angles)
    
    # Create figure
    fig = go.Figure(data=traces)
    
    fig.update_layout(
        title={
            'text': "myCobot 320 Pi - Real-time Visualization",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18, 'color': COLORS['primary'], 'family': "'Segoe UI', 'Roboto', sans-serif"}
        },
        scene=dict(
            xaxis=dict(
                range=[-0.5, 0.5],
                title='X (m)',
                backgroundcolor=COLORS['background'],
                gridcolor=COLORS['border'],
                showbackground=True
            ),
            yaxis=dict(
                range=[-0.5, 0.5],
                title='Y (m)',
                backgroundcolor=COLORS['background'],
                gridcolor=COLORS['border'],
                showbackground=True
            ),
            zaxis=dict(
                range=[0, 0.7],
                title='Z (m)',
                backgroundcolor=COLORS['background'],
                gridcolor=COLORS['border'],
                showbackground=True
            ),
            aspectmode='manual',
            aspectratio=dict(x=1, y=1, z=1.2),
            camera=dict(
                eye=dict(x=1.5, y=1.5, z=1.2),
                center=dict(x=0, y=0, z=0.3)
            )
        ),
        showlegend=False,
        margin=dict(l=0, r=0, b=0, t=50),
        uirevision='constant',  # Maintain camera position during updates
        paper_bgcolor=COLORS['card'],
        plot_bgcolor=COLORS['card']
    )
    
    # Create output labels for each slider with improved formatting
    slider_outputs = [
        f"📍 {angle:.4f} rad  •  {np.degrees(angle):.2f}°"
        for angle in current_angles
    ]
    
    # Create angles display text with improved formatting
    angles_text = "╔═══════════════════════════════════════════════╗\n"
    angles_text += "║         JOINT ANGLES CONFIGURATION           ║\n"
    angles_text += "╠═══════════════════════════════════════════════╣\n"
    for i, angle in enumerate(current_angles):
        angles_text += f"║  C{i+1} (J{i+1})  │  {angle:>7.4f} rad  │  {np.degrees(angle):>7.2f}°  ║\n"
    angles_text += "╠═══════════════════════════════════════════════╣\n"
    angles_text += f"║  Array: [{', '.join([f'{a:>6.3f}' for a in current_angles])}]  ║\n"
    angles_text += "╚═══════════════════════════════════════════════╝"
    
    # Return: figure, slider values (6), slider outputs (6), angles display
    return [fig] + current_angles + slider_outputs + [angles_text]

if __name__ == '__main__':
    print("\n" + "="*60)
    print("Starting Interactive Robot Arm Control Server")
    print("="*60)
    print("\nFeatures:")
    print("  • Real-time joint angle control with 6 sliders")
    print("  • Preset configurations")
    print("  • Live angle display in radians and degrees")
    print("\nThe server will open in your browser automatically...")
    print("Press Ctrl+C to stop the server")
    print("="*60 + "\n")
    
    app.run(debug=True, port=8050)
