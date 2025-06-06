from shiny import ui, render, App
import plotly.graph_objects as go
from shinywidgets import output_widget, render_widget, render_plotly

enso_data = {'months': [{'month': 0, 'probabilities': [{'elnino': 0, 'lanina': 66, 'neutral': 34, 'season': 'JFM'}, {'elnino': 0, 'lanina': 50, 'neutral': 50, 'season': 'FMA'}, {'elnino': 0, 'lanina': 35, 'neutral': 65, 'season': 'MAM'}, {'elnino': 2, 'lanina': 29, 'neutral': 69, 'season': 'AMJ'}, {'elnino': 7, 'lanina': 31, 'neutral': 62, 'season': 'MJJ'}, {'elnino': 11, 'lanina': 35, 'neutral': 54, 'season': 'JJA'}, {'elnino': 13, 'lanina': 38, 'neutral': 49, 'season': 'JAS'}, {'elnino': 13, 'lanina': 44, 'neutral': 43, 'season': 'ASO'}, {'elnino': 14, 'lanina': 48, 'neutral': 38, 'season': 'SON'}]}], 'year': 2025}


# Add MathJax script with additional configuration
mathjax_script = """
<script src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.5/MathJax.js?config=TeX-AMS-MML_HTMLorMML"></script>
<script type="text/x-mathjax-config">
  MathJax.Hub.Config({
    tex2jax: {
      inlineMath: [['$','$'], ['\\(','\\)']],
      displayMath: [['$$','$$'], ['\\[','\\]']],
      processEscapes: true
    },
    "HTML-CSS": { 
      scale: 100,
      linebreaks: { automatic: true }
    },
    SVG: { 
      linebreaks: { automatic: true } 
    }
  });
</script>
<style>
.math-content {
    padding: 20px;
    line-height: 1.6;
}
.math-content h2 {
    color: #2c3e50;
    margin-top: 20px;
    margin-bottom: 10px;
}
.math-content p {
    margin-bottom: 15px;
}
table {
    width: 100%;
    border-collapse: collapse;
    margin: 15px 0;
}
th, td {
    border: 1px solid #ddd;
    padding: 8px;
    text-align: left;
}
th {
    background-color: #f5f5f5;
}
</style>
"""

app_ui = ui.page_auto(
    ui.tags.head(ui.HTML(mathjax_script)),
    ui.h1("Effect of ENSO on Crop Yield"),
    ui.input_select(
        "variable",  
        "Select a crop below:", 
        {"rice": "Rice", 
         "soybean": "Soya Bean", 
         "wheat": "Wheat",
         "maize":"Maize"}
    ),

    ui.input_selectize(
        "oscillation",  
        "Select type of oscillation below:",  
        {"lanina":"La Nina", "elnino":"El Nino", "normal": "Neutral"}, 
    ),

    ui.card(
        ui.card_header("ENSO Probability Forecast 2025 from International Research Institute for Climate and Society"),
        output_widget("enso_plot")
    ),


    ui.card(
        ui.card_header("Crop Yield Prediction 2025"),
        ui.output_ui("seasonalmap", height="100%")
    ),

    ui.card(
        ui.card_header("Model Details"),
        ui.div(
            {"class": "math-content"},
            ui.HTML("""
            <h2>Crop Model Description</h2>
            <p>
                The model predicts the regional probability of decrease in crop-yield
                using GDHY data from 1982 to 2016 with 0.5° resolution as the target variable, with ERA5-Land 
                monthly measurements of temperature, precipitation, and solar radiation from 1979 to 2016 with 0.1° resolution as inputs.
            </p>

            <h4>Input Processing</h4>
            <p>
                The continuous climate variables are transformed into three discrete categories:
                -1 below normal, 0 near normal, and 
                1 above normal. This is done by assigning terciles based on the 
                distribution of each variable. Mathematically, the transformation is defined as:
            </p>
            <p style="text-align: center;">
                $$ 
                d(x) = \\begin{cases} 
                    -1, & x < q_{33} \\\\ 
                     0, & q_{33} \\le x < q_{66} \\\\ 
                     1, & x \\ge q_{66} 
                \\end{cases} 
                $$
            </p>
            <p>
                where <em>q<sub>33</sub></em> and <em>q<sub>66</sub></em> are the 33rd and 66th percentiles, respectively.
            </p>

            <h4>Model Input Construction</h4>
            <p>
                The processed input consists of two parts:
            </p>
            <ul>
                <li>
                    <strong>Time Series Input</strong>: a tensor with the shape <strong>(24, 3, 4, 4)</strong>, where:
                    <ul>
                        <li><strong>24</strong>: 24 consecutive months,</li>
                        <li><strong>3</strong>: the three climate variables, and</li>
                        <li><strong>4 × 4</strong>: a spatial grid representing a 0.4°×0.4° region centered on the crop location.</li>
                    </ul>
                </li>
                <li>
                    <strong>Static Features</strong>: a vector containing the following elements: longitude, latitude, year, and the FAO-reported country-level crop yield from the last three years.
                </li>
            </ul>

            <h3>Model Architecture</h3>
            <p>
                The overall architecture is a multi-branch neural network that integrates spatial–temporal dynamics 
                with static features. The main components are:
            </p>
            <ul>
                <li>
                    <strong>CNN Branch for each time step:</strong>
                    <p>
                        Each 4×4 image with 3 channels is processed by a convolutional layer followed by batch 
                        normalization and a ReLU activation. The spatial feature is then flattened and mapped to a 
                        lower-dimensional representation:
                    </p>
                    <p style="text-align: center;">
                        $$ 
                        x_t = \\text{ReLU}(\\text{BN}(\\text{Conv}(I_t))) \\quad  \\quad
                        f_t = \\text{ReLU}(W_{\\text{cnn}} \\cdot \\text{flatten}(x_t) + b_{\\text{cnn}})
                        $$
                    </p>
                </li>
                <li>
                    <strong>LSTM Branch:</strong>
                    <p>
                        The sequence of CNN features is fed into an LSTM to capture temporal dynamics:
                    </p>
                    <p style="text-align: center;">
                        $$ 
                        h_t = \\text{LSTM}(f_t, h_{t-1})
                        $$
                    </p>
                </li>
                <li>
                    <strong>Self-Attention Mechanism:</strong>
                    <p>
                        To aggregate the LSTM outputs over time, a self-attention layer is applied:
                    </p>
                    <p style="text-align: center;">
                        $$ 
                        \\alpha_t = \\frac{\\exp(\\text{tanh}(W_a h_t))}{\\sum_{k=1}^{T} \\exp(\\text{tanh}(W_a h_k))} 
                        \\quad \\text{and} \\quad
                        \\bar{h} = \\sum_{t=1}^{T} \\alpha_t h_t
                        $$
                    </p>
                </li>
                <li>
                    <strong>Static Branch:</strong>
                    <p>
                        A separate fully-connected layer processes a 6-dimensional vector of static features:
                    </p>
                    <p style="text-align: center;">
                        $$ 
                        s' = \\text{ReLU}(W_s s + b_s)
                        $$
                    </p>
                </li>
                <li>
                    <strong>Late Fusion and Classification:</strong>
                    <p>
                        The aggregated temporal feature $\\bar{h}$ and the static feature representation $s'$
                        are concatenated:
                    </p>
                    <p style="text-align: center;">
                        $$ 
                        z = [\\bar{h}; s']
                        $$
                    </p>
                    <p>
                        This combined vector is passed through additional fully-connected layers to produce the final logit:
                    </p>
                    <p style="text-align: center;">
                        $$ 
                        z' = \\text{ReLU}(W_f z + b_f) \\quad \\text{and} \\quad \\text{logit} = W_o z' + b_o
                        $$
                    </p>
                </li>
            </ul>

            <h4>Model Performance</h4>
            <p>
                The following table summarizes the model performance during the training period (1982–2013) and 
                validation period (2014–2015):
            </p>
            <table border="1" cellpadding="5" cellspacing="0">
                <tr>
                    <th>Crop</th>
                    <th>Train AUC 1982–2013</th>
                    <th>Validation AUC 2014–2015</th>
                </tr>
                <tr>
                    <td>Rice</td>
                    <td>0.77</td>
                    <td>0.70</td>
                </tr>
                <tr>
                    <td>Wheat</td>
                    <td>0.85</td>
                    <td>0.71</td>
                </tr>
                <tr>
                    <td>Maize</td>
                    <td>0.74</td>
                    <td>0.62</td>
                </tr>
                <tr>
                    <td>Soy Bean</td>
                    <td>0.79</td>
                    <td>0.68</td>
                </tr>
            </table>
          
                    </li>
            </ul>
                    
            <h4>2025 Prediction</h4>
          <p>
              For the 2025 prediction, the model input is derived from the results of a teleconnection model. We run three scenarios:
              <strong>El Niño</strong>, <strong>La Niña</strong>, and <strong>Neutral</strong>. For each scenario, the teleconnection model calculates 
              the probabilities that each climate variable is below normal, near normal, or above normal. These probability estimates are then used 
              as the 2025 climate time series.
          </p>
            
            """)
        )
    )

)

def server(input, output, session):

    @render_plotly
    def enso_plot():
        # Extract data from the ENSO probability data
        probabilities = enso_data['months'][0]['probabilities']
        seasons = [p['season'] for p in probabilities]
        elnino_probs = [p['elnino'] for p in probabilities]
        lanina_probs = [p['lanina'] for p in probabilities]
        neutral_probs = [p['neutral'] for p in probabilities]

        # Create figure
        fig = go.Figure()

        # Add traces for each ENSO condition
        fig.add_trace(go.Scatter(x=seasons, y=elnino_probs, mode='lines+markers',
                               name="El Niño", line=dict(color='red')))
        
        fig.add_trace(go.Scatter(x=seasons, y=lanina_probs, mode='lines+markers',
                               name="La Niña", line=dict(color='blue')))
        
        fig.add_trace(go.Scatter(x=seasons, y=neutral_probs, mode='lines+markers',
                               name="Neutral", line=dict(color='black')))

        # Update layout
        fig.update_layout(
            xaxis_title="Season",
            yaxis_title="Probability (%)",
            template="simple_white",
            showlegend=True,
            height=300
        )

        return fig
    
    @render.ui
    #@render.image(delete_file=True)
    def seasonalmap():
        return ui.tags.img(src=f"https://raw.githubusercontent.com/czhixi/fall_2024_trp_proj_zc/main/scripts/outcome_app_renames/{input.variable()}_{input.oscillation()}.png", width = "100%")

app=App(app_ui, server)